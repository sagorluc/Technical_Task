from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.response import Response as DRFResponse


class AuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            raise PermissionDenied("You must sign in to access this feature.")
        return True


def Response(success=True, status_code=200, message="Request successful", data=None):
    """
    Utility function to generate a custom API response.

    Args:
        success (bool): Indicates if the request was successful.
        status_code (int): The HTTP status code.
        message (str): A message to describe the response.
        data (dict): The data payload to include in the response.

    Returns:
        Response: A Django REST Framework Response object with the custom structure.

    """
    response = {
        "success": success,
        "status_code": status_code,
        "message": message,
        "data": data if data is not None else [],
    }
    return DRFResponse(response, status=status_code)
