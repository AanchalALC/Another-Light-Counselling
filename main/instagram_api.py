"""
Thin client for the Instagram API with Instagram Login (graph.instagram.com).

Three calls power the homepage feed:
  - profile()        : confirm the token maps to the right IG account
  - media()          : pull the latest posts / reels
  - refresh_token()  : extend a long-lived token for another 60 days

No app secret is needed for any of these, so nothing sensitive lives in
.env or in the repo. The token is stored in the database
(main.InstagramAccount) and refreshed in place by sync_instagram.
"""

import requests

GRAPH_BASE = 'https://graph.instagram.com'
TIMEOUT = 20

# media_url is the full image, or the video file for reels.
# thumbnail_url is the poster frame and is only returned for VIDEO items.
MEDIA_FIELDS = ','.join([
    'id',
    'caption',
    'media_type',
    'media_product_type',
    'media_url',
    'thumbnail_url',
    'permalink',
    'timestamp',
])


class InstagramError(Exception):
    """Raised when Instagram returns an error or an unusable payload."""
    pass


def _get(path, params):
    url = '{}{}'.format(GRAPH_BASE, path)
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise InstagramError('Network error calling {}: {}'.format(path, exc))

    try:
        payload = response.json()
    except ValueError:
        raise InstagramError(
            'Non-JSON response from {} (HTTP {})'.format(path, response.status_code)
        )

    if 'error' in payload:
        err = payload['error']
        raise InstagramError('Instagram API error on {}: {} (type={}, code={})'.format(
            path,
            err.get('message', 'unknown'),
            err.get('type', '?'),
            err.get('code', '?'),
        ))

    if response.status_code >= 400:
        raise InstagramError('HTTP {} from {}'.format(response.status_code, path))

    return payload


PROFILE_FIELDS = ','.join([
    'id',
    'username',
    'name',
    'biography',
    'followers_count',
    'follows_count',
    'profile_picture_url',
])


def profile(access_token):
    """
    Return account info for the token's account: id, username, name,
    biography, followers_count, follows_count, profile_picture_url.

    biography/followers_count/follows_count/profile_picture_url need the
    account to be a Business or Creator account. ALC's is (MEDIA_CREATOR),
    confirmed live against the real token.
    """
    return _get('/me', {
        'fields': PROFILE_FIELDS,
        'access_token': access_token,
    })


def media(access_token, limit=24):
    """Return a list of the most recent media objects, newest first."""
    payload = _get('/me/media', {
        'fields': MEDIA_FIELDS,
        'limit': limit,
        'access_token': access_token,
    })
    data = payload.get('data')
    if data is None:
        raise InstagramError('No "data" key in /me/media response.')
    return data


def refresh_token(access_token):
    """
    Extend a long-lived token by another 60 days.

    The token must be at least 24 hours old and not yet expired. Returns
    {'access_token': ..., 'token_type': ..., 'expires_in': <seconds>}.
    """
    return _get('/refresh_access_token', {
        'grant_type': 'ig_refresh_token',
        'access_token': access_token,
    })


def poster_url(item):
    """
    Pick the right still image for a media item.

    Reels and videos return the playable file in media_url, so the poster
    frame in thumbnail_url is what we display. Images and carousels only
    have media_url.
    """
    if item.get('media_type') == 'VIDEO':
        return item.get('thumbnail_url') or item.get('media_url') or ''
    return item.get('media_url') or ''
