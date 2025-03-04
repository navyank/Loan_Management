from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        auth = JWTAuthentication()
        user_auth = auth.authenticate(request)

        if user_auth is None:
            return False

        user, token = user_auth

        return token.get("role") == "admin"


class IsNormalUser(BasePermission):
    """
    Allows access only to normal users.
    """

    def has_permission(self, request, view):
        auth = JWTAuthentication()
        user_auth = auth.authenticate(request)

        if user_auth is None:
            return False

        user, token = user_auth

        return token.get("role") == "user"
