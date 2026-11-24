# Django Views/Controllers

import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.application.use_cases.login_use_case import LoginUseCase
from core.application.use_cases.verify_token_use_case import VerifyTokenUseCase
from core.application.use_cases.refresh_token_use_case import RefreshTokenUseCase
from core.application.use_cases.logout_use_case import LogoutUseCase
from core.application.exceptions import AuthenticationError
from core.infrastructure.adapters.repositories.django_user_repository import DjangoUserRepository
from core.infrastructure.adapters.repositories.django_refresh_token_repository import DjangoRefreshTokenRepository
from core.infrastructure.adapters.services.jwt_service import JwtTokenService
from core.infrastructure.adapters.services.hash_service import StandardPasswordHasher # (Assume standard PBKDF2 implementation)

# Dependency Injection Setup (In a larger app, use a DI container like python-dependency-injector)
user_repo = DjangoUserRepository()
refresh_token_repo = DjangoRefreshTokenRepository()
token_service = JwtTokenService()
hasher = StandardPasswordHasher()

logger = logging.getLogger(__name__)

@csrf_exempt
def login_api(request):
    logger.info("Received request at /api/v1/auth/login")

    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)
    use_case = LoginUseCase(user_repo, refresh_token_repo,hasher, token_service)
    
    # No try/except needed! The middleware catches AuthenticationError
    result = use_case.execute(data.get('username'), data.get('password'))
    return JsonResponse(result, status=200)

@csrf_exempt
def verify_api(request):
    logger.info("Received request at /api/v1/auth/verify")

    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    # Verify access token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthenticationError("Missing or invalid Authorization header")
        
    token = auth_header.split(' ')[1]
    use_case = VerifyTokenUseCase(token_service)
    
    payload = use_case.execute(token)

    # Add user details to response headers for Nginx to pass to upstream
    response = JsonResponse({"status": "Valid"}, status=200)
    response['X-User-Id'] = str(payload.get('user_id'))
    response['X-User-Roles'] = ",".join(payload.get('roles', []))
    
    return response

@csrf_exempt
def refresh_api(request):
    logger.info("Received request at /api/v1/auth/refresh")
    
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    data = json.loads(request.body)
    refresh_token = data.get('refresh_token')
    
    use_case = RefreshTokenUseCase(user_repo, refresh_token_repo, token_service)
    
    # Global exception middleware handles AuthenticationError
    result = use_case.execute(refresh_token)
    return JsonResponse(result, status=200)

@csrf_exempt
def logout_api(request):
    logger.info("Received request at /api/v1/auth/logout")

    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    data = json.loads(request.body)
    refresh_token = data.get('refresh_token')
    
    if refresh_token:
        use_case = LogoutUseCase(refresh_token_repo)
        use_case.execute(refresh_token)
        
    return JsonResponse({"message": "Successfully logged out"}, status=200)