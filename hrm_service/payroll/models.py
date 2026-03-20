from decimal import Decimal
from django.db import models

from hrm_service.core.base_models import BaseModel


class SalaryComponent(BaseModel):
    COMPONENT_TYPES = [
        ("basic", "Basic Salary"),
        ("allowance", "Allowance"),
        ("deduction", "Deduction"),
        ("benefit", "Benefit"),
    ]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    is_taxable = models.BooleanField(default=True)
    is_statutory = models.BooleanField(default=False, help_text="PAYE, NSSF, NHIF, etc.")
    affects_nssf = models.BooleanField(default=False)
    affects_nhif = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class EmployeeSalaryStructure(BaseModel):
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, related_name="salary_structures")
    component = models.ForeignKey(SalaryComponent, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.employee} — {self.component.name}: {self.amount}"


class PayrollRun(BaseModel):
    STATES = [
        ("draft", "Draft"),
        ("calculating", "Calculating"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()
    pay_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATES, default="draft")
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total_employer_nssf = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    journal_ref = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.UUIDField(null=True, blank=True)
    approved_by = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-period_start"]

    def __str__(self):
        return f"{self.name} ({self.period_start} to {self.period_end})"


class Payslip(BaseModel):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="payslips")
    employee = models.ForeignKey("employees.Employee", on_delete=models.PROTECT, related_name="payslips")
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    paye_tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    nssf_employee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), help_text="Employee NSSF contribution")
    nssf_employer = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), help_text="Employer NSSF contribution")
    nhif_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), help_text="SHA/NHIF monthly contribution")
    housing_levy = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), help_text="Affordable Housing Levy 1.5%")
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    lines = models.JSONField(default=list, help_text="Breakdown of all components")

    def __str__(self):
        return f"Payslip: {self.employee} — {self.payroll_run.period_start}"
