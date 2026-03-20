from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Interview, JobApplication, JobPosting
from .serializers import InterviewSerializer, JobApplicationSerializer, JobPostingSerializer


@api_view(["GET", "POST"])
def job_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        state = request.GET.get("state")
        qs = JobPosting.objects.filter(corporate_id=cid)
        if state:
            qs = qs.filter(state=state)
        return Response(JobPostingSerializer(qs, many=True).data)
    s = JobPostingSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PATCH"])
def job_detail(request, pk):
    cid = request.corporate_id
    try:
        job = JobPosting.objects.get(pk=pk, corporate_id=cid)
    except JobPosting.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(JobPostingSerializer(job).data)
    s = JobPostingSerializer(job, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def application_list_create(request, job_pk):
    cid = request.corporate_id
    try:
        job = JobPosting.objects.get(pk=job_pk, corporate_id=cid)
    except JobPosting.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)
    if request.method == "GET":
        qs = job.applications.all()
        stage = request.GET.get("stage")
        if stage:
            qs = qs.filter(stage=stage)
        return Response(JobApplicationSerializer(qs, many=True).data)
    s = JobApplicationSerializer(data=request.data)
    if s.is_valid():
        s.save(job=job)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PATCH"])
def application_detail(request, pk):
    cid = request.corporate_id
    try:
        app = JobApplication.objects.get(pk=pk, job__corporate_id=cid)
    except JobApplication.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(JobApplicationSerializer(app).data)
    s = JobApplicationSerializer(app, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["POST"])
def schedule_interview(request, application_pk):
    cid = request.corporate_id
    try:
        app = JobApplication.objects.get(pk=application_pk, job__corporate_id=cid)
    except JobApplication.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    s = InterviewSerializer(data=request.data)
    if s.is_valid():
        s.save(application=app)
        app.stage = "interview"
        app.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)
