import certifi
from django.db import models
from pymongo import MongoClient
from django.conf import settings

class DocumentStore:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://mashood100:Mashood123*@cluster0.rbsqq.mongodb.net/?ssl=true&sslCAFile=/path/to/certifi/cacert.pem",tlsCAFile=certifi.where())
        self.db = self.client["scope_test"]
        self.collection = self.db.documents

    def create_document(self, document_data):
        return self.collection.insert_one(document_data)

    def find_documents(self, query):
        return self.collection.find(query)

    def find_by_vector(self, vector, user_id, limit=5):
        pipeline = [
            {
                "$search": {
                    "index": "vector_index",
                    "knnBeta": {
                        "vector": vector,
                        "path": "embeddings",
                        "k": limit
                    }
                }
            },
            {
                "$match": {
                    "user_id": user_id
                }
            }
        ]
        return list(self.collection.aggregate(pipeline)) 