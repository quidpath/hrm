from django.db import models

from hrm_service.core.base_models import BaseModel


class Department(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="sub_departments")
    manager_id = models.UUIDField(null=True, blank=True, help_text="Employee UUID of department head")
    cost_center = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("corporate_id", "name")]

    def __str__(self):
        return self.name


class Position(BaseModel):
    EMPLOYMENT_TYPES = [
        ("full_time", "Full Time"), ("part_time", "Part Time"),
        ("contract", "Contract"), ("intern", "Intern"), ("casual", "Casual"),
    ]

    corporate_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="positions")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default="full_time")
    grade_level = models.CharField(max_length=50, blank=True)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} — {self.department.name}"
