"""
Create placeholder Instagram posts so the homepage widget can be built,
styled and reviewed before the real access token arrives.

    python manage.py seed_instagram_demo

Generates eight square images in the ALC brand palette using Pillow (already
a dependency, since the project uses ImageField), writes them to
MEDIA_ROOT/instagram/, and creates matching InstagramPost rows. It also
creates the InstagramAccount row with a clearly-marked placeholder token so
there is one obvious field to replace later.

Every row is flagged is_demo=True. The real sync_instagram command deletes
demo rows automatically the first time it pulls live posts, so there is no
cleanup step to forget.

To remove them by hand:
    python manage.py seed_instagram_demo --clear
"""

import io
import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import InstagramAccount, InstagramPost

PLACEHOLDER_TOKEN = 'PASTE_REAL_TOKEN_FROM_NAVEEN_HERE'

# ALC brand palette: Tangerine, Butter, Blush, Sea, Matcha. Each entry is a
# flat fill colour plus the ring colour drawn on top. Light fills use a
# translucent charcoal ring so the rings stay visible; darker fills use a
# translucent white ring.
PALETTE = [
    ('#F08C21', '#FFFFFF'),
    ('#6698CC', '#FFFFFF'),
    ('#E36888', '#FFFFFF'),
    ('#B4B534', '#FFFFFF'),
    ('#F2D88F', '#2B2B2B'),
    ('#6698CC', '#FFFFFF'),
    ('#F08C21', '#FFFFFF'),
    ('#E36888', '#FFFFFF'),
]

# Realistic-length captions so the hover overlay and truncation can be judged
# properly. Deliberately varied: long, short, hashtag-heavy, and empty.
DEMO_POSTS = [
    ('IMAGE', 'FEED',
     'Rest is not a reward you earn after burnout. It is part of the work. '
     'Small pauses through the day count more than one long collapse on Sunday. '
     '#mentalhealth #therapy #selfcare'),
    ('VIDEO', 'REELS',
     'Three grounding techniques you can use anywhere, in under sixty seconds. '
     'Save this one for the days that feel too loud. #anxiety #grounding'),
    ('CAROUSEL_ALBUM', 'FEED',
     'What does a first therapy session actually look like? Swipe through for '
     'what to expect, what we will ask, and what you never have to explain.'),
    ('IMAGE', 'FEED',
     'Boundaries are not walls. They are doors with you holding the handle.'),
    ('VIDEO', 'REELS',
     'Aanchal on why "just think positive" is some of the least helpful advice '
     'you can give someone in distress. #trauma #mentalhealthawareness'),
    ('IMAGE', 'FEED',
     'Pride is every month here. Affirmative, informed counselling for LGBTQIA+ '
     'clients across Andheri and Bandra. #lgbtqia #affirmativetherapy'),
    ('CAROUSEL_ALBUM', 'FEED',
     'Five signs your body is carrying stress your mind has not admitted to yet.'),
    ('IMAGE', 'FEED', ''),
]


class Command(BaseCommand):
    help = 'Create placeholder Instagram posts for design and QA work.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all demo posts instead of creating them.',
        )

    # ---------------------------------------------------------------- helpers

    def _make_image(self, index, bg_hex, ring_hex):
        """Build an 800x800 placeholder tile. Returns raw JPEG bytes."""
        try:
            from PIL import Image, ImageColor, ImageDraw
        except ImportError:
            raise RuntimeError(
                'Pillow is required for the demo seeder. It should already be '
                'installed because the project uses ImageField.'
            )

        size = 800
        base = Image.new('RGB', (size, size), bg_hex)

        # Faint concentric rings on a translucent overlay, composited on top,
        # so they blend into the fill instead of sitting on it as flat,
        # opaque outlines.
        overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        rng = random.Random(index)
        centre = size // 2
        ring_rgb = ImageColor.getrgb(ring_hex)

        for step in range(5, 0, -1):
            radius = int(size * (0.08 + step * 0.055))
            offset = rng.randint(-40, 40)
            alpha = 40 + step * 16
            draw.ellipse(
                [
                    centre - radius + offset,
                    centre - radius - offset,
                    centre + radius + offset,
                    centre + radius - offset,
                ],
                outline=ring_rgb + (alpha,),
                width=5,
            )

        # A small solid dot low-left gives the eye a fixed reference point for
        # checking crop and alignment across the grid.
        dot = 40
        draw.ellipse(
            [72, size - 72 - dot, 72 + dot, size - 72],
            fill=ring_rgb + (150,),
        )

        image = Image.alpha_composite(base.convert('RGBA'), overlay).convert('RGB')

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=88)
        return buffer.getvalue()

    # ------------------------------------------------------------------ main

    def handle(self, *args, **options):
        if options['clear']:
            count = 0
            for post in InstagramPost.objects.filter(is_demo=True):
                if post.thumbnail:
                    post.thumbnail.delete(save=False)
                post.delete()
                count += 1
            self.stdout.write(self.style.SUCCESS(
                'Removed {} demo post(s).'.format(count)
            ))
            return

        # Make sure there is an account row, with an obvious placeholder token.
        account, created_account = InstagramAccount.objects.get_or_create(
            defaults={
                'username': 'another_light_counselling',
                'access_token': PLACEHOLDER_TOKEN,
                'is_active': True,
                'last_sync_status': 'Demo mode - no real token yet.',
            }
        )
        if created_account:
            self.stdout.write(
                'Created Instagram account row with placeholder token.'
            )

        now = timezone.now()
        created = 0

        for index, (media_type, product_type, caption) in enumerate(DEMO_POSTS):
            media_id = 'demo-{:02d}'.format(index + 1)
            post, was_created = InstagramPost.objects.get_or_create(
                media_id=media_id,
                defaults={'is_demo': True},
            )

            post.is_demo = True
            post.media_type = media_type
            post.media_product_type = product_type
            post.caption = caption
            post.permalink = 'https://www.instagram.com/another_light_counselling/'
            post.posted_at = now - timedelta(days=index * 3, hours=index * 2)
            post.remote_thumbnail_url = ''
            post.save()

            if not post.thumbnail:
                bg_hex, ring_hex = PALETTE[index % len(PALETTE)]
                image_bytes = self._make_image(index, bg_hex, ring_hex)
                post.thumbnail.save(
                    '{}.jpg'.format(media_id),
                    ContentFile(image_bytes),
                    save=True,
                )

            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            '{} demo Instagram post(s) ready ({} newly created). '
            'Reload the homepage to see the widget.'.format(
                len(DEMO_POSTS), created
            )
        ))
        self.stdout.write(
            'Token placeholder lives in Django admin > Main > Instagram account '
            '> Access token.'
        )
