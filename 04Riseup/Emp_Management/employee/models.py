"""
Django models + services for a scalable Leave Management design matching the requirements. # noqa: E501
- Employees must have emails starting with 'appcubeemployee'
- Monthly take-off quota tracked and restored on withdrawal
- Employees can request leave; HR and TeamLead can approve/withdraw/reject
- TeamLead manages employees in their team

File contains:
- CustomUser (example) with validator
- Team, EmployeeProfile
- LeaveRequest, LeaveQuotaSnapshot, LeaveBalanceChange
- LeaveService: atomic operations to request/approve/withdraw/reject leave
- Signals/notes and recommended indexes

Assumptions:
- Django >= 3.2
- Timezone-aware datetimes
- Business days vs calendar days: this uses calendar days; replace days calculation if you need working days

This file focuses on models + service layer. Keep views/serializers/permissions separate for clarity.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone

from .validators import validate_appcube_email

# -----------------------
# User & Roles
# -----------------------


class User(AbstractUser):
    """Custom user to show role flags. In real project, prefer a role model or groups/permissions. # noqa: E501"""

    email = models.EmailField(unique=True, validators=[validate_appcube_email])
    is_hr = models.BooleanField(default=False)
    is_team_lead = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.username} <{self.email}>"


# -----------------------
# Team & EmployeeProfile
# -----------------------


class Team(models.Model):
    name = models.CharField(max_length=128)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leading_teams",
    )

    class Meta:
        unique_together = ("name",)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class EmployeeProfile(models.Model):
    """Profile with quota defaults and references to user and team."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="members"
    )
    default_monthly_quota = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("2.00")
    )
    current_month_balance = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"EmployeeProfile({self.user_id})"


# -----------------------
# Leave models
# -----------------------


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"
        WITHDRAWN = "WITHDRAWN"  # used when HR/Lead withdraws approval to restore quota

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="leave_requests"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)

    requested_days = models.DecimalField(max_digits=6, decimal_places=2)

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    # Track who acted on the request
    acted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acted_leave_requests",
    )
    acted_at = models.DateTimeField(null=True, blank=True)

    # Optional: keep a JSON audit trail or use separate model for history
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["employee", "status", "start_date"])]

    def clean(self) -> None:
        if self.end_date < self.start_date:
            raise ValidationError("end_date must be on or after start_date")

    @property
    def days(self) -> Decimal:
        # Simple calendar-days calculation; replace with business-day logic if required.
        delta = (self.end_date - self.start_date).days + 1
        return Decimal(delta)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"LeaveRequest({self.pk}) {self.employee.user.email} {self.start_date}..{self.end_date} {self.status}"  # noqa: E501


class LeaveBalanceChange(models.Model):
    """Ledger of balance changes so we can audit and restore on withdrawal."""

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="balance_changes"
    )
    leave_request = models.ForeignKey(
        LeaveRequest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="balance_changes",
    )

    # positive values increase balance (e.g., monthly allotment restored), negative decrease it (approved leave) # noqa: E501
    delta = models.DecimalField(max_digits=7, decimal_places=2)
    reason = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"BalanceChange({self.employee_id}, {self.delta})"


class LeaveQuotaSnapshot(models.Model):
    """Optional: snapshot of monthly quota allocation. Useful for reporting and restoring when months roll over."""  # noqa: E501

    employee = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="quota_snapshots"
    )
    year = models.IntegerField(db_index=True)
    month = models.IntegerField(db_index=True)
    allocated = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        unique_together = ("employee", "year", "month")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"QuotaSnapshot({self.employee_id} {self.year}-{self.month}: {self.allocated})"  # noqa: E501


# -----------------------
# Service layer (single source of truth for business logic)
# -----------------------


class LeaveServiceError(Exception):
    pass


class LeaveService:
    """
    Use this service to perform leave workflows. All mutating operations are atomic.

    Methods:
    - request_leave(employee_profile, start_date, end_date, reason)
    - approve(approver_user, leave_request_pk)
    - reject(approver_user, leave_request_pk)
    - withdraw(approver_user, leave_request_pk)

    Important: approver_user must be HR or Team Lead responsible for the employee.
    """

    @staticmethod
    def _check_approver_permission(
        approver_user: User, employee_profile: EmployeeProfile
    ) -> None:
        if approver_user.is_hr:
            return
        if (
            approver_user.is_team_lead
            and employee_profile.team
            and employee_profile.team.lead_id == approver_user.id
        ):
            return
        raise LeaveServiceError("User not authorized to act on this leave")

    @staticmethod
    def get_current_balance(employee: EmployeeProfile) -> Decimal:
        """Calculate current balance by summing ledger. This is authoritative.
        For performance, cache/denormalize if necessary.
        """
        agg = employee.balance_changes.aggregate(total=models.Sum("delta"))
        total = agg["total"] or Decimal("0.00")
        return Decimal(total)

    @staticmethod
    def ensure_monthly_allocation_for(
        employee: EmployeeProfile, year: int, month: int
    ) -> None:
        """Allocate monthly quota snapshot if missing (idempotent). Should be called by cron or on-demand. # noqa: E501
        This creates a positive BalanceChange equal to default_monthly_quota for the month. # noqa: E501
        """
        snapshot, created = LeaveQuotaSnapshot.objects.get_or_create(
            employee=employee,
            year=year,
            month=month,
            defaults={"allocated": employee.default_monthly_quota},
        )
        if created:
            LeaveBalanceChange.objects.create(
                employee=employee,
                delta=employee.default_monthly_quota,
                reason=f"Monthly allocation {year}-{month}",
            )

    @staticmethod
    def request_leave(
        employee: EmployeeProfile, start_date: date, end_date: date, reason: str = ""
    ) -> LeaveRequest:
        # Basic validation
        if end_date < start_date:
            raise LeaveServiceError("end_date must be >= start_date")

        requested_days = Decimal((end_date - start_date).days + 1)

        # Create request
        with transaction.atomic():
            req = LeaveRequest.objects.create(
                employee=employee,
                start_date=start_date,
                end_date=end_date,
                requested_days=requested_days,
                reason=reason or "",
                status=LeaveRequest.Status.PENDING,
            )
        return req

    @staticmethod
    def approve(approver_user: User, leave_request: LeaveRequest) -> LeaveRequest:
        """Approve a pending request and deduct quota. Raises on insufficient balance or invalid status."""  # noqa: E501
        LeaveService._check_approver_permission(approver_user, leave_request.employee)

        with transaction.atomic():
            # Lock the leave row for update to avoid races
            lr = LeaveRequest.objects.select_for_update().get(pk=leave_request.pk)
            if lr.status != LeaveRequest.Status.PENDING:
                raise LeaveServiceError("Only pending leaves can be approved")

            # ensure allocations exist for involved months
            # naive approach: allocate for each month touched by the leave
            cur = lr.start_date
            while cur <= lr.end_date:
                LeaveService.ensure_monthly_allocation_for(
                    lr.employee, cur.year, cur.month
                )
                # move to first of next month
                if cur.month == 12:
                    cur = date(cur.year + 1, 1, 1)
                else:
                    cur = date(cur.year, cur.month + 1, 1)

            # compute current balance (after allocations)
            balance = LeaveService.get_current_balance(lr.employee)
            if balance < lr.requested_days:
                raise LeaveServiceError("Insufficient leave balance")

            # Deduct
            LeaveBalanceChange.objects.create(
                employee=lr.employee,
                leave_request=lr,
                delta=-lr.requested_days,
                reason=f"Approved leave deduction for request {lr.pk}",
            )

            lr.status = LeaveRequest.Status.APPROVED
            lr.acted_by = approver_user
            lr.acted_at = timezone.now()
            lr.save(update_fields=["status", "acted_by", "acted_at", "updated_at"])
        return lr

    @staticmethod
    def reject(
        approver_user: User, leave_request: LeaveRequest, note: Optional[str] = None
    ) -> LeaveRequest:
        LeaveService._check_approver_permission(approver_user, leave_request.employee)

        with transaction.atomic():
            lr = LeaveRequest.objects.select_for_update().get(pk=leave_request.pk)
            if lr.status != LeaveRequest.Status.PENDING:
                raise LeaveServiceError("Only pending leaves can be rejected")
            lr.status = LeaveRequest.Status.REJECTED
            lr.acted_by = approver_user
            lr.acted_at = timezone.now()
            if note:
                lr.notes = (lr.notes or "") + f"\nRejected note: {note}"
            lr.save(
                update_fields=["status", "acted_by", "acted_at", "notes", "updated_at"]
            )
        return lr

    @staticmethod
    def withdraw(
        approver_user: User, leave_request: LeaveRequest, note: Optional[str] = None
    ) -> LeaveRequest:
        """Withdraw an already approved leave — this restores the quota for that request. # noqa: E501
        Can be used when HR/Lead wants to cancel previously approved leave.
        """
        LeaveService._check_approver_permission(approver_user, leave_request.employee)

        with transaction.atomic():
            lr = LeaveRequest.objects.select_for_update().get(pk=leave_request.pk)
            if lr.status != LeaveRequest.Status.APPROVED:
                raise LeaveServiceError("Only approved leaves can be withdrawn")

            # Restore ledger
            LeaveBalanceChange.objects.create(
                employee=lr.employee,
                leave_request=lr,
                delta=lr.requested_days,  # restore
                reason=f"Withdrawal restore for request {lr.pk}",
            )

            lr.status = LeaveRequest.Status.WITHDRAWN
            lr.acted_by = approver_user
            lr.acted_at = timezone.now()
            if note:
                lr.notes = (lr.notes or "") + f"\nWithdrawn note: {note}"
            lr.save(
                update_fields=["status", "acted_by", "acted_at", "notes", "updated_at"]
            )
        return lr


# -----------------------
# Usage notes / next steps (non-executable comments)
# -----------------------
# - Wire these into Django admin/REST API with appropriate permissions.
# - Views/serializers should call LeaveService to mutate state.
# - Create periodic task (cron/beat) to call ensure_monthly_allocation_for() for each active employee at month start. # noqa: E501
# - For performance, keep a denormalized current_month_balance in EmployeeProfile and update it inside the same transaction as balance changes. # noqa: E501
# - Add tests around concurrent approve/withdraw flows using select_for_update to avoid race conditions. # noqa: E501
# - Consider utilising a separate Role/Permission model (django-guardian or groups) for complex access rules. # noqa: E501
