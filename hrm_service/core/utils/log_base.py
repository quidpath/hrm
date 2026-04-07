# hrm_service/core/utils/log_base.py
import logging

logger = logging.getLogger(__name__)


class TransactionLogBase:
    """
    Simple logging utility for HRM service.
    """

    @classmethod
    def log(
        cls,
        transaction_type: str,
        user=None,
        message="",
        state_name="Active",
        extra=None,
        request=None,
    ):
        """
        Log a transaction/event.
        """
        try:
            user_id = user if isinstance(user, str) else (user.get("id") if isinstance(user, dict) else None)
            ip = cls._get_request_ip(request) if request else "0.0.0.0"
            
            log_message = f"[{transaction_type}] {message} | user={user_id} | state={state_name} | ip={ip}"
            
            if state_name == "Completed":
                logger.info(log_message)
            elif state_name == "Failed":
                logger.error(log_message)
            else:
                logger.debug(log_message)
                
            return True
            
        except Exception as e:
            logger.exception(f"[TransactionLog] Failed logging {transaction_type}: {e}")
            return False

    @classmethod
    def _get_request_ip(cls, request):
        """Extract client IP from request"""
        if not request:
            return None
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
