from django.contrib import admin
from .models import EmployeeSalaryStructure, PayrollRun, Payslip, SalaryComponent

admin.site.register(SalaryComponent)
admin.site.register(EmployeeSalaryStructure)

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ["name", "period_start", "period_end", "state", "total_gross", "total_net"]
    list_filter = ["state"]

admin.site.register(Payslip)
