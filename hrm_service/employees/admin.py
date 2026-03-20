from django.contrib import admin
from .models import Employee, EmergencyContact, EmployeeDocument

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_number", "full_name", "department", "employment_status", "date_joined"]
    list_filter = ["employment_status", "department"]
    search_fields = ["first_name", "last_name", "employee_number", "work_email"]

admin.site.register(EmergencyContact)
admin.site.register(EmployeeDocument)
