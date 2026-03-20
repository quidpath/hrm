from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Employee, EmployeeDocument, EmergencyContact
from .serializers import EmployeeDocumentSerializer, EmployeeListSerializer, EmployeeSerializer, EmergencyContactSerializer


@api_view(["GET", "POST"])
def employee_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = Employee.objects.filter(corporate_id=cid).select_related("department", "position")
        search = request.GET.get("search")
        if search:
            qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(employee_number__icontains=search) | Q(work_email__icontains=search))
        dept = request.GET.get("department")
        if dept:
            qs = qs.filter(department_id=dept)
        status = request.GET.get("status")
        if status:
            qs = qs.filter(employment_status=status)
        return Response(EmployeeListSerializer(qs, many=True).data)
    s = EmployeeSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH"])
def employee_detail(request, pk):
    cid = request.corporate_id
    try:
        emp = Employee.objects.get(pk=pk, corporate_id=cid)
    except Employee.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(EmployeeSerializer(emp).data)
    s = EmployeeSerializer(emp, data=request.data, partial=request.method == "PATCH")
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["POST"])
def upload_document(request, pk):
    cid = request.corporate_id
    try:
        emp = Employee.objects.get(pk=pk, corporate_id=cid)
    except Employee.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    s = EmployeeDocumentSerializer(data=request.data)
    if s.is_valid():
        s.save(employee=emp)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["POST"])
def add_emergency_contact(request, pk):
    cid = request.corporate_id
    try:
        emp = Employee.objects.get(pk=pk, corporate_id=cid)
    except Employee.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    s = EmergencyContactSerializer(data=request.data)
    if s.is_valid():
        s.save(employee=emp)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)
