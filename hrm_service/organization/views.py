from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Department, Position
from .serializers import DepartmentSerializer, PositionSerializer


@api_view(["GET", "POST"])
def department_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(DepartmentSerializer(Department.objects.filter(corporate_id=cid), many=True).data)
    s = DepartmentSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def department_detail(request, pk):
    cid = request.corporate_id
    try:
        dept = Department.objects.get(pk=pk, corporate_id=cid)
    except Department.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(DepartmentSerializer(dept).data)
    if request.method in ("PUT", "PATCH"):
        s = DepartmentSerializer(dept, data=request.data, partial=request.method == "PATCH")
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    dept.is_active = False
    dept.save()
    return Response(status=204)


@api_view(["GET", "POST"])
def position_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(PositionSerializer(Position.objects.filter(corporate_id=cid).select_related("department"), many=True).data)
    s = PositionSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH"])
def position_detail(request, pk):
    cid = request.corporate_id
    try:
        pos = Position.objects.get(pk=pk, corporate_id=cid)
    except Position.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(PositionSerializer(pos).data)
    s = PositionSerializer(pos, data=request.data, partial=request.method == "PATCH")
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)
