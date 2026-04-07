"""
Draft/Post state machine views for Payroll Runs.
Provides save-draft, approve (post), and auto-save endpoints.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from ..models import PayrollRun, Payslip


def validate_payroll_run_for_posting(payroll_run):
    """Validate that a payroll run can be approved/posted."""
    errors = []
    
    if not payroll_run.payslips.exists():
        errors.append("Cannot approve payroll with no payslips.")
    
    if not payroll_run.period_start or not payroll_run.period_end:
        errors.append("Payroll period dates are required.")
    
    if payroll_run.period_start > payroll_run.period_end:
        errors.append("Period start date must be before period end date.")
    
    if not payroll_run.pay_date:
        errors.append("Pay date is required before approval.")
    
    if payroll_run.total_net <= 0:
        errors.append("Total net pay must be greater than zero.")
    
    return errors


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_payroll_run_draft(request):
    """
    Save a payroll run as draft.
    Allows building payroll before final approval.
    """
    data = request.data
    payroll_id = data.get('id')
    corporate_id = request.user.corporate_id
    
    try:
        with transaction.atomic():
            if payroll_id:
                # Update existing draft
                try:
                    payroll = PayrollRun.objects.get(
                        id=payroll_id,
                        corporate_id=corporate_id
                    )
                except PayrollRun.DoesNotExist:
                    return JsonResponse(
                        {"error": "Payroll run not found"},
                        status=404
                    )
                
                # Check if editable
                if payroll.state not in ['draft', 'calculating', 'review']:
                    return JsonResponse(
                        {"error": f"Cannot edit payroll in {payroll.state} state"},
                        status=403
                    )
                
                # Update fields
                if 'name' in data:
                    payroll.name = data['name']
                if 'period_start' in data:
                    payroll.period_start = data['period_start']
                if 'period_end' in data:
                    payroll.period_end = data['period_end']
                if 'pay_date' in data:
                    payroll.pay_date = data['pay_date']
                if 'notes' in data:
                    payroll.notes = data['notes']
                
                if not payroll.drafted_at:
                    payroll.drafted_at = timezone.now()
                
                payroll.save()
            
            else:
                # Create new draft payroll
                payroll = PayrollRun.objects.create(
                    corporate_id=corporate_id,
                    name=data.get('name', f"Payroll {timezone.now().strftime('%B %Y')}"),
                    period_start=data['period_start'],
                    period_end=data['period_end'],
                    pay_date=data.get('pay_date'),
                    state='draft',
                    created_by=request.user.id,
                    drafted_at=timezone.now(),
                    notes=data.get('notes', '')
                )
            
            # Return payroll data
            return JsonResponse({
                "success": True,
                "message": "Payroll draft saved successfully",
                "data": {
                    "id": str(payroll.id),
                    "name": payroll.name,
                    "state": payroll.state,
                    "period_start": payroll.period_start.isoformat(),
                    "period_end": payroll.period_end.isoformat(),
                    "pay_date": payroll.pay_date.isoformat() if payroll.pay_date else None,
                    "total_gross": str(payroll.total_gross),
                    "total_net": str(payroll.total_net),
                    "drafted_at": payroll.drafted_at.isoformat() if payroll.drafted_at else None
                }
            })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_payroll_run(request, payroll_id):
    """
    Approve/post a payroll run (transition from review to approved).
    Validates all payslips and marks as ready for payment.
    """
    corporate_id = request.user.corporate_id
    
    try:
        with transaction.atomic():
            try:
                payroll = PayrollRun.objects.select_for_update().get(
                    id=payroll_id,
                    corporate_id=corporate_id
                )
            except PayrollRun.DoesNotExist:
                return JsonResponse(
                    {"error": "Payroll run not found"},
                    status=404
                )
            
            # Check if already approved
            if payroll.state == 'approved':
                return JsonResponse(
                    {"error": "Payroll is already approved"},
                    status=400
                )
            
            # Validate
            errors = validate_payroll_run_for_posting(payroll)
            if errors:
                return JsonResponse(
                    {"errors": errors},
                    status=400
                )
            
            # Update payroll
            payroll.state = 'approved'
            payroll.posted_at = timezone.now()
            payroll.posted_by = request.user.id
            payroll.approved_by = request.user.id
            payroll.save()
            
            return JsonResponse({
                "success": True,
                "message": "Payroll approved successfully",
                "data": {
                    "id": str(payroll.id),
                    "name": payroll.name,
                    "state": payroll.state,
                    "total_net": str(payroll.total_net),
                    "posted_at": payroll.posted_at.isoformat(),
                    "posted_by": str(payroll.posted_by),
                    "approved_by": str(payroll.approved_by)
                }
            })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def auto_save_payroll_run(request, payroll_id):
    """
    Auto-save payroll run with minimal validation.
    Used for periodic saves while building payroll.
    """
    corporate_id = request.user.corporate_id
    data = request.data
    
    try:
        try:
            payroll = PayrollRun.objects.get(
                id=payroll_id,
                corporate_id=corporate_id
            )
        except PayrollRun.DoesNotExist:
            return JsonResponse(
                {"error": "Payroll run not found"},
                status=404
            )
        
        # Check if editable
        if payroll.state not in ['draft', 'calculating', 'review']:
            return JsonResponse(
                {"error": "Cannot auto-save approved payroll"},
                status=403
            )
        
        # Update simple fields
        if 'notes' in data:
            payroll.notes = data['notes']
        if 'pay_date' in data:
            payroll.pay_date = data['pay_date']
        
        payroll.save()
        
        return JsonResponse({
            "success": True,
            "message": "Auto-save successful"
        })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_draft_payroll_runs(request):
    """List all draft payroll runs for the current corporate."""
    corporate_id = request.user.corporate_id
    
    try:
        drafts = PayrollRun.objects.filter(
            corporate_id=corporate_id,
            state__in=['draft', 'calculating', 'review']
        ).values(
            'id', 'name', 'state', 'period_start', 'period_end',
            'total_gross', 'total_net', 'drafted_at', 'created_at'
        )
        
        return JsonResponse({
            "success": True,
            "data": list(drafts)
        })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_payroll(request, payroll_id):
    """
    Calculate payslips for all employees in the payroll period.
    Transitions state from draft to calculating to review.
    """
    corporate_id = request.user.corporate_id
    
    try:
        with transaction.atomic():
            try:
                payroll = PayrollRun.objects.select_for_update().get(
                    id=payroll_id,
                    corporate_id=corporate_id
                )
            except PayrollRun.DoesNotExist:
                return JsonResponse(
                    {"error": "Payroll run not found"},
                    status=404
                )
            
            if payroll.state != 'draft':
                return JsonResponse(
                    {"error": "Can only calculate draft payroll"},
                    status=400
                )
            
            # Mark as calculating
            payroll.state = 'calculating'
            payroll.save()
            
            # TODO: Implement actual payroll calculation logic
            # This would fetch employees, calculate salaries, taxes, etc.
            # For now, just transition to review state
            
            payroll.state = 'review'
            payroll.save()
            
            return JsonResponse({
                "success": True,
                "message": "Payroll calculated successfully",
                "data": {
                    "id": str(payroll.id),
                    "state": payroll.state
                }
            })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )
