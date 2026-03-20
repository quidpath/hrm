from rest_framework import serializers
from .models import EmployeeSalaryStructure, PayrollRun, Payslip, SalaryComponent


class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = ["id", "name", "component_type", "is_taxable", "is_statutory", "is_active"]
        read_only_fields = ["id"]


class EmployeeSalaryStructureSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source="component.name", read_only=True)

    class Meta:
        model = EmployeeSalaryStructure
        fields = ["id", "employee", "component", "component_name", "amount", "effective_from", "effective_to", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_number = serializers.CharField(source="employee.employee_number", read_only=True)

    class Meta:
        model = Payslip
        fields = [
            "id", "payroll_run", "employee", "employee_name", "employee_number",
            "basic_salary", "gross_salary", "taxable_income", "paye_tax",
            "nssf_employee", "nssf_employer", "nhif_deduction", "housing_levy",
            "other_deductions", "total_deductions", "net_salary", "lines", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_employee_name(self, obj):
        return obj.employee.full_name


class PayrollRunSerializer(serializers.ModelSerializer):
    payslip_count = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = [
            "id", "name", "period_start", "period_end", "pay_date", "state",
            "total_gross", "total_deductions", "total_net", "total_employer_nssf",
            "journal_ref", "notes", "created_by", "approved_by", "created_at", "payslip_count",
        ]
        read_only_fields = ["id", "total_gross", "total_deductions", "total_net", "total_employer_nssf", "created_at"]

    def get_payslip_count(self, obj):
        return obj.payslips.count()
