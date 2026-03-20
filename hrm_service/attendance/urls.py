from django.urls import path
from .views import attendance_list_create, clock_in, clock_out, policy_list_create

urlpatterns = [
    path("policies/", policy_list_create),
    path("", attendance_list_create),
    path("employees/<uuid:employee_pk>/clock-in/", clock_in),
    path("employees/<uuid:employee_pk>/clock-out/", clock_out),
]
