import logging
from decimal import Decimal
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from hrm_service.employees.models import Employee
from hrm_service.payroll.kenya_tax import calculate_payslip
from hrm_service.payroll.models import (
    EmployeeSalaryStructure, PayrollRun, Payslip, SalaryComponent,
)
from hrm_service.payroll.serializers import (
    EmployeeSalaryStructureSerializer, PayrollRunSerializer,
    PayslipSerializer, SalaryComponentSerializer,
)
from hrm_service.services.erp_client import ERPClient

logger = logging.getLogger(__name__)
erp_client = ERPClient()


@api_view(["GET", "POST"])
def salary_component_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(SalaryComponentSerializer(SalaryComponent.objects.filter(corporate_id=cid), many=True).data)
    s = SalaryComponentSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def employee_salary_structure(request, employee_pk):
    cid = request.corporate_id
    try:
        emp = Employee.objects.get(pk=employee_pk, corporate_id=cid)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)
    if request.method == "GET":
        return Response(EmployeeSalaryStructureSerializer(
            EmployeeSalaryStructure.objects.filter(employee=emp, effective_to__isnull=True), many=True
        ).data)
    s = EmployeeSalaryStructureSerializer(data=request.data)
    if s.is_valid():
        s.save(employee=emp)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def payroll_run_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(PayrollRunSerializer(PayrollRun.objects.filter(corporate_id=cid), many=True).data)
    s = PayrollRunSerializer(data=request.data)
    if s.is_valid():
        run = s.save(corporate_id=cid, created_by=request.user_id)
        return Response(PayrollRunSerializer(run).data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PATCH"])
def payroll_run_detail(request, pk):
    cid = request.corporate_id
    try:
        run = PayrollRun.objects.get(pk=pk, corporate_id=cid)
    except PayrollRun.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        data = PayrollRunSerializer(run).data
        data["payslips"] = PayslipSerializer(run.payslips.select_related("employee"), many=True).data
        return Response(data)
    s = PayrollRunSerializer(run, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["POST"])
def calculate_payroll(request, pk):
    """
    Calculate all payslips for a payroll run using the Kenya tax engine.
    Deletes and recalculates existing payslips.
    """
    cid = request.corporate_id
    try:
        run = PayrollRun.objects.get(pk=pk, corporate_id=cid, state__in=["draft", "calculating"])
    except PayrollRun.DoesNotExist:
        return Response({"error": "Payroll run not found or already processed"}, status=404)

    run.state = "calculating"
    run.save()

    # Clear previous payslips
    run.payslips.all().delete()

    employees = Employee.objects.filter(corporate_id=cid, employment_status__in=["active", "on_leave", "probation"])
    total_gross = Decimal("0")
    total_deductions = Decimal("0")
    total_net = Decimal("0")
    total_employer_nssf = Decimal("0")

    for emp in employees:
        # Sum up all active salary structure components
        structures = EmployeeSalaryStructure.objects.filter(
            employee=emp, effective_to__isnull=True,
            effective_from__lte=run.period_end,
        ).select_related("component")

        gross = sum(
            s.amount for s in structures
            if s.component.component_type in ("basic", "allowance")
        )
        other_deductions = sum(
            s.amount for s in structures
            if s.component.component_type == "deduction"
        )

        calc = calculate_payslip(gross, other_deductions)

        payslip = Payslip.objects.create(
            payroll_run=run,
            employee=emp,
            basic_salary=gross,
            gross_salary=calc["gross_salary"],
            taxable_income=calc["taxable_income"],
            paye_tax=calc["paye"],
            nssf_employee=calc["nssf_employee"],
            nssf_employer=calc["nssf_employer"],
            nhif_deduction=calc["sha"],
            housing_levy=calc["housing_levy_employee"],
            other_deductions=calc["other_deductions"],
            total_deductions=calc["total_deductions"],
            net_salary=calc["net_salary"],
            lines=[
                {"name": "Basic Salary", "type": "earning", "amount": str(gross)},
                {"name": "PAYE", "type": "deduction", "amount": str(calc["paye"])},
                {"name": "NSSF Employee", "type": "deduction", "amount": str(calc["nssf_employee"])},
                {"name": "SHA", "type": "deduction", "amount": str(calc["sha"])},
                {"name": "Housing Levy", "type": "deduction", "amount": str(calc["housing_levy_employee"])},
                {"name": "Other Deductions", "type": "deduction", "amount": str(other_deductions)},
                {"name": "Net Pay", "type": "net", "amount": str(calc["net_salary"])},
            ],
        )

        total_gross += calc["gross_salary"]
        total_deductions += calc["total_deductions"]
        total_net += calc["net_salary"]
        total_employer_nssf += calc["nssf_employer"]

    run.total_gross = total_gross
    run.total_deductions = total_deductions
    run.total_net = total_net
    run.total_employer_nssf = total_employer_nssf
    run.state = "review"
    run.save()

    return Response(PayrollRunSerializer(run).data)


@api_view(["POST"])
def approve_payroll(request, pk):
    cid = request.corporate_id
    try:
        run = PayrollRun.objects.get(pk=pk, corporate_id=cid, state="review")
    except PayrollRun.DoesNotExist:
        return Response({"error": "Not found or not in review state"}, status=404)
    run.state = "approved"
    run.approved_by = request.user_id
    run.save()
    return Response(PayrollRunSerializer(run).data)


@api_view(["POST"])
def post_payroll_to_accounting(request, pk):
    """Post payroll journal entry to ERP Accounting."""
    cid = request.corporate_id
    try:
        run = PayrollRun.objects.get(pk=pk, corporate_id=cid, state="approved")
    except PayrollRun.DoesNotExist:
        return Response({"error": "Approved payroll run not found"}, status=404)

    journal_payload = {
        "corporate_id": str(cid),
        "reference": f"PAYROLL-{run.period_start}-{run.period_end}",
        "description": f"Payroll: {run.name}",
        "lines": [
            {"account": "Salaries Expense", "debit": str(run.total_gross), "credit": "0"},
            {"account": "NSSF Payable (Employer)", "debit": str(run.total_employer_nssf), "credit": "0"},
            {"account": "PAYE Payable", "debit": "0", "credit": str(sum(p.paye_tax for p in run.payslips.all()))},
            {"account": "NSSF Payable (Employee)", "debit": "0", "credit": str(sum(p.nssf_employee for p in run.payslips.all()))},
            {"account": "SHA Payable", "debit": "0", "credit": str(sum(p.nhif_deduction for p in run.payslips.all()))},
            {"account": "Net Salaries Payable", "debit": "0", "credit": str(run.total_net)},
        ],
    }

    result = erp_client.create_journal_entry(journal_payload)
    if result:
        run.journal_ref = result.get("reference", "")
        run.state = "paid"
        run.save()
        return Response({"journal": result, "run": PayrollRunSerializer(run).data})
    return Response({"error": "Failed to post to Accounting"}, status=502)


@api_view(["GET"])
def get_payslip(request, pk):
    cid = request.corporate_id
    try:
        payslip = Payslip.objects.select_related("employee", "payroll_run").get(
            pk=pk, employee__corporate_id=cid
        )
    except Payslip.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response(PayslipSerializer(payslip).data)
