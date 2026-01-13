
from rest_framework.response import Response as DRFResponse

def Response(success=True, status_code=200, message="Request successful", data=None):
    response = {
        "success": success,
        "status_code": status_code,
        "message": message,
        "data": data if data is not None else [],
    }
    return DRFResponse(response, status=status_code)