import certifi
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MongoPortfolioService:
    """Service class for managing portfolio projects in MongoDB"""
    
    def __init__(self):
        # Initialize MongoDB connection (using same connection string as document_search)
        self.client = MongoClient(
            "mongodb+srv://mashood100:Mashood123*@cluster0.rbsqq.mongodb.net/?ssl=true&sslCAFile=/path/to/certifi/cacert.pem",
            tlsCAFile=certifi.where()
        )
        self.db = self.client["scope_test"]
        self.portfolio_collection = self.db.portfolio_projects
    
    def create_portfolio_project(self, project_data):
        """
        Create a new portfolio project in MongoDB
        
        Args:
            project_data: Dict containing project information
                - name: str
                - description: str
                - user_id: str
                - tags: list (AI-generated)
                - ai_summary: str (AI-generated)
                - technologies: list (AI-generated)
                - project_type: str (AI-generated)
                - complexity_level: str (AI-generated)
                - embedding_vector: list (AI-generated)
                - github_url: str (optional)
                - live_url: str (optional)
                - app_store_url: str (optional)
                - images: list (optional)
                - is_featured: bool (optional)
                
        Returns:
            str: Inserted document ID
        """
        try:
            # Prepare document with timestamps
            document = {
                "name": project_data.get("name"),
                "description": project_data.get("description"),
                "user_id": project_data.get("user_id"),
                "tags": project_data.get("tags", []),
                "ai_summary": project_data.get("ai_summary"),
                "technologies": project_data.get("technologies", []),
                "project_type": project_data.get("project_type"),
                "complexity_level": project_data.get("complexity_level"),
                "embedding_vector": project_data.get("embedding_vector", []),
                "github_url": project_data.get("github_url"),
                "live_url": project_data.get("live_url"),
                "app_store_url": project_data.get("app_store_url"),
                "images": project_data.get("images", []),
                "is_featured": project_data.get("is_featured", False),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into MongoDB
            result = self.portfolio_collection.insert_one(document)
            
            logger.info(f"Created portfolio project in MongoDB with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating portfolio project in MongoDB: {str(e)}")
            raise Exception(f"Failed to create portfolio project: {str(e)}")
    
    def get_user_portfolio_projects(self, user_id, page=1, page_size=10, project_type=None, is_featured=None):
        """
        Get paginated portfolio projects for a specific user
        
        Args:
            user_id: str
            page: int (1-based)
            page_size: int
            project_type: str (optional filter)
            is_featured: bool (optional filter)
            
        Returns:
            dict: Contains projects list, total count, and pagination info
        """
        try:
            # Build query
            query = {"user_id": user_id}
            
            if project_type:
                query["project_type"] = project_type
                
            if is_featured is not None:
                query["is_featured"] = is_featured
            
            # Calculate skip value for pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total_count = self.portfolio_collection.count_documents(query)
            
            # Get projects with pagination, sorted by created_at descending
            cursor = self.portfolio_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            
            # Convert cursor to list and serialize ObjectIds
            projects = []
            for project in cursor:
                projects.append({
                    "id": str(project["_id"]),
                    "name": project.get("name"),
                    "description": project.get("description"),
                    "user_id": project.get("user_id"),
                    "tags": project.get("tags", []),
                    "ai_summary": project.get("ai_summary"),
                    "technologies": project.get("technologies", []),
                    "project_type": project.get("project_type"),
                    "complexity_level": project.get("complexity_level"),
                    "embedding_vector": project.get("embedding_vector", []),
                    "github_url": project.get("github_url"),
                    "live_url": project.get("live_url"),
                    "app_store_url": project.get("app_store_url"),
                    "images": project.get("images", []),
                    "is_featured": project.get("is_featured", False),
                    "created_at": project.get("created_at"),
                    "updated_at": project.get("updated_at")
                })
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            logger.info(f"Retrieved {len(projects)} portfolio projects for user {user_id} (page {page})")
            
            return {
                "projects": projects,
                "pagination": {
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                    "has_next": has_next,
                    "has_previous": has_previous
                }
            }
            
        except Exception as e:
            logger.error(f"Error retrieving user portfolio projects: {str(e)}")
            raise Exception(f"Failed to retrieve portfolio projects: {str(e)}")
    
    def get_portfolio_project_by_id(self, project_id):
        """
        Get a specific portfolio project by ID
        
        Args:
            project_id: str
            
        Returns:
            dict: Project data or None if not found
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(project_id)
            
            # Find the project
            project = self.portfolio_collection.find_one({"_id": object_id})
            
            if not project:
                return None
            
            # Convert ObjectId to string for JSON serialization
            project_data = {
                "id": str(project["_id"]),
                "name": project.get("name"),
                "description": project.get("description"),
                "user_id": project.get("user_id"),
                "tags": project.get("tags", []),
                "ai_summary": project.get("ai_summary"),
                "technologies": project.get("technologies", []),
                "project_type": project.get("project_type"),
                "complexity_level": project.get("complexity_level"),
                "embedding_vector": project.get("embedding_vector", []),
                "github_url": project.get("github_url"),
                "live_url": project.get("live_url"),
                "app_store_url": project.get("app_store_url"),
                "images": project.get("images", []),
                "is_featured": project.get("is_featured", False),
                "created_at": project.get("created_at"),
                "updated_at": project.get("updated_at")
            }
            
            logger.info(f"Retrieved portfolio project {project_id}")
            return project_data
            
        except Exception as e:
            logger.error(f"Error retrieving portfolio project {project_id}: {str(e)}")
            raise Exception(f"Failed to retrieve portfolio project: {str(e)}")
    
    def update_portfolio_project(self, project_id, update_data):
        """
        Update a portfolio project
        
        Args:
            project_id: str
            update_data: dict containing fields to update
            
        Returns:
            bool: True if updated successfully
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(project_id)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update the project
            result = self.portfolio_collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                logger.warning(f"No portfolio project found with ID {project_id}")
                return False
            
            logger.info(f"Updated portfolio project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating portfolio project {project_id}: {str(e)}")
            raise Exception(f"Failed to update portfolio project: {str(e)}")
    
    def delete_portfolio_project(self, project_id):
        """
        Delete a portfolio project
        
        Args:
            project_id: str
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(project_id)
            
            # Delete the project
            result = self.portfolio_collection.delete_one({"_id": object_id})
            
            if result.deleted_count == 0:
                logger.warning(f"No portfolio project found with ID {project_id}")
                return False
            
            logger.info(f"Deleted portfolio project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting portfolio project {project_id}: {str(e)}")
            raise Exception(f"Failed to delete portfolio project: {str(e)}")
    
    def find_similar_projects(self, user_id, job_description, top_k=5):
        """
        Find portfolio projects similar to a job description using vector similarity
        This is a placeholder - you'll need to implement vector search based on your existing logic
        
        Args:
            user_id: str
            job_description: str
            top_k: int
            
        Returns:
            list: Similar projects with similarity scores
        """
        try:
            # Get all user projects with embeddings
            query = {
                "user_id": user_id,
                "embedding_vector": {"$exists": True, "$ne": []}
            }
            
            projects = list(self.portfolio_collection.find(query))
            
            if not projects:
                return []
            
            # Convert to the format expected by PortfolioAnalysisService
            projects_data = []
            for project in projects:
                projects_data.append({
                    'id': str(project["_id"]),
                    'name': project.get("name"),
                    'description': project.get("description"),
                    'ai_summary': project.get("ai_summary"),
                    'tags': project.get("tags", []),
                    'technologies': project.get("technologies", []),
                    'project_type': project.get("project_type"),
                    'complexity_level': project.get("complexity_level"),
                    'embedding_vector': project.get("embedding_vector", []),
                    'github_url': project.get("github_url"),
                    'live_url': project.get("live_url"),
                    'app_store_url': project.get("app_store_url"),
                    'is_featured': project.get("is_featured", False)
                })
            
            # Use existing PortfolioAnalysisService for similarity calculation
            from .portfolio_service import PortfolioAnalysisService
            analysis_service = PortfolioAnalysisService()
            similar_projects = analysis_service.find_similar_projects(
                job_description, projects_data, top_k
            )
            
            logger.info(f"Found {len(similar_projects)} similar projects for user {user_id}")
            return similar_projects
            
        except Exception as e:
            logger.error(f"Error finding similar projects: {str(e)}")
            raise Exception(f"Failed to find similar projects: {str(e)}")
    
    def get_projects_with_embeddings(self, user_id):
        """
        Get all projects for a user that have embedding vectors
        
        Args:
            user_id: str
            
        Returns:
            list: Projects with embeddings
        """
        try:
            query = {
                "user_id": user_id,
                "embedding_vector": {"$exists": True, "$ne": []}
            }
            
            projects = list(self.portfolio_collection.find(query))
            
            # Convert ObjectIds to strings
            for project in projects:
                project["id"] = str(project["_id"])
                del project["_id"]
            
            logger.info(f"Retrieved {len(projects)} projects with embeddings for user {user_id}")
            return projects
            
        except Exception as e:
            logger.error(f"Error retrieving projects with embeddings: {str(e)}")
            raise Exception(f"Failed to retrieve projects with embeddings: {str(e)}")