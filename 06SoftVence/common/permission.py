from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return request.user.is_authenticated and request.user.role == "admin"

class IsVendorOrAdmin:
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["vendor", "admin"]

    def has_object_permission(self, request, view, obj):
        obj_usr = None
        if hasattr(obj, 'user'):
            obj_usr = obj.user
        elif hasattr(obj, 'service'):
            obj_usr = obj.service.vendor.user
        elif hasattr(obj, 'vendor'):
            obj_usr = obj.vendor.user
        else:
            return False
        
        if request.user.role == "admin":
            return True
        return obj_usr == request.user
