from rest_framework import status
from rest_framework.exceptions import APIException as DRFAPIException


class APIException(DRFAPIException):
    """
    Custom exception class for generating structured API responses.
    """

    def __init__(
        self,
        status_code=400,
        message="A server error occurred.",
    ):
        """
        Initialize the exception with custom response parameters.

        Args:
            status_code (int): The HTTP status code (default is 400).
            message (str): The error message.
        """
        self.detail = {
            "success": False,
            "status_code": status_code,
            "message": message,
        }


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid input."
    default_code = "invalid"

    def __init__(self, detail=None, code=None):
        if isinstance(detail, dict):
            message = list(detail.values())[0]  # first error message
            if isinstance(message, list):
                message = message[0]
        elif isinstance(detail, list):
            message = detail[0]
        else:
            message = detail or self.default_detail

        self.message = message
        super().__init__(message=message, status_code=self.status_code)