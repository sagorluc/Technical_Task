from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import EmployeeProfile, LeaveRequest, LeaveService, LeaveServiceError
from .permissions import IsEmployeeOwner, IsHROrTeamLeadForEmployee
from .serializers import (
    LeaveActionSerializer,
    LeaveRequestListSerializer,
    LeaveRequestSerializer,
)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    - POST /leaves/                -> employee create leave request
    - GET  /leaves/                -> list (employee: own, HR: all, lead: team)
    - GET  /leaves/{pk}/           -> retrieve
    - POST /leaves/{pk}/approve    -> HR/Lead approve
    - POST /leaves/{pk}/reject     -> HR/Lead reject
    - POST /leaves/{pk}/withdraw   -> employee or HR/Lead withdraw
    """

    queryset = LeaveRequest.objects.all().select_related(
        "employee", "employee__user", "acted_by"
    )
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    # -----------------------------------------
    # Disable update & delete (ModelViewSet offers them, but you don't need them)
    # -----------------------------------------
    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Update not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Update not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Delete not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # -----------------------------------------
    # Serializer switching
    # -----------------------------------------
    def get_serializer_class(self):
        if self.action == "list":
            return LeaveRequestListSerializer
        return LeaveRequestSerializer

    # -----------------------------------------
    # Queryset filtering per role
    # -----------------------------------------
    def get_queryset(self):
        user = self.request.user

        if user.is_hr:
            return self.queryset.order_by("-created_at")

        if user.is_team_lead:
            profile = getattr(user, "employee_profile", None)
            if profile and profile.team:
                return self.queryset.filter(employee__team=profile.team).order_by(
                    "-created_at"
                )

        # employee (default)
        profile = getattr(user, "employee_profile", None)
        if profile:
            return self.queryset.filter(employee=profile).order_by("-created_at")

        return LeaveRequest.objects.none()

    # -----------------------------------------
    # Custom retrieve with permissions
    # -----------------------------------------
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()

        # HR or team lead of the employee
        if request.user.is_hr or (
            request.user.is_team_lead
            and getattr(obj.employee.team, "lead_id", None) == request.user.id
        ):
            return super().retrieve(request, *args, **kwargs)

        # Owner
        owner_profile = getattr(request.user, "employee_profile", None)
        if owner_profile and owner_profile.id == obj.employee_id:
            return super().retrieve(request, *args, **kwargs)

        return Response(
            {"detail": "Not found or permission denied."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # -----------------------------------------
    # Approve
    # -----------------------------------------
    @extend_schema(
        summary="Approve a leave request",
        request=LeaveActionSerializer,
        responses={200: LeaveRequestSerializer},
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        lr = self.get_object()
        perm = IsHROrTeamLeadForEmployee()

        if not perm.has_object_permission(request, self, lr):
            return Response({"detail": "Permission denied"}, status=403)

        serializer = LeaveActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated = LeaveService.approve(request.user, lr)
        except LeaveServiceError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(LeaveRequestSerializer(updated).data, status=200)

    # -----------------------------------------
    # Reject
    # -----------------------------------------
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        lr = self.get_object()
        perm = IsHROrTeamLeadForEmployee()

        if not perm.has_object_permission(request, self, lr):
            return Response({"detail": "Permission denied"}, status=403)

        serializer = LeaveActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = serializer.validated_data.get("note")

        try:
            updated = LeaveService.reject(request.user, lr, note)
        except LeaveServiceError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(LeaveRequestSerializer(updated).data, status=200)

    # -----------------------------------------
    # Withdraw
    # -----------------------------------------
    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        lr = self.get_object()

        owner_profile = getattr(request.user, "employee_profile", None)

        # ----- Employee withdrawing their own pending leave -----
        if owner_profile and owner_profile.id == lr.employee_id:
            if lr.status != LeaveRequest.Status.PENDING:
                return Response(
                    {"detail": "You can only withdraw your own pending requests."},
                    status=400,
                )

            lr.status = LeaveRequest.Status.REJECTED
            lr.acted_by = request.user
            lr.acted_at = timezone.now()
            lr.notes = (
                (lr.notes or "")
                + f"\nWithdrawn by employee at {timezone.now().isoformat()}"
            )
            lr.save(update_fields=["status", "acted_by", "acted_at", "notes", "updated_at"])

            return Response(LeaveRequestSerializer(lr).data, status=200)

        # ----- HR / Team Lead withdrawing an approved leave -----
        perm = IsHROrTeamLeadForEmployee()
        if not perm.has_object_permission(request, self, lr):
            return Response({"detail": "Permission denied"}, status=403)

        if lr.status != LeaveRequest.Status.APPROVED:
            return Response(
                {"detail": "Only approved leaves can be withdrawn."}, status=400
            )

        serializer = LeaveActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = serializer.validated_data.get("note")

        try:
            updated = LeaveService.withdraw(request.user, lr, note)
        except LeaveServiceError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(LeaveRequestSerializer(updated).data, status=200)
