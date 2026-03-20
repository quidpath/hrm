from django.urls import path
from .views import add_key_result, goal_detail, goal_list_create, review_detail, review_list_create

urlpatterns = [
    path("goals/", goal_list_create),
    path("goals/<uuid:pk>/", goal_detail),
    path("goals/<uuid:goal_pk>/key-results/", add_key_result),
    path("reviews/", review_list_create),
    path("reviews/<uuid:pk>/", review_detail),
]
