from django.urls import path
from core.presentation.views import login_api, verify_api

urlpatterns = [
    path('login', login_api, name='api-login'),
    path('verify', verify_api, name='api-verify'),
]