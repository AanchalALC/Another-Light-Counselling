"""
main/management/commands/gbp_discover.py

Run once after OAuth works. Prints the three values you paste into .env:

    GBP_ACCOUNT_ID
    GBP_LOCATION_ID
    GOOGLE_PLACE_ID

    docker compose exec backend python manage.py gbp_discover
"""

from django.core.management.base import BaseCommand

from main.services.google_reviews import (
    GoogleReviewsError, get_access_token, list_accounts, list_locations,
)


class Command(BaseCommand):
    help = "Print the Business Profile account, location and place IDs."

    def handle(self, *args, **options):
        try:
            token = get_access_token()
        except GoogleReviewsError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        self.stdout.write(self.style.SUCCESS("Access token OK.\n"))

        try:
            accounts = list_accounts(token)
        except GoogleReviewsError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        if not accounts:
            self.stdout.write(self.style.WARNING(
                "No accounts returned. Either the signed-in Google account does not "
                "manage the ALC Business Profile, or access is not approved yet."))
            return

        for acc in accounts:
            name = acc.get("name", "")
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING(
                "ACCOUNT: %s" % acc.get("accountName", "(unnamed)")))
            self.stdout.write("  GBP_ACCOUNT_ID=%s" % name.split("/")[-1])

            try:
                locations = list_locations(name, token)
            except GoogleReviewsError as exc:
                self.stderr.write(self.style.ERROR("  locations failed: %s" % exc))
                continue

            if not locations:
                self.stdout.write("  (no locations under this account)")
                continue

            for loc in locations:
                meta = loc.get("metadata") or {}
                addr = loc.get("storefrontAddress") or {}
                self.stdout.write("")
                self.stdout.write("  LOCATION: %s" % loc.get("title", "(untitled)"))
                self.stdout.write("    GBP_LOCATION_ID=%s" % loc.get("name", "").split("/")[-1])
                self.stdout.write("    GOOGLE_PLACE_ID=%s" % meta.get("placeId", "(none)"))
                self.stdout.write("    address: %s %s" % (
                    ", ".join(addr.get("addressLines") or []), addr.get("locality", "")))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            "Paste those three into .env, restart the container, then run:\n"
            "  python manage.py sync_google_reviews --dry-run"))
