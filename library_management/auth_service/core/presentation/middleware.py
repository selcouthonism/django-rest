import logging
from django.http import JsonResponse
from core.application.exceptions import AuthenticationError, ValidationError, BaseApplicationError

logger = logging.getLogger(__name__)

class GlobalExceptionMiddleware:
    """This acts as the bridge between pure Python exceptions and Django's HTTP responses."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Continue processing the request
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Django automatically calls this method if a view raises an exception.
        """
        # 1. Handle Known Application Errors
        if isinstance(exception, AuthenticationError):
            return JsonResponse({"error": str(exception) or "Unauthorized"}, status=401)
            
        if isinstance(exception, ValidationError):
            return JsonResponse({"error": str(exception)}, status=400)
        
        # 2. Handle other known base domain errors (fallback)
        if isinstance(exception, BaseApplicationError):
            return JsonResponse({"error": str(exception)}, status=400)

        # 3. Handle Unexpected System Errors (Catch-all)
        # Log the full stack trace for debugging without exposing it to the user
        logger.error(f"Unhandled system exception: {str(exception)}", exc_info=True)
        return JsonResponse({"error": "An unexpected internal server error occurred."}, status=500)