# Django Views/Controllers

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.application.use_cases.login_use_case import LoginUseCase
from core.application.use_cases.verify_token_use_case import VerifyTokenUseCase
from core.application.exceptions import AuthenticationError
from core.infrastructure.adapters.repositories.django_user_repository import DjangoUserRepository
from core.infrastructure.adapters.services.jwt_service import JwtTokenService
from core.infrastructure.adapters.services.hash_service import StandardPasswordHasher # (Assume standard PBKDF2 implementation)

# Dependency Injection Setup (In a larger app, use a DI container like python-dependency-injector)
user_repo = DjangoUserRepository()
token_service = JwtTokenService()
hasher = StandardPasswordHasher()

@csrf_exempt
def login_api(request):
    print("Received request at /api/v1/login")  # Debug log
    if request.method == 'POST':
        data = json.loads(request.body)
        use_case = LoginUseCase(user_repo, hasher, token_service)
        
        try:
            result = use_case.execute(data.get('username'), data.get('password'))
            return JsonResponse(result, status=200)
        except AuthenticationError:
            return JsonResponse({"error": "Unauthorized"}, status=401)
            
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def verify_api(request):
    print("Received request at /api/v1/verify")  # Debug log
    if request.method == 'GET':
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"error": "Missing token"}, status=401)
            
        token = auth_header.split(' ')[1]
        use_case = VerifyTokenUseCase(token_service)
        
        try:
            payload = use_case.execute(token)
            # Add user details to response headers for Nginx to pass to upstream
            response = JsonResponse({"status": "Valid"}, status=200)
            response['X-User-Id'] = str(payload.get('user_id'))
            response['X-User-Roles'] = ",".join(payload.get('roles', []))
            return response
        except AuthenticationError:
            return JsonResponse({"error": "Unauthorized"}, status=401)