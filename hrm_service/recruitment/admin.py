from django.contrib import admin
from .models import Interview, JobApplication, JobPosting
admin.site.register(JobPosting)
admin.site.register(JobApplication)
admin.site.register(Interview)
