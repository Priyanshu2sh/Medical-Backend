from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from .models import Books, Descriptions, SubDescriptions
from .serializers import BooksSerializer, DescriptionsSerializer

class BooksAPIView(APIView):
    def get(self, request):
        books = Books.objects.all()
        serializer = BooksSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = BooksSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, book_id):
        book = Books.objects.get(id=book_id)
        if book is None:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BooksSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, book_id):
        book = Books.objects.filter(id=book_id).first()
        if book is None:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        book.delete()
        return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class BookDetailsAPIView(APIView):
    def get(self, request):
        try:
            books = Books.objects.all()
        except Books.DoesNotExist:
            return Response({"error": "No books found"}, status=status.HTTP_404_NOT_FOUND)
        
        books_data = []
        for book in books:
            descriptions = Descriptions.objects.filter(book=book)
            
            for description in descriptions:
                sub_descriptions = SubDescriptions.objects.filter(description=description)
                sub_descriptions_data = [
                    {"code": sub_desc.code, "sub_description": sub_desc.sub_description} 
                    for sub_desc in sub_descriptions
                ]
                books_data.append({
                    "book": {"name": book.name, "version": book.version},
                    'id': description.id,
                    "code": description.code,
                    "description": description.description,
                    "sub_descriptions": sub_descriptions_data
                })
        
        return Response(books_data, status=status.HTTP_200_OK)
        
    def post(self, request):
        book_id = request.data.get("book")
        code = request.data.get("code")
        user_id = request.data.get("user_id")
        description_text = request.data.get("description")
        sub_descriptions_data = request.data.get("sub_descriptions", [])

        # try:
        #     user = User.objects.get(id=user_id)
        # except Books.DoesNotExist:
        #     return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            book = Books.objects.get(id=book_id)
        except Books.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        
        description = Descriptions.objects.create(book=book, code=code, description=description_text)

        for sub_desc in sub_descriptions_data:
            SubDescriptions.objects.create(
                description=description,
                code=sub_desc.get("code"),
                sub_description=sub_desc.get("sub_description")
            )

        return Response({"message": "Book details added successfully"}, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        description_id = request.data.get("id")  # Get the description ID from request body
        if not description_id:
            return Response({"error": "Description ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            description = Descriptions.objects.get(id=description_id)
        except Descriptions.DoesNotExist:
            return Response({"error": "Description not found"}, status=status.HTTP_404_NOT_FOUND)

        # Updating the description text
        description_text = request.data.get("description")
        if description_text:
            description.description = description_text
            description.save()

        # Updating sub-descriptions
        sub_descriptions_data = request.data.get("sub_descriptions", [])

        for sub_desc in sub_descriptions_data:
            sub_id = sub_desc.get("id")  # ID of sub-description
            sub_code = sub_desc.get("code")
            sub_description_text = sub_desc.get("sub_description")

            if sub_id:
                # Update existing sub-description
                try:
                    sub_description = SubDescriptions.objects.get(id=sub_id, description=description)
                    sub_description.code = sub_code
                    sub_description.sub_description = sub_description_text
                    sub_description.save()
                except SubDescriptions.DoesNotExist:
                    return Response({"error": f"Sub-description with ID {sub_id} not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Create a new sub-description if ID is not provided
                SubDescriptions.objects.create(
                    description=description, code=sub_code, sub_description=sub_description_text
                )

        return Response({"message": "Description and sub-descriptions updated successfully"}, status=status.HTTP_200_OK)

    
    def delete(self, request, code_id):
        try:
            description = Descriptions.objects.get(id=code_id)
        except Descriptions.DoesNotExist:
            return Response({"error": "Description not found"}, status=status.HTTP_404_NOT_FOUND)
        
        description.delete()
        return Response({"message": "Description deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
