from rest_framework import permissions


class IsEmployeeOwner(permissions.BasePermission):
    """
    Allow only the owner employee (employee_profile.user) to access their object
    for non-approval actions.
    """

    def has_object_permission(self, request, view, obj):
        # obj is LeaveRequest
        if not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "employee_profile", None)
        if profile is None:
            return False
        return obj.employee_id == profile.id


class IsHROrTeamLeadForEmployee(permissions.BasePermission):
    """
    Allow if user is HR, or if user is a team lead for that employee.
    Used for approve/reject/withdraw actions.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        user = request.user
        if getattr(user, "is_hr", False):
            return True
        if getattr(user, "is_team_lead", False):
            # obj.employee is EmployeeProfile
            team = getattr(obj.employee, "team", None)
            return team is not None and team.lead_id == user.id
        return False
