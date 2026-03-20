from rest_framework import serializers
from .models import EmergencyContact, Employee, EmployeeDocument


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["id", "name", "relationship", "phone", "email", "is_primary"]
        read_only_fields = ["id"]


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = ["id", "document_type", "title", "file", "expiry_date", "notes", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    position_title = serializers.CharField(source="position.title", read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    documents = EmployeeDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id", "corporate_id", "employee_number", "user_id",
            "first_name", "middle_name", "last_name", "full_name",
            "date_of_birth", "gender", "marital_status", "national_id",
            "kra_pin", "nssf_number", "nhif_number", "personal_email",
            "work_email", "phone", "address", "city", "county", "country", "photo",
            "department", "department_name", "position", "position_title",
            "manager", "date_joined", "probation_end_date", "contract_end_date",
            "employment_status", "bank_name", "bank_account_number", "bank_branch",
            "created_at", "updated_at", "emergency_contacts", "documents",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    position_title = serializers.CharField(source="position.title", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id", "employee_number", "full_name", "work_email", "phone",
            "department_name", "position_title", "employment_status", "date_joined",
        ]
