from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

from .models import Redirect


class RedirectMiddleware:
    """Apply DB redirects before view resolution."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            target = Redirect.objects.get(old_path=request.path)
        except Redirect.DoesNotExist:
            return self.get_response(request)
        if target.is_permanent:
            return HttpResponsePermanentRedirect(target.new_path)
        return HttpResponseRedirect(target.new_path)
