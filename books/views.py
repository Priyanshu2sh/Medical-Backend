from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from .models import Books, Descriptions, History, SubDescriptions
from .serializers import BooksSerializer, DescriptionsSerializer

class BooksAPIView(APIView):
    def get(self, request):
        books = Books.objects.all()
        serializer = BooksSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user  
        data = request.data
        print("user",user)

        # code_sets_data = data.pop('code_sets', []) 
        
        data['created_by'] = user.id 
        data['updated_by'] = user.id

         # Ensure 'code_sets' is a list of dictionaries
        if not isinstance(data.get('code_sets', []), list):
            return Response({"error": "code_sets must be a list"}, status=status.HTTP_400_BAD_REQUEST)


        serializer = BooksSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, book_id):
        try:
            book = Books.objects.get(id=book_id)
        except Books.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        previous_data = {
            "name": book.name,
            "author": book.author,  # Track previous author value
            "code_sets": book.code_sets ,
            "version": book.version
            }
        data = request.data.copy()
        if "codeSets" in data:
            data["code_sets"] = data.pop("codeSets")

        # Ensure `code_sets` is correctly formatted
        if "code_sets" in data and isinstance(data["code_sets"], list):
            formatted_code_sets = [{"name": item.get("name")} for item in data["code_sets"]]
            data["code_sets"] = formatted_code_sets

        serializer = BooksSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Store history
            History.objects.create(
                model_name="Books",
                record_id=book.id,
                changes=previous_data
                # updated_by=user
            )

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
        books = Books.objects.all()
        books_data = []

        for book in books:
            descriptions = Descriptions.objects.filter(book=book)

            for description in descriptions:
                sub_descriptions = SubDescriptions.objects.filter(description=description)

                # Fetching sub-description history
                sub_descriptions_data = []
                for sub_desc in sub_descriptions:
                    sub_history = History.objects.filter(model_name="SubDescriptions", record_id=sub_desc.id).order_by('-updated_at')
                    sub_history_data = [
                        {
                            "changes": h.changes,
                            "updated_by": h.updated_by.username if h.updated_by else None,
                            "updated_at": h.updated_at
                        }
                        for h in sub_history
                    ]

                    sub_descriptions_data.append({
                        "id": sub_desc.id,
                        "code": sub_desc.code,
                        "sub_description": sub_desc.sub_description,
                        "history": sub_history_data  # Include sub-description history
                    })

                # Fetching description history
                desc_history = History.objects.filter(model_name="Descriptions", record_id=description.id).order_by('-updated_at')
                desc_history_data = [
                    {
                        "changes": h.changes,
                        "updated_by": h.updated_by.username if h.updated_by else None,
                        "updated_at": h.updated_at
                    }
                    for h in desc_history
                ]

                books_data.append({
                    "book": {"id": book.id, "name": book.name, "version": book.version, "created_by": book.created_by, "updated_by": book.updated_by},
                    'id': description.id,
                    "code": description.code,
                    "description": description.description,
                    "sub_descriptions": sub_descriptions_data,
                    "history": desc_history_data  # Include description history
                })

        return Response(books_data, status=status.HTTP_200_OK)


    def post(self, request):
        user_id = request.data.get("user_id")
        book_id = request.data.get("book")
        code = request.data.get("code")
        description_text = request.data.get("description")
        sub_descriptions_data = request.data.get("sub_descriptions", [])

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            book = Books.objects.get(id=book_id)
        except Books.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        
        description = Descriptions.objects.create(
            book=book, code=code, description=description_text, created_by=user, updated_by=user
        )

        for sub_desc in sub_descriptions_data:
            SubDescriptions.objects.create(
                description=description,
                code=sub_desc.get("code"),
                sub_description=sub_desc.get("sub_description"),
                created_by=user,
                updated_by=user
            )

        return Response({"message": "Book details added successfully"}, status=status.HTTP_201_CREATED)

    def put(self, request):
        description_id = request.data.get("id")
        if not description_id:
            return Response({"error": "Description ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            description = Descriptions.objects.get(id=description_id)
            print("description",description)
        except Descriptions.DoesNotExist:
            return Response({"error": "Description not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.data.get("user_id")
        book_id = request.data.get("book")

        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # If book is provided, update it
        if book_id:
            try:
                book = Books.objects.get(id=book_id)
                description.book = book  # Update book field
            except Books.DoesNotExist:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
            
        previous_data = {
        "book": description.book.id if description.book else None,
        "code": description.code,
        "description": description.description
    }

        description_text = request.data.get("description")
        code = request.data.get("code")
        if description_text:
            description.description = description_text
        if code:
            description.code = code  

        description.updated_by = user
        description.save()

        # Store history
        History.objects.create(
            model_name="Descriptions",
            record_id=description.id,
            changes=previous_data,
            updated_by=user
        )

        # Updating sub-descriptions
        sub_descriptions_data = request.data.get("sub_descriptions", [])
        for sub_desc in sub_descriptions_data:
            sub_id = sub_desc.get("id")
            sub_code = sub_desc.get("code")
            sub_description_text = sub_desc.get("sub_description")

            if sub_id:
                try:
                    sub_description = SubDescriptions.objects.get(id=sub_id, description=description)
                    previous_sub_data = {"code": sub_description.code, "sub_description": sub_description.sub_description}
                    
                    sub_description.code = sub_code
                    sub_description.sub_description = sub_description_text
                    sub_description.updated_by = user
                    sub_description.save()

                    # Store history
                    History.objects.create(
                        model_name="SubDescriptions",
                        record_id=sub_description.id,
                        changes=previous_sub_data,
                        updated_by=user
                    )
                except SubDescriptions.DoesNotExist:
                    return Response({"error": f"Sub-description with ID {sub_id} not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                SubDescriptions.objects.create(
                    description=description, code=sub_code, sub_description=sub_description_text, created_by=user, updated_by=user
                )

        return Response({ "book": description.book.id if description.book else None,
        "code": description.code,
        "description": description.description,
        "sub_descriptions": sub_descriptions_data,"message": "Description and sub-descriptions updated successfully"}, status=status.HTTP_200_OK)

    
    def delete(self, request, code_id):
        try:
            description = Descriptions.objects.get(id=code_id)
        except Descriptions.DoesNotExist:
            return Response({"error": "Description not found"}, status=status.HTTP_404_NOT_FOUND)
        
        description.delete()
        return Response({"message": "Description deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class HistoryAPIView(APIView):
    def get(self, request, model_name, record_id):
        history = History.objects.filter(model_name=model_name, record_id=record_id).order_by('-updated_at')
        history_data = [
            {
                "changes": h.changes,
                "updated_by": h.updated_by.username if h.updated_by else None,
                "updated_at": h.updated_at
            }
            for h in history
        ]
        return Response(history_data, status=status.HTTP_200_OK)