from decimal import Decimal
from django.db import models

from hrm_service.core.base_models import BaseModel


class Goal(BaseModel):
    STATES = [("active", "Active"), ("achieved", "Achieved"), ("missed", "Missed"), ("cancelled", "Cancelled")]

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    state = models.CharField(max_length=20, choices=STATES, default="active")
    target_date = models.DateField(null=True, blank=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    created_by = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.title


class KeyResult(BaseModel):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="key_results")
    description = models.CharField(max_length=300)
    target_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("100"))
    current_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0"))
    unit = models.CharField(max_length=50, default="%")
    due_date = models.DateField(null=True, blank=True)

    @property
    def progress_percent(self):
        if self.target_value == 0:
            return Decimal("0")
        return min((self.current_value / self.target_value) * 100, Decimal("100"))


class PerformanceReview(BaseModel):
    REVIEW_TYPES = [("annual", "Annual"), ("mid_year", "Mid-Year"), ("probation", "Probation"), ("360", "360 Degree")]
    STATES = [("draft", "Draft"), ("self_review", "Self Review"), ("manager_review", "Manager Review"), ("completed", "Completed")]

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="performance_reviews")
    reviewer_id = models.UUIDField(null=True, blank=True)
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES, default="annual")
    state = models.CharField(max_length=20, choices=STATES, default="draft")
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="1.0 to 5.0")
    employee_comments = models.TextField(blank=True)
    manager_comments = models.TextField(blank=True)
    development_plan = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
