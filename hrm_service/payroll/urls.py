from django.urls import path
from .views import (
    approve_payroll, calculate_payroll, employee_salary_structure,
    get_payslip, payroll_run_detail, payroll_run_list_create,
    post_payroll_to_accounting, salary_component_list_create,
)

urlpatterns = [
    path("components/", salary_component_list_create),
    path("employees/<uuid:employee_pk>/salary/", employee_salary_structure),
    path("runs/", payroll_run_list_create),
    path("runs/<uuid:pk>/", payroll_run_detail),
    path("runs/<uuid:pk>/calculate/", calculate_payroll),
    path("runs/<uuid:pk>/approve/", approve_payroll),
    path("runs/<uuid:pk>/post/", post_payroll_to_accounting),
    path("payslips/<uuid:pk>/", get_payslip),
]
