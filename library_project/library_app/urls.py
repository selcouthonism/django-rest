from django.urls import path
from .views import BookCollectionAPIView, BookDetailAPIView

urlpatterns = [
    path('books/', BookCollectionAPIView.as_view(), name='book-collection'),
    path('books/<int:id>/', BookDetailAPIView.as_view(), name='book-detail'),
]
