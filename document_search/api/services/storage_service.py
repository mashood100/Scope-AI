import datetime

import certifi
from pymongo import MongoClient
from ..models import DocumentStore
from .embedding_service import EmbeddingService

class StorageService:
    def __init__(self):
        self.document_store = DocumentStore()
        self.embedding_service = EmbeddingService()
        self.client = MongoClient("mongodb+srv://mashood100:Mashood123*@cluster0.rbsqq.mongodb.net/?ssl=true&sslCAFile=/path/to/certifi/cacert.pem",tlsCAFile=certifi.where())
        self.db = self.client["scope_test"]
    def store_document(self, file_data, content, metadata):
        # Generate embeddings and summary
        embeddings = self.embedding_service.generate_embedding(content)

        document = {
            "filename": file_data.name,
            "content": content,
            "embeddings": embeddings,

        }

        try:
            result = self.document_store.create_document(document)
        except Exception as e:
            print(f"Error storing document: {e}")  # Add error logging
            return None  # Return None or handle the error as needed
        return str(result.inserted_id)  # Convert ObjectId to string

    def create_document(self, file_id, name, mime_type, text, user_id):
        # Generate embeddings and summary
        embeddings = self.embedding_service.generate_embedding(text)

        # Create document entry
        document = {
            "_id": file_id,
            "name": name,
            "mimeType": mime_type,
            "content": text, 
            "embeddings": embeddings,
            "user_id": user_id,
          
        }

        try:
            result = self.document_store.create_document(document)
            return result.inserted_id 
        except Exception as e:
            print(f"Error creating document: {e}")
            return None 

    def get_user_documents(self, user_id):
        documents = self.db.documents.find({"user_id": user_id})
        # Convert MongoDB cursor to list and serialize ObjectId
        return [{**doc, "_id": str(doc["_id"])} for doc in documents] 