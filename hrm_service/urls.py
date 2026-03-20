from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", lambda request: __import__("django.http", fromlist=["JsonResponse"]).JsonResponse({"status": "ok"})),
    path("api/hrm/org/", include("hrm_service.organization.urls")),
    path("api/hrm/employees/", include("hrm_service.employees.urls")),
    path("api/hrm/recruitment/", include("hrm_service.recruitment.urls")),
    path("api/hrm/attendance/", include("hrm_service.attendance.urls")),
    path("api/hrm/leaves/", include("hrm_service.leaves.urls")),
    path("api/hrm/payroll/", include("hrm_service.payroll.urls")),
    path("api/hrm/performance/", include("hrm_service.performance.urls")),
]
