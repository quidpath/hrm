from rest_framework import serializers
from .models import Goal, KeyResult, PerformanceReview


class KeyResultSerializer(serializers.ModelSerializer):
    progress_percent = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = KeyResult
        fields = ["id", "description", "target_value", "current_value", "unit", "due_date", "progress_percent", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class GoalSerializer(serializers.ModelSerializer):
    key_results = KeyResultSerializer(many=True, read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ["id", "employee", "employee_name", "title", "description", "state", "target_date", "progress_percent", "created_at", "key_results"]
        read_only_fields = ["id", "created_at"]

    def get_employee_name(self, obj):
        return obj.employee.full_name


class PerformanceReviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = PerformanceReview
        fields = [
            "id", "employee", "employee_name", "reviewer_id", "review_type",
            "state", "review_period_start", "review_period_end", "overall_rating",
            "employee_comments", "manager_comments", "development_plan", "created_at", "completed_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_employee_name(self, obj):
        return obj.employee.full_name
