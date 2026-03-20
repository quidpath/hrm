"""
Kenya-compliant payroll tax engine.
Implements current KRA PAYE bands, NSSF Tier I/II, SHA (formerly NHIF),
Affordable Housing Levy, and SHIF calculations.

Tax bands effective FY 2023/2024:
  - 0 to 24,000: 10%
  - 24,001 to 32,333: 25%
  - 32,334 and above: 30%
  - Personal relief: KES 2,400/month
"""
from decimal import Decimal, ROUND_HALF_UP


def round2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_paye(taxable_income: Decimal) -> Decimal:
    """
    Calculate PAYE using Kenya's progressive bands (monthly).
    Personal relief of KES 2,400 applied after tax computation.
    """
    ti = taxable_income
    if ti <= 0:
        return Decimal("0")

    tax = Decimal("0")

    # Band 1: 0–24,000 @ 10%
    band1 = min(ti, Decimal("24000"))
    tax += band1 * Decimal("0.10")
    ti -= band1

    if ti <= 0:
        return round2(max(tax - Decimal("2400"), Decimal("0")))

    # Band 2: 24,001–32,333 @ 25%
    band2 = min(ti, Decimal("8333"))
    tax += band2 * Decimal("0.25")
    ti -= band2

    if ti <= 0:
        return round2(max(tax - Decimal("2400"), Decimal("0")))

    # Band 3: above 32,333 @ 30%
    tax += ti * Decimal("0.30")

    # Deduct personal relief
    tax -= Decimal("2400")
    return round2(max(tax, Decimal("0")))


def calculate_nssf(gross_salary: Decimal) -> dict:
    """
    NSSF Act 2013 — Tier I and Tier II contributions.
    Lower Earnings Limit (LEL): KES 7,000
    Upper Earnings Limit (UEL): KES 36,000
    Tier I: 6% of the lower of gross or LEL (max: KES 420 employee, KES 420 employer)
    Tier II: 6% of the excess up to UEL (employee + employer)
    Total max Tier I employee: 420, Tier I employer: 420
    """
    LEL = Decimal("7000")
    UEL = Decimal("36000")
    rate = Decimal("0.06")

    tier1_base = min(gross_salary, LEL)
    tier1_employee = round2(tier1_base * rate)
    tier1_employer = tier1_employee

    tier2_base = max(min(gross_salary, UEL) - LEL, Decimal("0"))
    tier2_employee = round2(tier2_base * rate)
    tier2_employer = tier2_employee

    return {
        "tier1_employee": tier1_employee,
        "tier1_employer": tier1_employer,
        "tier2_employee": tier2_employee,
        "tier2_employer": tier2_employer,
        "total_employee": tier1_employee + tier2_employee,
        "total_employer": tier1_employer + tier2_employer,
    }


def calculate_sha(gross_salary: Decimal) -> Decimal:
    """
    Social Health Authority (SHA) contribution — 2.75% of gross salary (no cap as of 2024).
    """
    return round2(gross_salary * Decimal("0.0275"))


def calculate_housing_levy(gross_salary: Decimal) -> Decimal:
    """
    Affordable Housing Levy — 1.5% of gross salary (employee side).
    Employer also contributes 1.5% (not deducted from employee).
    """
    return round2(gross_salary * Decimal("0.015"))


def calculate_payslip(gross_salary: Decimal, other_deductions: Decimal = Decimal("0")) -> dict:
    """
    Full payslip calculation for a Kenya employee.
    Returns all deductions and net pay.
    """
    nssf = calculate_nssf(gross_salary)
    sha = calculate_sha(gross_salary)
    housing_levy = calculate_housing_levy(gross_salary)

    # NSSF employee contribution is deducted before PAYE calculation
    nssf_employee_total = nssf["total_employee"]

    # SHA and housing levy are NOT deducted from taxable income
    taxable_income = gross_salary - nssf_employee_total

    paye = calculate_paye(taxable_income)

    total_deductions = paye + nssf_employee_total + sha + housing_levy + other_deductions
    net_salary = gross_salary - total_deductions

    return {
        "gross_salary": gross_salary,
        "taxable_income": taxable_income,
        "paye": paye,
        "nssf_employee": nssf_employee_total,
        "nssf_employer": nssf["total_employer"],
        "nssf_tier1_employee": nssf["tier1_employee"],
        "nssf_tier2_employee": nssf["tier2_employee"],
        "sha": sha,
        "housing_levy_employee": housing_levy,
        "housing_levy_employer": housing_levy,
        "other_deductions": other_deductions,
        "total_deductions": total_deductions,
        "net_salary": max(net_salary, Decimal("0")),
    }
