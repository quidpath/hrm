"""
Draft/Post state machine views for Job Postings.
Provides save-draft, post (publish job), and auto-save endpoints.
"""
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from ..models import JobPosting


def validate_job_posting_for_posting(job):
    """Validate that a job posting can be published."""
    errors = []
    
    if not job.title:
        errors.append("Job title is required.")
    
    if not job.description:
        errors.append("Job description is required.")
    
    if not job.job_type:
        errors.append("Job type is required.")
    
    if not job.vacancies or job.vacancies <= 0:
        errors.append("Number of vacancies must be greater than zero.")
    
    if not job.deadline:
        errors.append("Application deadline is required.")
    
    if job.deadline < timezone.now().date():
        errors.append("Application deadline must be in the future.")
    
    return errors


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_job_posting_draft(request):
    """
    Save a job posting as draft.
    Allows creating job postings before they go live.
    """
    data = request.data
    job_id = data.get('id')
    corporate_id = request.user.corporate_id
    
    try:
        with transaction.atomic():
            if job_id:
                # Update existing draft
                try:
                    job = JobPosting.objects.get(
                        id=job_id,
                        corporate_id=corporate_id
                    )
                except JobPosting.DoesNotExist:
                    return JsonResponse(
                        {"error": "Job posting not found"},
                        status=404
                    )
                
                # Check if editable
                if job.state not in ['draft', 'on_hold']:
                    return JsonResponse(
                        {"error": f"Cannot edit job in {job.state} state"},
                        status=403
                    )
                
                # Update fields
                if 'title' in data:
                    job.title = data['title']
                if 'description' in data:
                    job.description = data['description']
                if 'requirements' in data:
                    job.requirements = data['requirements']
                if 'job_type' in data:
                    job.job_type = data['job_type']
                if 'location' in data:
                    job.location = data['location']
                if 'salary_range_min' in data:
                    job.salary_range_min = data['salary_range_min']
                if 'salary_range_max' in data:
                    job.salary_range_max = data['salary_range_max']
                if 'vacancies' in data:
                    job.vacancies = data['vacancies']
                if 'deadline' in data:
                    job.deadline = data['deadline']
                if 'department' in data:
                    job.department_id = data['department']
                if 'position' in data:
                    job.position_id = data['position']
                
                if not job.drafted_at:
                    job.drafted_at = timezone.now()
                
                job.save()
            
            else:
                # Create new draft job posting
                job = JobPosting.objects.create(
                    corporate_id=corporate_id,
                    title=data.get('title', 'Untitled Position'),
                    description=data.get('description', ''),
                    requirements=data.get('requirements', ''),
                    job_type=data.get('job_type', 'full_time'),
                    location=data.get('location', ''),
                    salary_range_min=data.get('salary_range_min'),
                    salary_range_max=data.get('salary_range_max'),
                    vacancies=data.get('vacancies', 1),
                    deadline=data.get('deadline'),
                    department_id=data.get('department'),
                    position_id=data.get('position'),
                    state='draft',
                    created_by=request.user.id,
                    drafted_at=timezone.now()
                )
            
            # Return job data
            return JsonResponse({
                "success": True,
                "message": "Job posting draft saved successfully",
                "data": {
                    "id": str(job.id),
                    "title": job.title,
                    "state": job.state,
                    "job_type": job.job_type,
                    "vacancies": job.vacancies,
                    "drafted_at": job.drafted_at.isoformat() if job.drafted_at else None
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
def post_job_posting(request, job_id):
    """
    Post a job posting (publish it and make it live).
    Validates required fields and transitions to open status.
    """
    corporate_id = request.user.corporate_id
    
    try:
        with transaction.atomic():
            try:
                job = JobPosting.objects.select_for_update().get(
                    id=job_id,
                    corporate_id=corporate_id
                )
            except JobPosting.DoesNotExist:
                return JsonResponse(
                    {"error": "Job posting not found"},
                    status=404
                )
            
            # Check if already posted
            if job.state == 'open':
                return JsonResponse(
                    {"error": "Job posting is already live"},
                    status=400
                )
            
            # Validate
            errors = validate_job_posting_for_posting(job)
            if errors:
                return JsonResponse(
                    {"errors": errors},
                    status=400
                )
            
            # Update job
            job.state = 'open'
            job.posted_at = timezone.now()
            job.posted_by = request.user.id
            job.save()
            
            return JsonResponse({
                "success": True,
                "message": "Job posting published successfully",
                "data": {
                    "id": str(job.id),
                    "title": job.title,
                    "state": job.state,
                    "posted_at": job.posted_at.isoformat(),
                    "posted_by": str(job.posted_by)
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
def auto_save_job_posting(request, job_id):
    """
    Auto-save job posting with minimal validation.
    Used for periodic saves while editing.
    """
    corporate_id = request.user.corporate_id
    data = request.data
    
    try:
        try:
            job = JobPosting.objects.get(
                id=job_id,
                corporate_id=corporate_id
            )
        except JobPosting.DoesNotExist:
            return JsonResponse(
                {"error": "Job posting not found"},
                status=404
            )
        
        # Check if editable
        if job.state not in ['draft', 'on_hold']:
            return JsonResponse(
                {"error": "Cannot auto-save published job"},
                status=403
            )
        
        # Update simple fields
        if 'description' in data:
            job.description = data['description']
        if 'requirements' in data:
            job.requirements = data['requirements']
        
        job.save()
        
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
def list_draft_job_postings(request):
    """List all draft job postings for the current corporate."""
    corporate_id = request.user.corporate_id
    
    try:
        drafts = JobPosting.objects.filter(
            corporate_id=corporate_id,
            state='draft'
        ).values(
            'id', 'title', 'job_type', 'location', 'vacancies',
            'deadline', 'drafted_at', 'created_at'
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
def close_job_posting(request, job_id):
    """
    Close a job posting (stop accepting applications).
    """
    corporate_id = request.user.corporate_id
    
    try:
        try:
            job = JobPosting.objects.get(
                id=job_id,
                corporate_id=corporate_id
            )
        except JobPosting.DoesNotExist:
            return JsonResponse(
                {"error": "Job posting not found"},
                status=404
            )
        
        if job.state != 'open':
            return JsonResponse(
                {"error": "Can only close open job postings"},
                status=400
            )
        
        job.state = 'closed'
        job.save()
        
        return JsonResponse({
            "success": True,
            "message": "Job posting closed successfully",
            "data": {
                "id": str(job.id),
                "state": job.state
            }
        })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )
