from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.storage_service import StorageService
from .services.search_service import SearchService
from .services.gmail_group_service import check_gmail_group_messages, check_gmail_from_settings, GmailService
from rest_framework.pagination import PageNumberPagination
import logging
# import magic

logger = logging.getLogger(__name__)

# class DocumentUploadView(APIView):
#     def post(self, request):
#         if 'file' not in request.FILES:
#             return Response(
#                 {"error": "No file provided"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         file = request.FILES['file']
        
#         # Read file content
#         content = file.read().decode('utf-8')
        
#         # Get file metadata
#         mime = magic.Magic(mime=True)
#         file_type = mime.from_buffer(content)
        
#         metadata = {
#             "file_type": file_type,
#             "file_size": file.size,
#             **request.data
#         }

#         # Store document
#         storage_service = StorageService()
#         storage_service.store_document(file, content, metadata)

#         return Response({"message": "File processed successfully"})

class SearchView(APIView):
    def post(self, request):
        try:
            query = request.data.get('query')
            user_id = request.data.get('user_id')
            conversation_history = request.data.get('conversation_history', [])
            
            if not query or not user_id:
                return Response(
                    {"error": "Both query and user_id are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            search_service = SearchService()
            results = search_service.semantic_search(
                query, 
                user_id, 
                conversation_history=conversation_history
            )
            
            return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DocumentCreateView(APIView):
    def post(self, request):
        if not isinstance(request.data, list):
            return Response(
                {"error": "Request body must be an array of documents"},
                status=status.HTTP_400_BAD_REQUEST
            )

        required_fields = ['id', 'name', 'mimeType', 'text', 'user_id']
        storage_service = StorageService()
        results = []
        
        for document in request.data:
            # Validate required fields
            missing_fields = [field for field in required_fields if field not in document]
            if missing_fields:
                results.append({
                    "id": document.get('id'),
                    "status": "error",
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue

            try:
                created_doc = storage_service.create_document(
                    file_id=document['id'],
                    name=document['name'],
                    mime_type=document['mimeType'],
                    text=document['text'],
                    user_id=document['user_id']
                )
                results.append({
                    "id": document['id'],
                    "status": "success",
                    "mongodb_id": created_doc['_id']
                })
            except Exception as e:
                results.append({
                    "id": document['id'],
                    "status": "error",
                    "error": str(e)
                })

        return Response({
            "message": "Bulk document creation completed",
            "results": results
        })

class DocumentsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserDocumentsView(APIView):
    pagination_class = DocumentsPagination

    def get(self, request, user_id):
        try:
            storage_service = StorageService()
            documents = storage_service.get_user_documents(user_id)
            
            # Filter fields
            filtered_documents = [{
                'id': doc['_id'],
                'name': doc['name'],
                'mimeType': doc['mimeType']
            } for doc in documents]
            
            # Initialize paginator
            paginator = self.pagination_class()
            paginated_documents = paginator.paginate_queryset(filtered_documents, request)
            
            return paginator.get_paginated_response({
                "user_id": user_id,
                "documents": paginated_documents
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GmailCheckView(APIView):
    def post(self, request):
        try:

            messages = check_gmail_from_settings("noreply@groups.google.com", 24)
            
            return Response({
                "message_count": len(messages),
                "messages": messages
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 