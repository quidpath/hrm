from django.urls import path
from .views import approve_leave, employee_leave_balances, leave_request_list_create, leave_type_list_create, reject_leave

urlpatterns = [
    path("types/", leave_type_list_create),
    path("employees/<uuid:employee_pk>/balances/", employee_leave_balances),
    path("requests/", leave_request_list_create),
    path("requests/<uuid:pk>/approve/", approve_leave),
    path("requests/<uuid:pk>/reject/", reject_leave),
]
