from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AttendancePolicy, AttendanceRecord
from .serializers import AttendancePolicySerializer, AttendanceRecordSerializer
from hrm_service.employees.models import Employee


@api_view(["GET", "POST"])
def policy_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(AttendancePolicySerializer(AttendancePolicy.objects.filter(corporate_id=cid), many=True).data)
    s = AttendancePolicySerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def attendance_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = AttendanceRecord.objects.filter(employee__corporate_id=cid).select_related("employee")
        emp_id = request.GET.get("employee")
        if emp_id:
            qs = qs.filter(employee_id=emp_id)
        date = request.GET.get("date")
        if date:
            qs = qs.filter(date=date)
        month = request.GET.get("month")
        if month:
            qs = qs.filter(date__startswith=month)
        return Response(AttendanceRecordSerializer(qs, many=True).data)
    s = AttendanceRecordSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["POST"])
def clock_in(request, employee_pk):
    cid = request.corporate_id
    try:
        emp = Employee.objects.get(pk=employee_pk, corporate_id=cid)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)
    today = timezone.now().date()
    record, created = AttendanceRecord.objects.get_or_create(
        employee=emp, date=today,
        defaults={"clock_in": timezone.now(), "status": "present"},
    )
    if not created and record.clock_in:
        return Response({"error": "Already clocked in today"}, status=400)
    record.clock_in = timezone.now()
    record.status = "present"
    record.save()
    return Response(AttendanceRecordSerializer(record).data)


@api_view(["POST"])
def clock_out(request, employee_pk):
    cid = request.corporate_id
    try:
        emp = Employee.objects.get(pk=employee_pk, corporate_id=cid)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)
    today = timezone.now().date()
    try:
        record = AttendanceRecord.objects.get(employee=emp, date=today)
    except AttendanceRecord.DoesNotExist:
        return Response({"error": "No clock-in record for today"}, status=400)
    if record.clock_out:
        return Response({"error": "Already clocked out"}, status=400)
    record.clock_out = timezone.now()
    record.save()
    return Response(AttendanceRecordSerializer(record).data)
