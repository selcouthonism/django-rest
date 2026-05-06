from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .dependencies import get_book_service

service = get_book_service()

@method_decorator(csrf_exempt, name='dispatch')
class ApiRootView(View):
    def get(self, request):        
        message = 'Test API Root View'         
        return JsonResponse({"message": message}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class BookCollectionAPIView(View):
    def get(self, request):
        books = service.get_all_books()
        data = [book.__dict__ for book in books]
        return JsonResponse({"books": data}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class BookDetailAPIView(View):
    def get(self, request, id):
        book = service.get_book_by_id(id)
        if not book:
            return JsonResponse({"error": "Book not found"}, status=404)
        return JsonResponse(book.__dict__, status=200)

    def post(self, request, id=None):
        try:
            serializer = BookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_book = service.create_book(serializer.validated_data)
            serializer = BookSerializer(new_book)
            return JsonResponse(serializer.data, status=201)
        except Exception as e:
            return JsonResponse({"error": "Invalid payload"}, status=400)

    def put(self, request, id):
        try:
            serializer = BookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_book = service.update_book(id, serializer.validated_data)
            serializer = BookSerializer(new_book)
            return JsonResponse(serializer.data, status=200)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=404) # Not Found
        except Exception as e:
            return JsonResponse({"error": "Invalid payload"}, status=400)

    def delete(self, request, id):
        try:
            service.delete_book(id)
            return JsonResponse({}, status=204)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class BookView(View):
    def get(self, request, id=None):
        if id:
            try:
                book = service.get_book_by_id(id)
                return JsonResponse(book.__dict__, status=200)
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=404)
        else:
            books = service.get_all_books()
            books_data = [book.__dict__ for book in books]
            return JsonResponse(books_data, safe=False, status=200)
    