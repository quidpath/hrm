from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import LeaveBalance, LeaveRequest, LeaveType
from .serializers import LeaveBalanceSerializer, LeaveRequestSerializer, LeaveTypeSerializer
from hrm_service.employees.models import Employee
import datetime


@api_view(["GET", "POST"])
def leave_type_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(LeaveTypeSerializer(LeaveType.objects.filter(corporate_id=cid, is_active=True), many=True).data)
    s = LeaveTypeSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET"])
def employee_leave_balances(request, employee_pk):
    cid = request.corporate_id
    try:
        emp = Employee.objects.get(pk=employee_pk, corporate_id=cid)
    except Employee.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    year = int(request.GET.get("year", datetime.date.today().year))
    balances = LeaveBalance.objects.filter(employee=emp, year=year).select_related("leave_type")
    return Response(LeaveBalanceSerializer(balances, many=True).data)


@api_view(["GET", "POST"])
def leave_request_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = LeaveRequest.objects.filter(employee__corporate_id=cid).select_related("employee", "leave_type")
        state = request.GET.get("state")
        if state:
            qs = qs.filter(state=state)
        emp_id = request.GET.get("employee")
        if emp_id:
            qs = qs.filter(employee_id=emp_id)
        return Response(LeaveRequestSerializer(qs, many=True).data)
    s = LeaveRequestSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["POST"])
def approve_leave(request, pk):
    cid = request.corporate_id
    try:
        leave = LeaveRequest.objects.get(pk=pk, employee__corporate_id=cid, state="submitted")
    except LeaveRequest.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    leave.state = "approved"
    leave.approved_by = request.user_id
    leave.save()
    # Deduct from balance
    year = leave.start_date.year
    balance, _ = LeaveBalance.objects.get_or_create(
        employee=leave.employee, leave_type=leave.leave_type, year=year,
        defaults={"entitled_days": leave.leave_type.days_per_year, "accrued_days": leave.leave_type.days_per_year},
    )
    balance.used_days += leave.days_requested
    balance.save()
    return Response(LeaveRequestSerializer(leave).data)


@api_view(["POST"])
def reject_leave(request, pk):
    cid = request.corporate_id
    try:
        leave = LeaveRequest.objects.get(pk=pk, employee__corporate_id=cid, state="submitted")
    except LeaveRequest.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    leave.state = "rejected"
    leave.rejection_reason = request.data.get("reason", "")
    leave.save()
    return Response(LeaveRequestSerializer(leave).data)
