from rest_framework import serializers
from .models import AttendancePolicy, AttendanceRecord


class AttendancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendancePolicy
        fields = ["id", "name", "work_hours_per_day", "work_days_per_week", "clock_in_grace_minutes", "overtime_threshold_hours", "overtime_rate", "is_active"]
        read_only_fields = ["id"]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = ["id", "employee", "employee_name", "date", "status", "clock_in", "clock_out", "hours_worked", "overtime_hours", "notes", "created_at"]
        read_only_fields = ["id", "hours_worked", "overtime_hours", "created_at"]

    def get_employee_name(self, obj):
        return obj.employee.full_name
