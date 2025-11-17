from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    """Allow access only to teachers."""
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'teacher_profile'))


class IsStudent(BasePermission):
    """Allow access only to students."""
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'student_profile'))


class IsAdmin(BasePermission):
    """Allow access only to superusers (admins)."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
