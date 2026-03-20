from rest_framework import serializers
from .models import LeaveBalance, LeaveRequest, LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "is_paid", "days_per_year", "carry_forward", "max_carry_forward_days", "requires_approval", "requires_document", "min_notice_days", "is_active"]
        read_only_fields = ["id"]


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    available_days = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = LeaveBalance
        fields = ["id", "leave_type", "leave_type_name", "year", "entitled_days", "accrued_days", "used_days", "carried_forward", "available_days", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    state_display = serializers.CharField(source="get_state_display", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id", "employee", "employee_name", "leave_type", "leave_type_name",
            "state", "state_display", "start_date", "end_date", "days_requested",
            "reason", "document", "approved_by", "rejection_reason", "created_at",
        ]
        read_only_fields = ["id", "days_requested", "approved_by", "created_at"]

    def get_employee_name(self, obj):
        return obj.employee.full_name
