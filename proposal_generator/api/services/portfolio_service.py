import openai
from django.conf import settings
import logging
import json
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PortfolioAnalysisService:
    """Service class for AI-powered portfolio project analysis"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
    
    def analyze_project(self, name: str, description: str) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of a portfolio project
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Dictionary containing all analyzed metadata
        """
        try:
            logger.info(f"Starting AI analysis for project: {name}")
            
            # Run all analyses
            metadata = self._extract_metadata(name, description)
            embedding = self._generate_embedding(description)
            summary = self._generate_summary(name, description)
            
            result = {
                'tags': metadata.get('tags', []),
                'technologies': metadata.get('technologies', []),
                'project_type': metadata.get('project_type', ''),
                'complexity_level': metadata.get('complexity_level', ''),
                'ai_summary': summary,
                'embedding_vector': embedding
            }
            
            logger.info(f"Successfully analyzed project: {name}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing project {name}: {str(e)}")
            raise Exception(f"Failed to analyze project: {str(e)}")
    
    def _extract_metadata(self, name: str, description: str) -> Dict[str, Any]:
        """Extract tags, technologies, project type, and complexity using AI"""
        try:
            system_prompt = """You are a technical project analyst. Analyze the given project and extract structured metadata. Return your response as a valid JSON object with these exact keys:

{
  "tags": ["tag1", "tag2", "tag3"],
  "technologies": ["tech1", "tech2", "tech3"],
  "project_type": "web_app|mobile_app|api|desktop_app|game|ai_ml|other",
  "complexity_level": "beginner|intermediate|advanced|expert"
}

Guidelines:
- tags: 5-8 relevant keywords (e.g., "e-commerce", "real-time", "responsive", "authentication")
- technologies: Specific technologies, frameworks, languages mentioned or implied
- project_type: Choose the most appropriate category
- complexity_level: Based on technical scope and features described

Return ONLY the JSON object, no additional text."""

            user_message = f"Project Name: {name}\n\nProject Description: {description}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.3,  # Lower temperature for more consistent structured output
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                metadata = json.loads(result_text)
                
                # Validate required keys
                required_keys = ['tags', 'technologies', 'project_type', 'complexity_level']
                for key in required_keys:
                    if key not in metadata:
                        metadata[key] = [] if key in ['tags', 'technologies'] else ''
                
                return metadata
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {result_text}")
                # Return default structure
                return {
                    'tags': [],
                    'technologies': [],
                    'project_type': 'other',
                    'complexity_level': 'intermediate'
                }
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            raise
    
    def _generate_embedding(self, description: str) -> List[float]:
        """Generate vector embedding for the project description"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=description
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []  # Return empty list on failure
    
    def _generate_summary(self, name: str, description: str) -> str:
        """Generate a concise AI summary of the project"""
        try:
            system_prompt = """Create a concise, professional summary of this project in 2-3 sentences. Focus on:
1. What the project does/solves
2. Key technical highlights
3. Main technologies used

Keep it under 100 words and make it suitable for a portfolio."""
            
            user_message = f"Project: {name}\n\nDescription: {description}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.5,
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary for project: {name}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"A {name} project with comprehensive functionality."
    
    def find_similar_projects(self, job_description: str, projects_with_embeddings: List[Dict], top_k: int = 3) -> List[Dict]:
        """
        Find portfolio projects most similar to a job description
        
        Args:
            job_description: The job description to match against
            projects_with_embeddings: List of projects with their embeddings
            top_k: Number of top matches to return
            
        Returns:
            List of most similar projects with similarity scores
        """
        try:
            # Generate embedding for job description
            job_embedding = self._generate_embedding(job_description)
            
            if not job_embedding:
                return []
            
            # Calculate cosine similarities
            similarities = []
            for project in projects_with_embeddings:
                if not project.get('embedding_vector'):
                    continue
                
                similarity = self._cosine_similarity(job_embedding, project['embedding_vector'])
                similarities.append({
                    'project': project,
                    'similarity_score': similarity
                })
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar projects: {str(e)}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0 