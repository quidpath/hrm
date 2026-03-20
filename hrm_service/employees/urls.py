from django.urls import path
from .views import add_emergency_contact, employee_detail, employee_list_create, upload_document

urlpatterns = [
    path("", employee_list_create),
    path("<uuid:pk>/", employee_detail),
    path("<uuid:pk>/documents/", upload_document),
    path("<uuid:pk>/emergency-contacts/", add_emergency_contact),
]
