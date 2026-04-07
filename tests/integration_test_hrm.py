"""
Integration tests for HRM Service
"""
import requests
import uuid

BASE_URL = "http://localhost:8006"

class TestHealthEndpoints:
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/health/")
        assert response.status_code == 200

class TestEmployeeEndpoints:
    def test_list_employees_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/hrm/employees/")
        assert response.status_code in [401, 403]

class TestDepartmentEndpoints:
    def test_list_departments_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/hrm/org/departments/")
        assert response.status_code in [401, 403, 404]

class TestAttendanceEndpoints:
    def test_list_attendance_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/hrm/attendance/")
        assert response.status_code in [401, 403]

class TestLeaveEndpoints:
    def test_list_leaves_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/hrm/leaves/")
        assert response.status_code in [401, 403]

class TestPayrollEndpoints:
    def test_list_payslips_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/hrm/payroll/payslips/")
        assert response.status_code in [401, 403, 404]

class TestRecruitmentEndpoints:
    def test_list_jobs_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/hrm/recruitment/jobs/")
        assert response.status_code in [401, 403, 404]
