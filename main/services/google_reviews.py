"""
main/services/google_reviews.py

Fetches every Google review for the Another Light Counselling listing.

HOW MANY REVIEWS DOES THIS RETURN?
----------------------------------
All of them. Google sends reviews 50 at a time and includes a nextPageToken
whenever there are more. This code keeps asking until the token stops coming.
For ALC's 121 reviews that is 3 requests, about two seconds.

The 5-review cap people run into belongs to a DIFFERENT Google product (the
Places API). This module does not use it.

WHAT YOU NEED IN .env
---------------------
    GOOGLE_OAUTH_CLIENT_ID
    GOOGLE_OAUTH_CLIENT_SECRET
    GOOGLE_OAUTH_REFRESH_TOKEN
    GBP_ACCOUNT_ID
    GBP_LOCATION_ID
    GOOGLE_PLACE_ID          (only used to build the "read on Google" links)

Run `python manage.py gbp_discover` to print the last three.
"""

import datetime
import logging

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
ACCOUNTS_URL = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
LOCATIONS_URL = "https://mybusinessbusinessinformation.googleapis.com/v1/{account}/locations"
REVIEWS_URL = "https://mybusiness.googleapis.com/v4/accounts/{account_id}/locations/{location_id}/reviews"

STAR_WORDS = {
    "STAR_RATING_UNSPECIFIED": 0,
    "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5,
}

TIMEOUT = 30
PAGE_SIZE = 50      # Google's documented maximum for v4 reviews.list
MAX_PAGES = 200     # 10,000 reviews. Runaway guard only.

# Both naming schemes are in circulation for these credentials, so accept
# either and stop anyone losing an hour to a variable name.
_ALIASES = {
    "GOOGLE_OAUTH_CLIENT_ID": ("GBP_CLIENT_ID",),
    "GOOGLE_OAUTH_CLIENT_SECRET": ("GBP_CLIENT_SECRET",),
    "GOOGLE_OAUTH_REFRESH_TOKEN": ("GBP_REFRESH_TOKEN",),
}


class GoogleReviewsError(Exception):
    pass


# ---------------------------------------------------------------- helpers
def _cfg(name, default=""):
    value = getattr(settings, name, "") or ""
    if value:
        return value
    for alias in _ALIASES.get(name, ()):
        value = getattr(settings, alias, "") or ""
        if value:
            return value
    return default


def parse_rfc3339(value):
    """Python 3.7 can't parse Google's trailing 'Z' or 9-digit fractions."""
    if not value:
        return None
    text = str(value).strip().replace("Z", "")
    if "." in text:
        head, tail = text.split(".", 1)
        tail = "".join(c for c in tail if c.isdigit())[:6]
        text = head + ("." + tail if tail else "")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return timezone.make_aware(
                datetime.datetime.strptime(text, fmt), timezone.utc)
        except ValueError:
            continue
    logger.warning("google_reviews: unparseable timestamp %r", value)
    return None


def place_reviews_url(place_id=None):
    """Public 'all reviews' page. Every card links here."""
    place_id = place_id or _cfg("GOOGLE_PLACE_ID")
    if not place_id:
        return "https://www.google.com/maps"
    return "https://search.google.com/local/reviews?placeid=" + str(place_id)


def place_write_review_url(place_id=None):
    place_id = place_id or _cfg("GOOGLE_PLACE_ID")
    if not place_id:
        return "https://www.google.com/maps"
    return "https://search.google.com/local/writereview?placeid=" + str(place_id)


# ---------------------------------------------------------------- OAuth
def get_access_token():
    """
    Swap the long-lived refresh token for a short-lived access token.
    The refresh token is minted once via the OAuth Playground and lives in .env.
    """
    client_id = _cfg("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = _cfg("GOOGLE_OAUTH_CLIENT_SECRET")
    refresh_token = _cfg("GOOGLE_OAUTH_REFRESH_TOKEN")

    missing = [n for n, v in (
        ("GOOGLE_OAUTH_CLIENT_ID", client_id),
        ("GOOGLE_OAUTH_CLIENT_SECRET", client_secret),
        ("GOOGLE_OAUTH_REFRESH_TOKEN", refresh_token),
    ) if not v]
    if missing:
        raise GoogleReviewsError("Missing settings: " + ", ".join(missing))

    resp = requests.post(TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }, timeout=TIMEOUT)

    if resp.status_code != 200:
        detail = resp.text[:400]
        hint = ""
        if "invalid_grant" in detail:
            hint = ("\nHINT: 'invalid_grant' almost always means the OAuth consent "
                    "screen was left in Testing mode, which expires refresh tokens "
                    "after 7 days. Publish the app, then mint a fresh token in the "
                    "OAuth Playground.")
        raise GoogleReviewsError(
            "Token refresh failed (%s): %s%s" % (resp.status_code, detail, hint))

    token = resp.json().get("access_token")
    if not token:
        raise GoogleReviewsError("Token refresh returned no access_token")
    return token


def _auth_get(url, token, params=None):
    resp = requests.get(
        url,
        headers={"Authorization": "Bearer " + token},
        params=params or {},
        timeout=TIMEOUT,
    )
    if resp.status_code == 429:
        raise GoogleReviewsError(
            "HTTP 429 from %s\n"
            "This is NOT a rate limit. A brand new project sits at ZERO quota until "
            "Google approves the Business Profile API access request, and rejects "
            "every call with a 429. Check: Cloud Console > IAM & Admin > Quotas > "
            "search 'Business Profile'. 0 QPM means still waiting; 300 QPM means "
            "approved." % url)
    if resp.status_code == 403:
        raise GoogleReviewsError(
            "HTTP 403 PERMISSION_DENIED from %s\n"
            "Either the signed-in account is not an Owner/Manager of the listing, or "
            "the three Business Profile APIs are not enabled, or (on Google Workspace) "
            "Business Profile is switched off for the organisation.\nDetail: %s"
            % (url, resp.text[:400]))
    if resp.status_code != 200:
        raise GoogleReviewsError(
            "HTTP %s from %s: %s" % (resp.status_code, url, resp.text[:500]))
    return resp.json()


# ---------------------------------------------------------------- discovery
def list_accounts(token=None):
    token = token or get_access_token()
    out, page_token = [], None
    while True:
        params = {"pageSize": 20}
        if page_token:
            params["pageToken"] = page_token
        data = _auth_get(ACCOUNTS_URL, token, params)
        out.extend(data.get("accounts", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return out


def list_locations(account_name, token=None):
    token = token or get_access_token()
    url = LOCATIONS_URL.format(account=account_name)
    out, page_token = [], None
    while True:
        params = {"readMask": "name,title,storefrontAddress,metadata,websiteUri",
                  "pageSize": 100}
        if page_token:
            params["pageToken"] = page_token
        data = _auth_get(url, token, params)
        out.extend(data.get("locations", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return out


# ---------------------------------------------------------------- reviews
def fetch_all_reviews(account_id=None, location_id=None, progress=None):
    """
    EVERY review for the listing. Returns (reviews, stats).

    `progress` is an optional callable(str) so the management command can print
    each page as it lands - that is how you prove nothing was truncated.
    """
    account_id = account_id or _cfg("GBP_ACCOUNT_ID")
    location_id = location_id or _cfg("GBP_LOCATION_ID")

    if not account_id or not location_id:
        raise GoogleReviewsError(
            "GBP_ACCOUNT_ID and GBP_LOCATION_ID must be set in .env. "
            "Run: python manage.py gbp_discover")

    token = get_access_token()
    url = REVIEWS_URL.format(account_id=account_id, location_id=location_id)
    listing_url = place_reviews_url()

    reviews = []
    stats = {"average_rating": None, "total_ratings": 0, "reviews_url": listing_url}
    page_token, page_no = None, 0

    while True:
        page_no += 1
        if page_no > MAX_PAGES:
            logger.warning("google_reviews: hit MAX_PAGES guard")
            break

        params = {"pageSize": PAGE_SIZE, "orderBy": "updateTime desc"}
        if page_token:
            params["pageToken"] = page_token
        data = _auth_get(url, token, params)

        # Identical on every page; last one wins.
        if data.get("averageRating") is not None:
            stats["average_rating"] = data["averageRating"]
        if data.get("totalReviewCount") is not None:
            stats["total_ratings"] = data["totalReviewCount"]

        batch = data.get("reviews") or []

        for item in batch:
            reviewer = item.get("reviewer") or {}
            reply = item.get("reviewReply") or {}
            reviews.append({
                "external_id": item.get("reviewId") or item.get("name", ""),
                "author_name": reviewer.get("displayName", "") or "",
                "author_photo_url": reviewer.get("profilePhotoUrl", "") or "",
                "rating": STAR_WORDS.get(item.get("starRating", ""), 0),
                "comment": (item.get("comment") or "").strip(),
                # v4 has no per-review permalink, so cards link to the
                # listing's public reviews page.
                "review_url": listing_url,
                "created_at_google": parse_rfc3339(item.get("createTime")),
                "updated_at_google": parse_rfc3339(item.get("updateTime")),
                "reply_comment": (reply.get("comment") or "").strip(),
                "reply_time": parse_rfc3339(reply.get("updateTime")),
            })

        if progress:
            progress("  page %d: +%-3d  running total %d of %s"
                     % (page_no, len(batch), len(reviews),
                        stats["total_ratings"] or "?"))

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return reviews, stats
