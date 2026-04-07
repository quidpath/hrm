# hrm_service/core/utils/request_parser.py
import json
import logging

import jwt
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


def get_request_data(request):
    try:
        if request is None:
            return {}

        content_type = request.META.get("CONTENT_TYPE", "")
        method = request.method.upper()

        if "application/json" in content_type:
            return json.loads(request.body or "{}")
        elif "multipart/form-data" in content_type:
            return request.POST.dict()
        elif method == "GET":
            return request.GET.dict()
        elif method == "POST":
            return request.POST.dict()
        elif request.body:
            return json.loads(request.body)

        return {}
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        raise ValueError(f"Error parsing request data: {e}")


def get_clean_data(request):
    """
    Parse request data and extract user/corporate information from JWT token.
    Returns (data, metadata) tuple.
    """
    data = get_request_data(request)
    user_id, corporate_id = resolve_user_from_token(request)

    metadata = {
        "ip_address": get_client_ip(request),
        "user_agent": request.META.get("HTTP_USER_AGENT"),
        "origin": request.META.get("HTTP_ORIGIN"),
        "user_id": user_id,
        "corporate_id": corporate_id,
    }

    return data, metadata


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def resolve_user_from_token(request):
    """
    Extract user_id and corporate_id from JWT token.
    Returns (user_id, corporate_id) tuple.
    """
    try:
        token = request.headers.get("Authorization", "").split("Bearer ")[-1].strip()

        if not token:
            return None, None

        access_token = AccessToken(token)
        user_id = access_token.get("user_id")
        corporate_id = access_token.get("corporate_id")

        return user_id, corporate_id

    except Exception as e:
        logger.warning(f"Token decode error: {e}")
        return None, None
