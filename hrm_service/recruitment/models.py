from django.db import models

from hrm_service.core.base_models import BaseModel


class JobPosting(BaseModel):
    STATES = [("draft", "Draft"), ("open", "Open"), ("closed", "Closed"), ("on_hold", "On Hold")]
    JOB_TYPES = [("full_time", "Full Time"), ("part_time", "Part Time"), ("contract", "Contract"), ("intern", "Internship")]

    corporate_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey("organization.Department", on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey("organization.Position", on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATES, default="draft")
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default="full_time")
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    salary_range_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_range_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    vacancies = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True)
    created_by = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.title


class JobApplication(BaseModel):
    STAGES = [
        ("applied", "Applied"), ("screening", "Screening"), ("shortlisted", "Shortlisted"),
        ("interview", "Interview Scheduled"), ("interviewed", "Interviewed"),
        ("offer", "Offer Sent"), ("hired", "Hired"), ("rejected", "Rejected"), ("withdrawn", "Withdrawn"),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applications")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    resume = models.FileField(upload_to="recruitment/resumes/", null=True, blank=True)
    cover_letter = models.TextField(blank=True)
    current_employer = models.CharField(max_length=200, blank=True)
    current_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stage = models.CharField(max_length=20, choices=STAGES, default="applied")
    score = models.PositiveIntegerField(default=0, help_text="0–100 candidate score")
    notes = models.TextField(blank=True)
    assigned_to = models.UUIDField(null=True, blank=True, help_text="Recruiter user_id")

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.job.title}"


class Interview(BaseModel):
    TYPES = [("phone", "Phone Screen"), ("video", "Video Call"), ("in_person", "In-Person"), ("panel", "Panel")]
    RESULTS = [("pending", "Pending"), ("passed", "Passed"), ("failed", "Failed"), ("no_show", "No Show")]

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="interviews")
    interview_type = models.CharField(max_length=20, choices=TYPES, default="video")
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    interviewer_ids = models.JSONField(default=list, help_text="List of interviewer user_ids")
    location_or_link = models.CharField(max_length=300, blank=True)
    result = models.CharField(max_length=20, choices=RESULTS, default="pending")
    feedback = models.TextField(blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
