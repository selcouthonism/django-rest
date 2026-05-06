import json
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .dependencies import get_book_service

def _get_service():
    return get_book_service()


@method_decorator(csrf_exempt, name='dispatch')
class BookCollectionAPIView(View):
    def get(self, request):
        books = _get_service().get_all_books()
        data = [book.__dict__ for book in books]
        return JsonResponse({"books": data}, status=200)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        try:
            new_book = _get_service().create_book(data)
            return JsonResponse(new_book.__dict__, status=201)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class BookDetailAPIView(View):
    def get(self, request, id):
        try:
            book_id = int(id)
        except ValueError:
            return JsonResponse({"error": "Invalid book ID"}, status=400)

        try:
            book = _get_service().get_book_by_id(book_id)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=404)

        return JsonResponse(book.__dict__, status=200)

    def put(self, request, id):
        try:
            book_id = int(id)
        except ValueError:
            return JsonResponse({"error": "Invalid book ID"}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        try:
            updated_book = _get_service().update_book(book_id, data)
            return JsonResponse(updated_book.__dict__, status=200)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=404)

    def delete(self, request, id):
        try:
            book_id = int(id)
        except ValueError:
            return JsonResponse({"error": "Invalid book ID"}, status=400)

        try:
            _get_service().delete_book(book_id)
            return HttpResponse(status=204)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=404)
