from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from django.conf import settings
openai_api_key = "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"
class EmbeddingService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
        openai_api_key=openai_api_key

        )
        self.chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key
        )
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "Summarize the following text concisely:"),
            ("user", "{text}")
        ])

    def generate_embedding(self, text):
        return self.embeddings.embed_query(text)

    def generate_summary(self, text):
        chain = self.summary_prompt | self.chat_model
        response = chain.invoke({"text": text})
        return response.content

    def calculate_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        import numpy as np
        
        # Convert to numpy arrays
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2) 