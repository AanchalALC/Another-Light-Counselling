"""
main/management/commands/import_reviews_csv.py

OPTIONAL BRIDGE. Only needed if the page must launch before Google approves
API access. Lets someone type existing reviews into a CSV so the page is not
empty on day one.

Rows land with source='manual' and look identical to synced reviews. When
approval arrives:

    python manage.py sync_google_reviews --retire-manual

...which unpublishes every seeded row in one go. No manual cleanup.

CSV COLUMNS (header row required, order irrelevant)
    author_name   required
    rating        required, 1-5
    comment       the review text
    date          YYYY-MM-DD, approximate is fine (drives sort order)
    reply         Aanchal's public reply (optional)

    python manage.py import_reviews_csv reviews_seed.csv --dry-run
    python manage.py import_reviews_csv reviews_seed.csv

Re-running is safe: the key is a hash of author + comment, so edits update
rows rather than duplicating them.

Fill it in by hand from the live listing. Do not use a scraper - automated
extraction of Google Maps review content breaches Google's Terms of Service,
and that is not a risk worth taking on a counselling practice's site.
"""

import csv
import hashlib
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_date

from main.models import GoogleReview
from main.services import google_reviews as gr


def _dedupe_key(author, comment):
    raw = ("%s|%s" % (author.strip().lower(), comment.strip())).encode("utf-8")
    return "manual-" + hashlib.sha256(raw).hexdigest()[:32]


class Command(BaseCommand):
    help = "Seed reviews from a CSV while API approval is pending."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        path = options["csv_path"]
        if not os.path.exists(path):
            raise CommandError("File not found: %s" % path)

        default_url = gr.place_reviews_url()
        created = updated = skipped = 0

        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = set((h or "").strip() for h in (reader.fieldnames or []))
            if not {"author_name", "rating"}.issubset(headers):
                raise CommandError(
                    "CSV needs at least author_name and rating columns. Found: %s"
                    % ", ".join(sorted(headers)))

            for line_no, row in enumerate(reader, start=2):
                row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
                author = row.get("author_name", "")
                comment = row.get("comment", "")

                try:
                    rating = int(float(row.get("rating") or 0))
                except ValueError:
                    rating = 0

                if not author or not (1 <= rating <= 5):
                    self.stderr.write(
                        "  line %d skipped: needs author_name and a rating of 1-5" % line_no)
                    skipped += 1
                    continue

                created_at = None
                if row.get("date"):
                    parsed = parse_date(row["date"])
                    if parsed:
                        created_at = timezone.make_aware(
                            timezone.datetime.combine(
                                parsed, timezone.datetime.min.time()), timezone.utc)
                    else:
                        self.stderr.write("  line %d: bad date %r, expected YYYY-MM-DD"
                                          % (line_no, row["date"]))

                if options["dry_run"]:
                    self.stdout.write("  [%d*] %-20s %s" % (
                        rating, author[:20], comment[:60].replace("\n", " ")))
                    continue

                _, was_created = GoogleReview.objects.update_or_create(
                    source=GoogleReview.SOURCE_MANUAL,
                    external_id=_dedupe_key(author, comment),
                    defaults={
                        "author_name": author[:255],
                        "rating": rating,
                        "comment": comment,
                        "review_url": default_url,
                        "created_at_google": created_at,
                        "updated_at_google": created_at,
                        "reply_comment": row.get("reply", ""),
                    },
                )
                created += 1 if was_created else 0
                updated += 0 if was_created else 1

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(
                "Dry run: nothing written. %d row(s) would be skipped." % skipped))
            return

        self.stdout.write(self.style.SUCCESS(
            "Seeded %d new, updated %d, skipped %d." % (created, updated, skipped)))
        self.stdout.write("Temporary. Once API access is approved:\n"
                          "  python manage.py sync_google_reviews --retire-manual")
