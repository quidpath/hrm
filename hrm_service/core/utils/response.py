# hrm_service/core/utils/response.py
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.core.files.base import File
from django.db import models
from django.http import JsonResponse


def comprehensive_serializer(obj):
    """
    Comprehensive serializer that handles all common Django/Python objects
    """
    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, models.Model):
        result = {}
        for field in obj._meta.fields:
            field_name = field.name
            field_value = getattr(obj, field_name)

            if isinstance(field_value, models.Model):
                result[f"{field_name}_id"] = str(field_value.pk) if field_value.pk else None
            elif isinstance(field_value, (datetime, date)):
                result[field_name] = field_value.isoformat() if field_value else None
            elif isinstance(field_value, UUID):
                result[field_name] = str(field_value)
            elif isinstance(field_value, Decimal):
                result[field_name] = float(field_value)
            elif isinstance(field_value, File):
                result[field_name] = field_value.url if field_value else None
            else:
                result[field_name] = field_value

        return result

    if isinstance(obj, File):
        return obj.url if obj else None

    if isinstance(obj, (list, tuple)):
        return [comprehensive_serializer(item) for item in obj]

    if isinstance(obj, dict):
        return {key: comprehensive_serializer(value) for key, value in obj.items()}

    if isinstance(obj, set):
        return list(obj)

    return str(obj)


class ResponseProvider:
    """Provides standardized JSON responses."""

    @staticmethod
    def success_response(data=None, message=None, status=200):
        """Return a success JsonResponse."""
        payload = {"success": True}
        if data is not None:
            payload["data"] = data
        if message is not None:
            payload["message"] = message
        try:
            serialized = json.loads(json.dumps(payload, default=comprehensive_serializer))
            return JsonResponse(serialized, status=status)
        except Exception:
            return JsonResponse({"success": True, "message": message or "OK"}, status=status)

    @staticmethod
    def error_response(message, status=400, data=None):
        """Return an error JsonResponse."""
        payload = {"success": False, "message": message}
        if data is not None:
            payload["data"] = data
        return JsonResponse(payload, status=status)

    @staticmethod
    def method_not_allowed(allowed_methods):
        """Return 405 Method Not Allowed."""
        return JsonResponse(
            {
                "success": False,
                "message": "Method not allowed",
                "allowed": allowed_methods,
            },
            status=405,
        )
