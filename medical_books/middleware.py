from django.http import HttpResponseBadRequest

class SanitizeHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(',')[0].strip()  # Take first domain if duplicated
        request.META['HTTP_HOST'] = host
        return self.get_response(request)