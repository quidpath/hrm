"""
HRM Dashboard Summary with period-over-period comparisons
"""
from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from hrm_service.employees.models import Employee
from hrm_service.leaves.models import LeaveRequest
from hrm_service.organization.models import Department


@api_view(["GET"])
def hrm_summary(request):
    """
    Returns HRM metrics with period-over-period comparisons.
    Compares current month vs previous month.
    """
    cid = request.corporate_id
    
    # Current period (this month)
    now = timezone.now()
    today = now.date()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Previous period (last month)
    if month_start.month == 1:
        prev_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        prev_month_start = month_start.replace(month=month_start.month - 1)
    prev_month_end = month_start - timedelta(seconds=1)
    
    # Helper functions
    def calc_change(current, previous):
        if previous > 0:
            return round(float(((current - previous) / previous) * 100), 1)
        return 0.0
    
    def get_trend(change):
        if change > 0:
            return "up"
        elif change < 0:
            return "down"
        return "neutral"
    
    # Total Employees
    total_employees = Employee.objects.filter(
        corporate_id=cid,
        employment_status='active'
    ).count()
    
    prev_employees = Employee.objects.filter(
        corporate_id=cid,
        employment_status='active',
        date_joined__lt=month_start.date()
    ).count()
    
    employees_change = calc_change(total_employees, prev_employees)
    
    # New Employees This Month
    new_this_month = Employee.objects.filter(
        corporate_id=cid,
        date_joined__gte=month_start.date()
    ).count()
    
    # On Leave Today
    on_leave_today = LeaveRequest.objects.filter(
        corporate_id=cid,
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).count()
    
    # Pending Leave Requests
    pending_leaves = LeaveRequest.objects.filter(
        corporate_id=cid,
        status='pending'
    ).count()
    
    # Departments Count
    departments_count = Department.objects.filter(
        corporate_id=cid,
        is_active=True
    ).count()
    
    # Employees by Department
    departments_with_count = Department.objects.filter(
        corporate_id=cid,
        is_active=True
    ).annotate(
        employee_count=Count('employees', filter=Q(employees__employment_status='active'))
    )
    
    departments_data = [
        {
            "id": str(dept.id),
            "name": dept.name,
            "employee_count": dept.employee_count
        }
        for dept in departments_with_count
    ]
    
    return Response({
        "total_employees": total_employees,
        "total_employees_previous": prev_employees,
        "total_employees_change": employees_change,
        "total_employees_trend": get_trend(employees_change),
        
        "new_this_month": new_this_month,
        "on_leave_today": on_leave_today,
        "pending_leaves": pending_leaves,
        "departments_count": departments_count,
        "departments": departments_data,
    })
