from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrAdminReadOnly(BasePermission):
    def has_permission(self, request, view):
        return(
            request.method in SAFE_METHODS 
            or (request.user.is_authenticated
                or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        return(
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.is_staff
        )


class IsUserOrAdminReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return(
            request.method in SAFE_METHODS
            or request.user.is_staff
        )


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return(
            request.method in SAFE_METHODS 
            or (request.user.is_authenticated
                and request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff  
