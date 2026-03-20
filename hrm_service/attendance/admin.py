from django.contrib import admin
from .models import AttendancePolicy, AttendanceRecord
admin.site.register(AttendancePolicy)
admin.site.register(AttendanceRecord)
