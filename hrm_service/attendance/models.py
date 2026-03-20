from decimal import Decimal
from django.db import models

from hrm_service.core.base_models import BaseModel


class AttendancePolicy(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    work_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("8"))
    work_days_per_week = models.PositiveIntegerField(default=5)
    clock_in_grace_minutes = models.PositiveIntegerField(default=15)
    overtime_threshold_hours = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("8"))
    overtime_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("1.5"))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AttendanceRecord(BaseModel):
    STATUSES = [
        ("present", "Present"), ("absent", "Absent"), ("late", "Late"),
        ("half_day", "Half Day"), ("on_leave", "On Leave"), ("holiday", "Public Holiday"),
    ]

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUSES, default="present")
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    notes = models.CharField(max_length=300, blank=True)

    class Meta:
        unique_together = [("employee", "date")]

    def save(self, *args, **kwargs):
        if self.clock_in and self.clock_out:
            delta = self.clock_out - self.clock_in
            self.hours_worked = Decimal(str(round(delta.total_seconds() / 3600, 2)))
            self.overtime_hours = max(self.hours_worked - Decimal("8"), Decimal("0"))
        super().save(*args, **kwargs)
