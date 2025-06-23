from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow managers to edit feedback.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            # Employees can only read their own feedback
            if not request.user.is_manager:
                return obj.employee == request.user
            # Managers can read feedback they gave
            return obj.manager == request.user
        
        # Write permissions only for managers who gave the feedback
        return request.user.is_manager and obj.manager == request.user

class IsEmployeeOrManager(permissions.BasePermission):
    """
    Custom permission for feedback acknowledgment.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only the employee who received the feedback can acknowledge it
        return obj.employee == request.user
