from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Goal, KeyResult, PerformanceReview
from .serializers import GoalSerializer, KeyResultSerializer, PerformanceReviewSerializer
from hrm_service.employees.models import Employee


@api_view(["GET", "POST"])
def goal_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = Goal.objects.filter(employee__corporate_id=cid).select_related("employee")
        emp_id = request.GET.get("employee")
        if emp_id:
            qs = qs.filter(employee_id=emp_id)
        return Response(GoalSerializer(qs, many=True).data)
    s = GoalSerializer(data=request.data)
    if s.is_valid():
        s.save(created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PATCH"])
def goal_detail(request, pk):
    cid = request.corporate_id
    try:
        goal = Goal.objects.get(pk=pk, employee__corporate_id=cid)
    except Goal.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(GoalSerializer(goal).data)
    s = GoalSerializer(goal, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["POST"])
def add_key_result(request, goal_pk):
    cid = request.corporate_id
    try:
        goal = Goal.objects.get(pk=goal_pk, employee__corporate_id=cid)
    except Goal.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    s = KeyResultSerializer(data=request.data)
    if s.is_valid():
        s.save(goal=goal)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def review_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = PerformanceReview.objects.filter(employee__corporate_id=cid).select_related("employee")
        emp_id = request.GET.get("employee")
        if emp_id:
            qs = qs.filter(employee_id=emp_id)
        return Response(PerformanceReviewSerializer(qs, many=True).data)
    s = PerformanceReviewSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PATCH"])
def review_detail(request, pk):
    cid = request.corporate_id
    try:
        rev = PerformanceReview.objects.get(pk=pk, employee__corporate_id=cid)
    except PerformanceReview.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(PerformanceReviewSerializer(rev).data)
    s = PerformanceReviewSerializer(rev, data=request.data, partial=True)
    if s.is_valid():
        if request.data.get("state") == "completed":
            s.save(completed_at=timezone.now())
        else:
            s.save()
        return Response(s.data)
    return Response(s.errors, status=400)
