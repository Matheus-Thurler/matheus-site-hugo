from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

from .models import Redirect


class RedirectMiddleware:
    """Apply DB redirects before view resolution."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        target = Redirect.objects.filter(old_path=request.path).first()
        if not target:
            return self.get_response(request)
        if target.is_permanent:
            return HttpResponsePermanentRedirect(target.new_path)
        return HttpResponseRedirect(target.new_path)
