from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hrm_service.core.utils.request_parser import get_clean_data
from hrm_service.core.utils.response import ResponseProvider
from hrm_service.core.utils.log_base import TransactionLogBase
from hrm_service.core.services.registry import ServiceRegistry
from hrm_service.core.utils.pagination import paginate_qs


@csrf_exempt
@require_http_methods(["GET", "POST"])
def employee_list_create(request):
    """
    List all employees or create a new employee.
    GET: Returns list of employees with optional filtering
    POST: Creates a new employee
    """
    data, metadata = get_clean_data(request)
    corporate_id = metadata.get("corporate_id")
    user_id = metadata.get("user_id")
    
    if not corporate_id:
        return ResponseProvider.error_response("Unauthorized", status=401)
    
    registry = ServiceRegistry()
    
    if request.method == "GET":
        # Build query
        q = Q(corporate_id=corporate_id)
        
        # Search filter
        search = data.get("search") or request.GET.get("search", "")
        if search and search.strip():
            q &= (
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_number__icontains=search) |
                Q(work_email__icontains=search)
            )
        
        # Department filter
        dept = data.get("department") or request.GET.get("department")
        if dept:
            q &= Q(department_id=dept)
        
        # Status filter
        status = data.get("status") or request.GET.get("status")
        if status:
            q &= Q(employment_status=status)
        
        try:
            from hrm_service.employees.models import Employee
            qs = Employee.objects.filter(q).order_by("-date_joined")
            page_qs, meta = paginate_qs(qs, request)
            employees = registry.serialize_data(page_qs)
            
            TransactionLogBase.log(
                transaction_type="EMPLOYEE_LIST_SUCCESS",
                user=user_id,
                message=f"Retrieved {meta['count']} employees",
                state_name="Completed",
                request=request
            )
            
            return ResponseProvider.success_response(
                data={"results": employees, **meta},
                status=200
            )
        except Exception as e:
            TransactionLogBase.log(
                transaction_type="EMPLOYEE_LIST_FAILED",
                user=user_id,
                message=str(e),
                state_name="Failed",
                request=request
            )
            return ResponseProvider.error_response(str(e), status=500)
    
    if request.method == "POST":
        # Validate required fields
        required_fields = ["first_name", "last_name", "employee_number", "date_joined"]
        for field in required_fields:
            if field not in data:
                return ResponseProvider.error_response(
                    f"{field.replace('_', ' ').title()} is required",
                    status=400
                )
        
        try:
            # Check for duplicate employee number
            existing = registry.database(
                "employee",
                "filter",
                data={"employee_number": data["employee_number"], "corporate_id": corporate_id}
            )
            if existing:
                return ResponseProvider.error_response(
                    "Employee number already exists",
                    status=400
                )
            
            # Prepare employee data
            employee_data = {
                "corporate_id": corporate_id,
                "employee_number": data["employee_number"],
                "first_name": data["first_name"],
                "middle_name": data.get("middle_name", ""),
                "last_name": data["last_name"],
                "date_of_birth": data.get("date_of_birth"),
                "gender": data.get("gender", ""),
                "marital_status": data.get("marital_status", ""),
                "national_id": data.get("national_id", ""),
                "kra_pin": data.get("kra_pin", ""),
                "nssf_number": data.get("nssf_number", ""),
                "nhif_number": data.get("nhif_number", ""),
                "personal_email": data.get("personal_email", ""),
                "work_email": data.get("work_email", ""),
                "phone": data.get("phone", ""),
                "address": data.get("address", ""),
                "city": data.get("city", ""),
                "county": data.get("county", ""),
                "country": data.get("country", "Kenya"),
                "department_id": data.get("department"),
                "position_id": data.get("position"),
                "manager_id": data.get("manager"),
                "date_joined": data["date_joined"],
                "probation_end_date": data.get("probation_end_date"),
                "contract_end_date": data.get("contract_end_date"),
                "employment_status": data.get("employment_status", "active"),
                "bank_name": data.get("bank_name", ""),
                "bank_account_number": data.get("bank_account_number", ""),
                "bank_branch": data.get("bank_branch", ""),
                "created_by": user_id,
            }
            
            # Create employee
            employee = registry.database("employee", "create", data=employee_data)
            
            TransactionLogBase.log(
                transaction_type="EMPLOYEE_CREATED",
                user=user_id,
                message=f"Employee {employee['employee_number']} created",
                state_name="Completed",
                extra={"employee_id": employee["id"]},
                request=request
            )
            
            return ResponseProvider.success_response(data=employee, status=201)
            
        except Exception as e:
            TransactionLogBase.log(
                transaction_type="EMPLOYEE_CREATE_FAILED",
                user=user_id,
                message=str(e),
                state_name="Failed",
                request=request
            )
            return ResponseProvider.error_response(str(e), status=500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def employee_detail(request, pk):
    """
    Retrieve, update, or delete an employee.
    """
    data, metadata = get_clean_data(request)
    corporate_id = metadata.get("corporate_id")
    user_id = metadata.get("user_id")
    
    if not corporate_id:
        return ResponseProvider.error_response("Unauthorized", status=401)
    
    registry = ServiceRegistry()
    
    try:
        employee = registry.database(
            "employee",
            "get",
            data={"id": pk, "corporate_id": corporate_id}
        )
    except Exception:
        return ResponseProvider.error_response("Employee not found", status=404)
    
    if request.method == "GET":
        return ResponseProvider.success_response(data=employee, status=200)
    
    if request.method == "DELETE":
        try:
            registry.database("employee", "delete", instance_id=pk, soft=True)
            
            TransactionLogBase.log(
                transaction_type="EMPLOYEE_DELETED",
                user=user_id,
                message=f"Employee {pk} deactivated",
                state_name="Completed",
                request=request
            )
            
            return ResponseProvider.success_response(message="Employee deactivated", status=200)
        except Exception as e:
            return ResponseProvider.error_response(str(e), status=500)
    
    if request.method in ["PUT", "PATCH"]:
        try:
            # Prepare update data (only include provided fields)
            update_data = {}
            allowed_fields = [
                "first_name", "middle_name", "last_name", "date_of_birth", "gender",
                "marital_status", "national_id", "kra_pin", "nssf_number", "nhif_number",
                "personal_email", "work_email", "phone", "address", "city", "county",
                "country", "department", "position", "manager", "date_joined",
                "probation_end_date", "contract_end_date", "employment_status",
                "bank_name", "bank_account_number", "bank_branch"
            ]
            
            for field in allowed_fields:
                if field in data:
                    # Handle FK fields
                    if field in ["department", "position", "manager"]:
                        update_data[f"{field}_id"] = data[field]
                    else:
                        update_data[field] = data[field]
            
            if not update_data:
                return ResponseProvider.success_response(data=employee, status=200)
            
            # Update employee
            updated_employee = registry.database(
                "employee",
                "update",
                instance_id=pk,
                data=update_data
            )
            
            TransactionLogBase.log(
                transaction_type="EMPLOYEE_UPDATED",
                user=user_id,
                message=f"Employee {pk} updated",
                state_name="Completed",
                request=request
            )
            
            return ResponseProvider.success_response(data=updated_employee, status=200)
            
        except Exception as e:
            TransactionLogBase.log(
                transaction_type="EMPLOYEE_UPDATE_FAILED",
                user=user_id,
                message=str(e),
                state_name="Failed",
                request=request
            )
            return ResponseProvider.error_response(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def upload_document(request, pk):
    """
    Upload a document for an employee.
    """
    data, metadata = get_clean_data(request)
    corporate_id = metadata.get("corporate_id")
    user_id = metadata.get("user_id")
    
    if not corporate_id:
        return ResponseProvider.error_response("Unauthorized", status=401)
    
    registry = ServiceRegistry()
    
    try:
        # Verify employee exists
        employee = registry.database(
            "employee",
            "get",
            data={"id": pk, "corporate_id": corporate_id}
        )
    except Exception:
        return ResponseProvider.error_response("Employee not found", status=404)
    
    try:
        # Create document
        document_data = {
            "employee_id": pk,
            "document_type": data.get("document_type"),
            "title": data.get("title"),
            "file": request.FILES.get("file"),
            "expiry_date": data.get("expiry_date"),
            "notes": data.get("notes", ""),
        }
        
        document = registry.database("employeedocument", "create", data=document_data)
        
        TransactionLogBase.log(
            transaction_type="EMPLOYEE_DOCUMENT_UPLOADED",
            user=user_id,
            message=f"Document uploaded for employee {pk}",
            state_name="Completed",
            request=request
        )
        
        return ResponseProvider.success_response(data=document, status=201)
        
    except Exception as e:
        return ResponseProvider.error_response(str(e), status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_emergency_contact(request, pk):
    """
    Add an emergency contact for an employee.
    """
    data, metadata = get_clean_data(request)
    corporate_id = metadata.get("corporate_id")
    user_id = metadata.get("user_id")
    
    if not corporate_id:
        return ResponseProvider.error_response("Unauthorized", status=401)
    
    registry = ServiceRegistry()
    
    try:
        # Verify employee exists
        employee = registry.database(
            "employee",
            "get",
            data={"id": pk, "corporate_id": corporate_id}
        )
    except Exception:
        return ResponseProvider.error_response("Employee not found", status=404)
    
    try:
        # Create emergency contact
        contact_data = {
            "employee_id": pk,
            "name": data.get("name"),
            "relationship": data.get("relationship"),
            "phone": data.get("phone"),
            "email": data.get("email", ""),
            "is_primary": data.get("is_primary", False),
        }
        
        contact = registry.database("emergencycontact", "create", data=contact_data)
        
        TransactionLogBase.log(
            transaction_type="EMERGENCY_CONTACT_ADDED",
            user=user_id,
            message=f"Emergency contact added for employee {pk}",
            state_name="Completed",
            request=request
        )
        
        return ResponseProvider.success_response(data=contact, status=201)
        
    except Exception as e:
        return ResponseProvider.error_response(str(e), status=500)

