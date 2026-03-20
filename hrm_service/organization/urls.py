from django.urls import path
from .views import department_detail, department_list_create, position_detail, position_list_create

urlpatterns = [
    path("departments/", department_list_create),
    path("departments/<uuid:pk>/", department_detail),
    path("positions/", position_list_create),
    path("positions/<uuid:pk>/", position_detail),
]
