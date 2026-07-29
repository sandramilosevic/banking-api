class CustomHeaderMiddleware:
    """
    Django middleware that adds the authenticated user's email
    to the response headers.

    If the request is made by an authenticated user, the middleware
    appends a custom `X-Django-User` header containing the user's
    email address.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            response["X-Django-User"] = request.user.email
        return response
