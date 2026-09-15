"""
Pull the latest Instagram posts into the database and cache their images
locally.

Run from cron every 15 minutes:
    python manage.py sync_instagram

Why images are downloaded rather than hot-linked: Instagram's CDN URLs in
media_url / thumbnail_url are signed and expire after a few days.
Hot-linking means the homepage silently fills with broken images later.
Storing them under MEDIA_ROOT/instagram/ makes the widget stable and means
the page never depends on Instagram being reachable.

Posts deleted on Instagram are removed here too, which keeps the site in
line with Meta's platform terms.
"""

import time
from datetime import datetime, timedelta

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import OperationalError
from django.utils import timezone

from main.instagram_api import (
    InstagramError, media, poster_url, profile, refresh_token,
)
from main.models import InstagramAccount, InstagramPost

# Refresh the 60-day token once it is inside this window of expiring.
REFRESH_WHEN_DAYS_LEFT = 20

# How many posts to keep cached. The homepage shows fewer; the extra rows
# give headroom to hide a post in admin without leaving a gap.
KEEP_POSTS = 24

IMAGE_TIMEOUT = 45

PLACEHOLDER_TOKENS = (
    '',
    'PASTE_REAL_TOKEN_FROM_NAVEEN_HERE',
    'DEMO_TOKEN_NOT_REAL',
)


class Command(BaseCommand):
    help = 'Sync the latest Instagram posts for the ALC account into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=KEEP_POSTS,
            help='How many recent posts to fetch (default {}).'.format(KEEP_POSTS),
        )
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='Refresh the access token regardless of how long it has left.',
        )

    # ---------------------------------------------------------------- helpers

    def _parse_timestamp(self, raw):
        """Instagram sends '2026-01-15T10:30:00+0000'."""
        if not raw:
            return None
        try:
            return datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S%z')
        except (ValueError, TypeError):
            return None

    def _maybe_refresh_token(self, account, force=False):
        if not account.token_expires_at and not force:
            # Unknown expiry (token pasted in by hand). Refresh so we start
            # tracking it properly.
            force = True

        if not force:
            days_left = (account.token_expires_at - timezone.now()).days
            if days_left > REFRESH_WHEN_DAYS_LEFT:
                self.stdout.write('Token has {} days left. No refresh needed.'.format(days_left))
                return

        try:
            result = refresh_token(account.access_token)
        except InstagramError as exc:
            # Not fatal for this run: the existing token may still be valid
            # for weeks. Log and carry on.
            self.stderr.write(self.style.WARNING('Token refresh failed: {}'.format(exc)))
            return

        account.access_token = result.get('access_token', account.access_token)
        expires_in = result.get('expires_in')
        if expires_in:
            account.token_expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        self._retry(lambda: account.save(update_fields=['access_token', 'token_expires_at']))
        self.stdout.write(self.style.SUCCESS(
            'Token refreshed. New expiry: {}'.format(account.token_expires_at)
        ))

    def _retry(self, fn, attempts=4, delay=1.5):
        """
        Run fn() (a zero-arg callable doing a DB write), retrying on
        OperationalError.

        SQLite occasionally throws a transient "disk I/O error" on this
        deployment right after a file write to the same bind-mounted
        volume — not real corruption (PRAGMA integrity_check passes, and
        a retry always succeeds), but frequent enough on a 15-minute cron
        job that a single flaky write shouldn't abort the whole sync and
        leave demo rows stranded alongside real ones.
        """
        last_exc = None
        for attempt in range(1, attempts + 1):
            try:
                return fn()
            except OperationalError as exc:
                last_exc = exc
                if attempt < attempts:
                    time.sleep(delay * attempt)
        raise last_exc

    def _download_thumbnail(self, post, url):
        """Fetch the image and attach it to the post. Returns True on success."""
        if not url:
            return False
        try:
            response = requests.get(url, timeout=IMAGE_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.stderr.write(self.style.WARNING(
                'Could not download image for {}: {}'.format(post.media_id, exc)
            ))
            return False

        filename = 'ig_{}.jpg'.format(post.media_id)
        self._retry(lambda: post.thumbnail.save(filename, ContentFile(response.content), save=True))
        return True

    def _download_avatar(self, account, url):
        """Fetch the profile picture and attach it to the account. Returns True on success."""
        try:
            response = requests.get(url, timeout=IMAGE_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.stderr.write(self.style.WARNING(
                'Could not download avatar: {}'.format(exc)
            ))
            return False

        account.avatar.save(
            'avatar_{}.jpg'.format(account.ig_user_id or account.username),
            ContentFile(response.content),
            save=False,
        )
        return True

    # ------------------------------------------------------------------ main

    def handle(self, *args, **options):
        account = InstagramAccount.objects.filter(is_active=True).first()

        if not account:
            self.stderr.write(self.style.ERROR(
                'No active Instagram account configured. '
                'Add one in Django admin under Main > Instagram account.'
            ))
            return

        token = (account.access_token or '').strip()
        if token in PLACEHOLDER_TOKENS:
            self._fail(
                account,
                'Access token is still the placeholder. Paste the real token '
                'from Naveen into Django admin > Instagram account > Access token.'
            )
            return

        self._maybe_refresh_token(account, force=options['force_refresh'])

        # Confirm the token still maps to the expected account.
        try:
            me = profile(account.access_token)
        except InstagramError as exc:
            self._fail(account, str(exc))
            return

        account.ig_user_id = me.get('id', account.ig_user_id)
        if me.get('username'):
            account.username = me['username']
        account.display_name = me.get('name', '')
        account.biography = me.get('biography', '')
        account.followers_count = me.get('followers_count')
        account.follows_count = me.get('follows_count')
        update_fields = [
            'ig_user_id', 'username', 'display_name', 'biography',
            'followers_count', 'follows_count',
        ]

        avatar_url = me.get('profile_picture_url', '')
        if avatar_url and avatar_url != account.remote_avatar_url:
            account.remote_avatar_url = avatar_url
            if self._download_avatar(account, avatar_url):
                update_fields.append('avatar')
            update_fields.append('remote_avatar_url')

        self._retry(lambda: account.save(update_fields=update_fields))

        try:
            items = media(account.access_token, limit=options['limit'])
        except InstagramError as exc:
            self._fail(account, str(exc))
            return

        seen_ids = []
        created = 0
        updated = 0

        for item in items:
            media_id = item.get('id')
            if not media_id:
                continue
            seen_ids.append(media_id)

            post, was_created = self._retry(
                lambda: InstagramPost.objects.get_or_create(media_id=media_id)
            )

            post.media_type = item.get('media_type') or 'IMAGE'
            post.media_product_type = item.get('media_product_type') or ''
            post.permalink = item.get('permalink') or ''
            post.caption = item.get('caption') or ''
            post.posted_at = self._parse_timestamp(item.get('timestamp'))
            post.is_demo = False

            remote = poster_url(item)
            post.remote_thumbnail_url = remote
            self._retry(post.save)

            # Only download if there is no local copy yet. Instagram image
            # bytes never change for an existing post.
            if not post.thumbnail:
                self._download_thumbnail(post, remote)

            if was_created:
                created += 1
            else:
                updated += 1

        # Drop anything that has disappeared from the account. Demo rows are
        # spared so a half-set-up site does not go blank mid-review.
        removed = 0
        stale = InstagramPost.objects.filter(is_demo=False).exclude(media_id__in=seen_ids)
        for post in stale:
            if post.thumbnail:
                post.thumbnail.delete(save=False)
            self._retry(post.delete)
            removed += 1

        # Once real posts land, retire the demo rows automatically.
        demo_removed = 0
        if created or updated:
            for post in InstagramPost.objects.filter(is_demo=True):
                if post.thumbnail:
                    post.thumbnail.delete(save=False)
                self._retry(post.delete)
                demo_removed += 1

        account.last_synced_at = timezone.now()
        account.last_sync_status = 'OK - {} new, {} updated, {} removed'.format(
            created, updated, removed
        )
        account.save(update_fields=['last_synced_at', 'last_sync_status'])

        message = 'Instagram sync complete for @{}: {} new, {} updated, {} removed.'.format(
            account.username, created, updated, removed
        )
        if demo_removed:
            message += ' Cleared {} demo placeholder(s).'.format(demo_removed)
        self.stdout.write(self.style.SUCCESS(message))

    def _fail(self, account, message):
        account.last_sync_status = 'FAILED - {}'.format(message)[:255]
        account.save(update_fields=['last_sync_status'])
        self.stderr.write(self.style.ERROR(message))
