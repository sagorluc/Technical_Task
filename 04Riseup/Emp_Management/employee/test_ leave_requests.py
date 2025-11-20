import pytest
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.mark.django_db
class TestLeaveRequests:

    def setup_method(self):
        self.client = APIClient()

    def test_employee_can_create_leave(self, employee_user, employee_profile):
        self.client.force_authenticate(employee_user)
        payload = {
            "leave_type": "SICK",
            "start_date": "2025-01-10",
            "end_date": "2025-01-12",
            "reason": "Fever"
        }
        res = self.client.post("/api/leaves/", payload, format="json")
        assert res.status_code == 201
        assert res.data["employee"] == employee_profile.id

    def test_hr_can_approve(self, hr_user, leave_request):
        self.client.force_authenticate(hr_user)
        url = f"/api/leaves/{leave_request.id}/approve/"
        res = self.client.post(url, {"note": "Approved OK"}, format="json")
        assert res.status_code == 200
        assert res.data["status"] == "APPROVED"

    def test_team_lead_can_reject(self, lead_user, leave_request):
        self.client.force_authenticate(lead_user)
        url = f"/api/leaves/{leave_request.id}/reject/"
        res = self.client.post(url, {"note": "Reason not valid"}, format="json")
        assert res.status_code == 200
        assert res.data["status"] == "REJECTED"

    def test_employee_can_withdraw_own_pending(self, employee_user, pending_leave):
        self.client.force_authenticate(employee_user)
        url = f"/api/leaves/{pending_leave.id}/withdraw/"
        res = self.client.post(url, {"note": "Cancel"}, format="json")
        assert res.status_code == 200
        assert res.data["status"] == "REJECTED"

    def test_hr_can_withdraw_approved(self, hr_user, approved_leave):
        self.client.force_authenticate(hr_user)
        url = f"/api/leaves/{approved_leave.id}/withdraw/"
        res = self.client.post(url, {"note": "Quota fix"}, format="json")
        assert res.status_code == 200
        assert res.data["status"] == "WITHDRAWN"
        
    def test_employee_cannot_approve(self, employee_user, leave_request):
        self.client.force_authenticate(employee_user)
        url = f"/api/leaves/{leave_request.id}/approve/"
        res = self.client.post(url, {"note": "Trying to approve"}, format="json")
        assert res.status_code == 403