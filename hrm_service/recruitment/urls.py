from django.urls import path
from .views import application_detail, application_list_create, job_detail, job_list_create, schedule_interview

urlpatterns = [
    path("jobs/", job_list_create),
    path("jobs/<uuid:pk>/", job_detail),
    path("jobs/<uuid:job_pk>/applications/", application_list_create),
    path("applications/<uuid:pk>/", application_detail),
    path("applications/<uuid:application_pk>/interviews/", schedule_interview),
]
