from decimal import Decimal
from django.db import models

from hrm_service.core.base_models import BaseModel


class LeaveType(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=100)
    is_paid = models.BooleanField(default=True)
    days_per_year = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("21"))
    carry_forward = models.BooleanField(default=False)
    max_carry_forward_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("10"))
    requires_approval = models.BooleanField(default=True)
    requires_document = models.BooleanField(default=False)
    min_notice_days = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LeaveBalance(BaseModel):
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    year = models.PositiveIntegerField()
    entitled_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    accrued_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    used_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    carried_forward = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))

    class Meta:
        unique_together = [("employee", "leave_type", "year")]

    @property
    def available_days(self):
        return self.accrued_days + self.carried_forward - self.used_days


class LeaveRequest(BaseModel):
    STATES = [
        ("draft", "Draft"), ("submitted", "Submitted"),
        ("approved", "Approved"), ("rejected", "Rejected"), ("cancelled", "Cancelled"),
    ]

    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    state = models.CharField(max_length=20, choices=STATES, default="draft")
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    reason = models.TextField(blank=True)
    document = models.FileField(upload_to="leaves/documents/", null=True, blank=True)
    approved_by = models.UUIDField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days + 1
            self.days_requested = Decimal(str(delta))
        super().save(*args, **kwargs)
