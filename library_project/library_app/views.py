import json
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .dependencies import get_book_service, get_author_service

#author_service = get_author_service()
#book_service = get_book_service()

def _get_book_service():
    return get_book_service()

def _get_author_service():
    return get_author_service()

def serialize_author(author):
    return {
        "id": author.id,
        "name": author.name,
        "surname": author.surname,
        "date_of_birth": author.date_of_birth
    }

def serialize_book(book):
    return {
        "id": book.id,
        "title": book.title,
        "published_year": book.published_year,
        "author": serialize_author(book.author)
    }

@method_decorator(csrf_exempt, name='dispatch')
class AuthorAPIView(View):
    def get(self, request, id=None):
        if id:
            author = _get_author_service().get_by_id(id)
            if not author:
                return JsonResponse({"error": "Not found"}, status=404)
            return JsonResponse(serialize_author(author), status=200)
        else:
            authors = _get_author_service().get_all()
            return JsonResponse([serialize_author(a) for a in authors], safe=False, status=200)

    def post(self, request):
        data = json.loads(request.body)
        author = _get_author_service().create(
            name=data.get('name'),
            surname=data.get('surname'),
            date_of_birth=data.get('date_of_birth')
        )
        return JsonResponse(serialize_author(author), status=201)

    def put(self, request, id):
        data = json.loads(request.body)
        try:
            author = _get_author_service().update(
                author_id=id,
                name=data.get('name'),
                surname=data.get('surname'),
                date_of_birth=data.get('date_of_birth')
            )
            return JsonResponse(serialize_author(author), status=200)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=404)

    def delete(self, request, id):
        _get_author_service().delete(id)
        return JsonResponse({}, status=204)


@method_decorator(csrf_exempt, name='dispatch')
class BookAPIView(View):
    def get(self, request, id=None):
        if id:
            book = _get_book_service().get_by_id(id)
            if not book:
                return JsonResponse({"error": "Not found"}, status=404)
            return JsonResponse(serialize_book(book), status=200)
        else:
            books = _get_book_service().get_all()
            return JsonResponse([serialize_book(b) for b in books], safe=False, status=200)

    def post(self, request):
        data = json.loads(request.body)
        try:
            book = _get_book_service().create(
                title=data.get('title'),
                published_year=data.get('published_year'),
                author_id=data.get('author_id')
            )
            return JsonResponse(serialize_book(book), status=201)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, id):
        data = json.loads(request.body)
        try:
            book = _get_book_service().update(
                book_id=id,
                title=data.get('title'),
                published_year=data.get('published_year'),
                author_id=data.get('author_id')
            )
            return JsonResponse(serialize_book(book), status=200)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=404)

    def delete(self, request, id):
        _get_book_service().delete(id)
        return JsonResponse({}, status=204)
