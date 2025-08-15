from .embedding_service import EmbeddingService
from ..models import DocumentStore
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from django.conf import settings
from typing import List, Tuple, Dict, Any
from bson import ObjectId

class SearchService:
    def __init__(self):
        # Initialize the SearchService with DocumentStore and EmbeddingService
        # and set up the chat model with the specified API key and parameters.
        self.document_store = DocumentStore()
        self.embedding_service = EmbeddingService()
        self.chat_model = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )

    def semantic_search(self, query: str, user_id: str, conversation_history: List[Dict] = None, limit: int = 5) -> Dict:
        # Perform a semantic search for the given query and user_id,
        # generating an embedding for the query and retrieving relevant documents.
        query_embedding = self.embedding_service.generate_embedding(query)
        documents = self._get_and_process_documents(user_id, query_embedding, limit)
        context = self._build_context(documents)
        return self._generate_ai_response(query, context, conversation_history, documents)

    def _get_and_process_documents(self, user_id: str, query_embedding: List[float], limit: int) -> List[Tuple[Dict, Dict]]:
        # Retrieve documents for the specified user_id, process them to update
        # any missing vectors, and calculate similarities to the query embedding.
        all_docs = list(self.document_store.collection.find({"user_id": user_id}))
        self._update_missing_vectors(all_docs)
        
        results_list = self._calculate_similarities(all_docs, query_embedding)
        top_results = sorted(results_list, key=lambda x: x[1], reverse=True)[:limit]
        
        return [self._prepare_document_context(doc, similarity) for doc, similarity in top_results]

    def _update_missing_vectors(self, documents: List[Dict]) -> None:
        # Update documents that are missing their vector representations
        # by generating embeddings for their content.
        docs_without_vectors = [doc for doc in documents if not doc.get('vector')]
        if not docs_without_vectors:
            return

        updates = [
            {
                "doc_id": doc["_id"],
                "vector": self.embedding_service.generate_embedding(doc.get('content', ''))
            }
            for doc in docs_without_vectors
        ]

        # Bulk update for better performance
        for update in updates:
            self.document_store.collection.update_one(
                {"_id": update["doc_id"]},
                {"$set": {"vector": update["vector"]}}
            )

    def _calculate_similarities(self, documents: List[Dict], query_embedding: List[float]) -> List[Tuple[Dict, float]]:
        # Calculate the similarity scores between the query embedding and
        # the vectors of the provided documents.
        return [
            (doc, self.embedding_service.calculate_similarity(query_embedding, doc['vector']))
            for doc in documents
            if doc.get('vector')
        ]

    def _prepare_document_context(self, doc: Dict, similarity: float) -> Tuple[Dict, Dict]:
        # Prepare the full document context and a simplified version
        # containing only essential information for the response.
        full_doc = {
            'content': doc.get('content', ''),
            'type': doc.get('metadata', {}).get('type', 'general'),
            'name': doc.get('name', ''),
            'metadata': doc.get('metadata', {}),
            'similarity_score': similarity
        }
        
        simplified_doc = {
            'id': str(doc.get('_id')),
            'name': doc.get('name', '')
        }
        
        return full_doc, simplified_doc

    def _build_context(self, context_docs: List[Tuple[Dict, Dict]]) -> str:
        # Build a string context from the provided documents,
        # summarizing their types, content, and similarity scores.
        context_parts = ["Available documents:"]
        
        for i, (full_doc, _) in enumerate(context_docs, 1):
            context_parts.extend([
                f"\nDocument {i}:",
                f"Type: {full_doc['type']}",
                f"Content: {full_doc['content']}",
                f"Similarity Score: {full_doc['similarity_score']:.4f}"
            ])
            
        return "\n".join(context_parts)

    def _generate_ai_response(self, query: str, context: str, conversation_history: List[Dict], context_docs: List[Tuple[Dict, Dict]]) -> Dict:
        # Generate a response from the AI model based on the query,
        # context, and conversation history, returning the AI's response
        # and relevant documents.
        system_prompt = """You are a helpful assistant analyzing documents. Follow these guidelines:
1. For specific queries (numbers, dates, names), extract and quote the exact information
2. For topic-based queries, synthesize information from multiple documents
3. If the answer isn't in the documents, clearly state that
4. Always cite which document(s) you used in your answer
Maintain a professional and helpful tone."""

        messages = self._prepare_messages(conversation_history, system_prompt, context, query)
        response = self.chat_model.invoke(messages)

        return {
            "ai_response": response.content,
            "relevant_documents": [doc[1] for doc in context_docs],
            "conversation_history": (conversation_history or []) + [
                {"role": "assistant", "content": response.content}
            ]
        }

    def _prepare_messages(self, conversation_history: List[Dict], system_prompt: str, context: str, query: str) -> List:
        # Prepare the messages for the AI model, including the system prompt,
        # context, and the user's query, along with the conversation history.
        messages = []
        
        if conversation_history:
            messages.extend(
                HumanMessage(content=msg["content"]) if msg["role"] == "user"
                else AIMessage(content=msg["content"])
                for msg in conversation_history
            )

        messages.extend([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context: {context}\n\nQuestion: {query}")
        ])
        
        return messages 