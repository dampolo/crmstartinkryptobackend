from rest_framework.permissions import BasePermission

class DiscountCodePermission(BasePermission):
    """
    Admins can CRUD.
    Customers can only use validate_code action.
    """
       
    # Allow authenticated users to validate code
    def has_permission(self, request, view):
        if view.action == 'validate_code':
            return request.user and request.user.is_authenticated
        
        # Only admin/staff can do CRUD actions
        return request.user and request.user.is_staff