from django.urls import path
from .views import BookAPIView, AuthorAPIView

urlpatterns = [
    # Authors
    path('api/authors/', AuthorAPIView.as_view(), name='author-list'),
    path('api/authors/<str:id>/', AuthorAPIView.as_view(), name='author-detail'),

    # Books
    path('api/books/', BookAPIView.as_view(), name='book-list'),
    path('api/books/<str:id>/', BookAPIView.as_view(), name='book-detail'),
]
