from rest_framework import serializers
from .models import Department, Position


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code", "parent", "manager_id", "cost_center", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Position
        fields = ["id", "title", "department", "department_name", "employment_type", "grade_level", "min_salary", "max_salary", "description", "requirements", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
