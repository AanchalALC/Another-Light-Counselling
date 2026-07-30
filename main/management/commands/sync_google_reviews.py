"""
main/management/commands/sync_google_reviews.py

Pulls EVERY Google review for the ALC listing and saves them into the database.

Safe to run as often as you like: reviews are keyed on Google's own reviewId,
so re-running updates rows instead of duplicating them.

    python manage.py sync_google_reviews --dry-run   # look, don't touch
    python manage.py sync_google_reviews             # the real thing
    python manage.py sync_google_reviews --prune     # also delete reviews Google dropped
    python manage.py sync_google_reviews --retire-manual   # after a CSV seed

Cron on the VPS, daily 4am IST:
0 4 * * * cd ~/sites/another-light.com/django && /usr/bin/docker compose exec -T backend python manage.py sync_google_reviews >> /var/log/alc-reviews.log 2>&1
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import GoogleReview, GoogleReviewStats
from main.services import google_reviews as gr


class Command(BaseCommand):
    help = "Fetch every Google review for the ALC listing and store it."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--prune", action="store_true",
                            help="Delete stored reviews Google no longer returns.")
        parser.add_argument("--retire-manual", action="store_true",
                            help="Unpublish CSV-seeded rows once real reviews land.")

    def handle(self, *args, **options):
        self.stdout.write("Fetching all reviews from Google Business Profile...")

        try:
            reviews, stats = gr.fetch_all_reviews(progress=self.stdout.write)
        except gr.GoogleReviewsError as exc:
            self._record_failure(str(exc))
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        reported = int(stats.get("total_ratings") or 0)
        self.stdout.write("")
        self.stdout.write("Google reports %s total ratings; %d review objects returned."
                          % (reported or "?", len(reviews)))

        if reported and len(reviews) < reported:
            self.stdout.write(self.style.WARNING(
                "Gap of %d. This is normal - Google counts star-only ratings with no "
                "written text in the total, and does not always return them as review "
                "objects. Nothing is being truncated by pagination: the fetch ran until "
                "Google stopped sending a nextPageToken." % (reported - len(reviews))))

        if options["dry_run"]:
            self.stdout.write("")
            for r in reviews[:10]:
                self.stdout.write("  [%s*] %-22s %s" % (
                    r["rating"],
                    (r["author_name"] or "(anonymous)")[:22],
                    (r["comment"] or "(rating only)")[:60].replace("\n", " ")))
            if len(reviews) > 10:
                self.stdout.write("  ... and %d more" % (len(reviews) - 10))
            self.stdout.write(self.style.WARNING("\nDry run: nothing written."))
            return

        created = updated = 0
        seen_ids = []

        for r in reviews:
            ext_id = r.get("external_id") or ""
            if not ext_id:
                continue
            seen_ids.append(ext_id)

            _, was_created = GoogleReview.objects.update_or_create(
                source=GoogleReview.SOURCE_GBP,
                external_id=ext_id,
                defaults={
                    "author_name": r["author_name"][:255],
                    "author_photo_url": r["author_photo_url"][:1000],
                    "rating": r["rating"] or 0,
                    "comment": r["comment"],
                    "review_url": r["review_url"][:1000],
                    "created_at_google": r["created_at_google"],
                    "updated_at_google": r["updated_at_google"],
                    "reply_comment": r["reply_comment"],
                    "reply_time": r["reply_time"],
                },
            )
            created += 1 if was_created else 0
            updated += 0 if was_created else 1

        deleted = 0
        if options["prune"] and seen_ids:
            qs = GoogleReview.objects.filter(
                source=GoogleReview.SOURCE_GBP).exclude(external_id__in=seen_ids)
            deleted = qs.count()
            qs.delete()

        retired = 0
        if options["retire_manual"] and (created or updated):
            retired = GoogleReview.objects.filter(
                source=GoogleReview.SOURCE_MANUAL, is_published=True
            ).update(is_published=False)

        stats_obj, _ = GoogleReviewStats.objects.get_or_create(pk=1)
        if stats.get("average_rating") is not None:
            stats_obj.average_rating = round(float(stats["average_rating"]), 2)
        stats_obj.total_ratings = reported
        stats_obj.reviews_url = stats.get("reviews_url") or ""
        stats_obj.write_review_url = gr.place_write_review_url()
        stats_obj.last_synced = timezone.now()
        stats_obj.last_status = ("OK - %d fetched, %d new, %d updated, %d pruned"
                                 % (len(reviews), created, updated, deleted))
        stats_obj.save()

        self.stdout.write(self.style.SUCCESS(
            "\nDone. %d new, %d updated, %d pruned, %d seeded rows retired.\n"
            "Live on the site: %d review(s), average %s."
            % (created, updated, deleted, retired,
               GoogleReview.objects.filter(is_published=True).count(),
               stats_obj.average_rating)))

    def _record_failure(self, message):
        stats_obj, _ = GoogleReviewStats.objects.get_or_create(pk=1)
        stats_obj.last_status = ("FAILED: %s" % message)[:500]
        stats_obj.last_synced = timezone.now()
        stats_obj.save()
