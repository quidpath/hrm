from rest_framework import serializers
from .models import Interview, JobApplication, JobPosting


class JobPostingSerializer(serializers.ModelSerializer):
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = ["id", "title", "department", "position", "state", "job_type", "location", "description", "requirements", "salary_range_min", "salary_range_max", "vacancies", "deadline", "created_at", "application_count"]
        read_only_fields = ["id", "created_at"]

    def get_application_count(self, obj):
        return obj.applications.count()


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ["id", "interview_type", "scheduled_at", "duration_minutes", "interviewer_ids", "location_or_link", "result", "feedback", "score", "created_at"]
        read_only_fields = ["id", "created_at"]


class JobApplicationSerializer(serializers.ModelSerializer):
    interviews = InterviewSerializer(many=True, read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id", "job", "job_title", "first_name", "last_name", "email", "phone",
            "resume", "cover_letter", "current_employer", "current_salary",
            "expected_salary", "stage", "score", "notes", "assigned_to",
            "created_at", "updated_at", "interviews",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
