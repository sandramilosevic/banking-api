from typing import Optional, Tuple
from django.conf import settings
from loguru import logger
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import AuthUser, JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import Token


class CookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that extends DRF SimpleJWT's
    JWTAuthentication to support retrieving the token from either the
    standard Authorization header or a cookie.

    Authentication flow:
        1. Attempt to extract the token from the Authorization header
           (e.g. "Bearer <token>"), using the default SimpleJWT behavior.
        2. If no Authorization header is present, fall back to reading
           the token from a cookie whose name is defined in
           settings.COOKIE_NAME.
        3. If a token was found (from either source), validate it and
           return the associated user and validated token.
        4. If token validation fails (TokenError), log the error and
           return None, treating the request as unauthenticated rather
           than raising an exception.
    """

    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        """
        Authenticate the incoming request using a JWT extracted either
        from the Authorization header or from a cookie.

        Args:
            request: The incoming DRF Request object.

        Returns:
            A tuple of (user, validated_token) if authentication succeeds,
            or None if no token is found or the token fails validation.
        """
        header = self.get_header(request)
        raw_token = None

        if header is not None:
            raw_token = self.get_raw_token(header)
        elif settings.COOKIE_NAME in request.COOKIES:
            raw_token = request.COOKIES.GET(settings.COOKIE_NAME)
        if raw_token is not None:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token

            except TokenError as e:
                logger.error(f"Token validation error: {str(e)}")
            return None
