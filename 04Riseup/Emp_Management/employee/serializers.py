from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import EmployeeProfile, LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Used by employees to create and view their leave requests."""

    employee_id = serializers.IntegerField(read_only=True, source="employee.id")
    requested_days = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee_id",
            "start_date",
            "end_date",
            "reason",
            "requested_days",
            "status",
            "acted_by_id",
            "acted_at",
            "created_at",
            "updated_at",
            "notes",
        ]
        read_only_fields = [
            "status",
            "requested_days",
            "acted_by_id",
            "acted_at",
            "created_at",
            "updated_at",
            "notes",
        ]

    def validate(self, attrs):
        # ensure end >= start
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "end_date must be >= start_date"}
            )
        return attrs

    def create(self, validated_data):
        # set employee from request.user.employee_profile
        request = self.context.get("request")
        if request is None or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")

        profile = getattr(request.user, "employee_profile", None)
        if profile is None:
            raise serializers.ValidationError("Employee profile not found for user")

        # compute requested_days and call LeaveService.request_leave to ensure canonical behavior
        from .models import \
            LeaveService  # import here to avoid circular import

        start = validated_data["start_date"]
        end = validated_data["end_date"]
        reason = validated_data.get("reason", "")

        # LeaveService.request_leave raises LeaveServiceError on invalid input
        try:
            req = LeaveService.request_leave(
                employee=profile, start_date=start, end_date=end, reason=reason
            )
        except Exception as exc:
            # convert to DRF validation error if it's a service error
            raise serializers.ValidationError({"detail": str(exc)})
        return req


class LeaveActionSerializer(serializers.Serializer):
    """Used for approve/reject/withdraw endpoints. Provide optional note."""

    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class LeaveRequestListSerializer(serializers.ModelSerializer):
    """Light listing serializer for employees/HR list endpoints."""

    employee_email = serializers.CharField(source="employee.user.email", read_only=True)
    requested_days = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee_email",
            "start_date",
            "end_date",
            "requested_days",
            "status",
            "acted_by",
            "acted_at",
            "created_at",
        ]
