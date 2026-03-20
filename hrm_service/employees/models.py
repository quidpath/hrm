from django.db import models

from hrm_service.core.base_models import BaseModel


class Employee(BaseModel):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Other")]
    EMPLOYMENT_STATUSES = [
        ("active", "Active"), ("on_leave", "On Leave"), ("probation", "Probation"),
        ("notice_period", "Notice Period"), ("terminated", "Terminated"),
    ]
    MARITAL_STATUSES = [("single", "Single"), ("married", "Married"), ("divorced", "Divorced"), ("widowed", "Widowed")]

    corporate_id = models.UUIDField(db_index=True)
    employee_number = models.CharField(max_length=50, db_index=True)
    user_id = models.UUIDField(null=True, blank=True, help_text="Linked user account in ERP backend")
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUSES, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    kra_pin = models.CharField(max_length=20, blank=True, help_text="Kenya Revenue Authority PIN")
    nssf_number = models.CharField(max_length=20, blank=True)
    nhif_number = models.CharField(max_length=20, blank=True)
    personal_email = models.EmailField(blank=True)
    work_email = models.EmailField(blank=True, db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Kenya")
    photo = models.ImageField(upload_to="employees/photos/", null=True, blank=True)
    department = models.ForeignKey("organization.Department", on_delete=models.SET_NULL, null=True, blank=True, related_name="employees")
    position = models.ForeignKey("organization.Position", on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="direct_reports")
    date_joined = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUSES, default="active")
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        unique_together = [("corporate_id", "employee_number")]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_number})"

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)


class EmergencyContact(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="emergency_contacts")
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=False)


class EmployeeDocument(BaseModel):
    DOC_TYPES = [
        ("national_id", "National ID"), ("passport", "Passport"), ("contract", "Employment Contract"),
        ("certificate", "Certificate"), ("academic", "Academic Qualification"),
        ("medical", "Medical Record"), ("other", "Other"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=30, choices=DOC_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="employees/documents/")
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
