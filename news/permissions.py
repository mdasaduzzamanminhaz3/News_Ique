from rest_framework.permissions import BasePermission

class IsAdminOrEditor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['ADMIN', 'EDITOR']
        )