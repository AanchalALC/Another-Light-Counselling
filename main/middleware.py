"""
Canonical-host redirect for another-light.com.

Deliberately does NOT use Django's PREPEND_WWW. PREPEND_WWW derives its redirect
target from request.scheme and request.get_host(), which behind a reverse proxy
are the internal scheme and host — it 301s visitors to a dead address and fires
on every non-www host including health checks. That took the site down once.

This middleware instead hardcodes the public scheme and host, and is allow-list
based: only the exact hosts in settings.REDIRECT_HOSTS are ever redirected.
Everything else — www, localhost, container IPs, platform health checks —
passes through untouched.

Controlled by the CANONICAL_REDIRECT env var. When off, MiddlewareNotUsed removes
it from the chain entirely, so it costs nothing and can be killed via an env
change without a code deploy.
"""

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponsePermanentRedirect


class CanonicalHostRedirectMiddleware:
    def __init__(self, get_response):
        if not getattr(settings, "CANONICAL_REDIRECT_ENABLED", False):
            raise MiddlewareNotUsed
        self.get_response = get_response
        self.canonical_host = getattr(
            settings, "CANONICAL_HOST", "www.another-light.com"
        ).lower()
        self.redirect_hosts = {
            h.lower()
            for h in getattr(settings, "REDIRECT_HOSTS", ["another-light.com"])
        }

    def __call__(self, request):
        try:
            host = request.get_host().split(":")[0].lower()
        except Exception:
            return self.get_response(request)

        if host in self.redirect_hosts:
            return HttpResponsePermanentRedirect(
                "https://{}{}".format(self.canonical_host, request.get_full_path())
            )

        return self.get_response(request)
