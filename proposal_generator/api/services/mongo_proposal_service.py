import certifi
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MongoProposalService:
    """Service class for managing proposals in MongoDB"""
    
    def __init__(self):
        # Initialize MongoDB connection (using same connection string as document_search)
        self.client = MongoClient(
            "mongodb+srv://mashood100:Mashood123*@cluster0.rbsqq.mongodb.net/?ssl=true&sslCAFile=/path/to/certifi/cacert.pem",
            tlsCAFile=certifi.where()
        )
        self.db = self.client["scope_test"]
        self.proposals_collection = self.db.job_proposals
        self.portfolio_collection = self.db.portfolio_projects
    
    def create_proposal(self, proposal_data):
        """
        Create a new proposal in MongoDB
        
        Args:
            proposal_data: Dict containing proposal information
                - job_description: str
                - generated_proposal: str
                - user_id: str
                - job_title: str (optional)
                - budget_range: str (optional)
                - project_duration: str (optional)
                
        Returns:
            str: Inserted document ID
        """
        try:
            # Prepare document with timestamps
            document = {
                "job_description": proposal_data.get("job_description"),
                "generated_proposal": proposal_data.get("generated_proposal"),
                "user_id": proposal_data.get("user_id"),
                "job_title": proposal_data.get("job_title"),
                "budget_range": proposal_data.get("budget_range"),
                "project_duration": proposal_data.get("project_duration"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into MongoDB
            result = self.proposals_collection.insert_one(document)
            
            logger.info(f"Created proposal in MongoDB with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating proposal in MongoDB: {str(e)}")
            raise Exception(f"Failed to create proposal: {str(e)}")
    
    def get_user_proposals(self, user_id, page=1, page_size=10):
        """
        Get paginated proposals for a specific user
        
        Args:
            user_id: str
            page: int (1-based)
            page_size: int
            
        Returns:
            dict: Contains proposals list, total count, and pagination info
        """
        try:
            # Calculate skip value for pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total_count = self.proposals_collection.count_documents({"user_id": user_id})
            
            # Get proposals with pagination, sorted by created_at descending
            cursor = self.proposals_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(page_size)
            
            # Convert cursor to list and serialize ObjectIds
            proposals = []
            for proposal in cursor:
                proposals.append({
                    "id": str(proposal["_id"]),
                    "job_description": proposal.get("job_description"),
                    "generated_proposal": proposal.get("generated_proposal"),
                    "job_title": proposal.get("job_title"),
                    "budget_range": proposal.get("budget_range"),
                    "project_duration": proposal.get("project_duration"),
                    "user_id": proposal.get("user_id"),
                    "created_at": proposal.get("created_at"),
                    "updated_at": proposal.get("updated_at")
                })
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            logger.info(f"Retrieved {len(proposals)} proposals for user {user_id} (page {page})")
            
            return {
                "proposals": proposals,
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
            logger.error(f"Error retrieving user proposals: {str(e)}")
            raise Exception(f"Failed to retrieve proposals: {str(e)}")
    
    def get_proposal_by_id(self, proposal_id):
        """
        Get a specific proposal by ID
        
        Args:
            proposal_id: str
            
        Returns:
            dict: Proposal data or None if not found
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(proposal_id)
            
            # Find the proposal
            proposal = self.proposals_collection.find_one({"_id": object_id})
            
            if not proposal:
                return None
            
            # Convert ObjectId to string for JSON serialization
            proposal_data = {
                "id": str(proposal["_id"]),
                "job_description": proposal.get("job_description"),
                "generated_proposal": proposal.get("generated_proposal"),
                "job_title": proposal.get("job_title"),
                "budget_range": proposal.get("budget_range"),
                "project_duration": proposal.get("project_duration"),
                "user_id": proposal.get("user_id"),
                "created_at": proposal.get("created_at"),
                "updated_at": proposal.get("updated_at")
            }
            
            logger.info(f"Retrieved proposal {proposal_id}")
            return proposal_data
            
        except Exception as e:
            logger.error(f"Error retrieving proposal {proposal_id}: {str(e)}")
            raise Exception(f"Failed to retrieve proposal: {str(e)}")
    
    def update_proposal(self, proposal_id, update_data):
        """
        Update a proposal
        
        Args:
            proposal_id: str
            update_data: dict containing fields to update
            
        Returns:
            bool: True if updated successfully
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(proposal_id)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update the proposal
            result = self.proposals_collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                logger.warning(f"No proposal found with ID {proposal_id}")
                return False
            
            logger.info(f"Updated proposal {proposal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating proposal {proposal_id}: {str(e)}")
            raise Exception(f"Failed to update proposal: {str(e)}")
    
    def delete_proposal(self, proposal_id):
        """
        Delete a proposal
        
        Args:
            proposal_id: str
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(proposal_id)
            
            # Delete the proposal
            result = self.proposals_collection.delete_one({"_id": object_id})
            
            if result.deleted_count == 0:
                logger.warning(f"No proposal found with ID {proposal_id}")
                return False
            
            logger.info(f"Deleted proposal {proposal_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting proposal {proposal_id}: {str(e)}")
            raise Exception(f"Failed to delete proposal: {str(e)}")
    
    def search_proposals(self, user_id, search_query):
        """
        Search proposals by job title or description content
        
        Args:
            user_id: str
            search_query: str
            
        Returns:
            list: Matching proposals
        """
        try:
            # Create text search query
            query = {
                "user_id": user_id,
                "$or": [
                    {"job_title": {"$regex": search_query, "$options": "i"}},
                    {"job_description": {"$regex": search_query, "$options": "i"}},
                    {"generated_proposal": {"$regex": search_query, "$options": "i"}}
                ]
            }
            
            # Find matching proposals
            cursor = self.proposals_collection.find(query).sort("created_at", -1)
            
            # Convert to list
            proposals = []
            for proposal in cursor:
                proposals.append({
                    "id": str(proposal["_id"]),
                    "job_description": proposal.get("job_description"),
                    "generated_proposal": proposal.get("generated_proposal"),
                    "job_title": proposal.get("job_title"),
                    "budget_range": proposal.get("budget_range"),
                    "project_duration": proposal.get("project_duration"),
                    "user_id": proposal.get("user_id"),
                    "created_at": proposal.get("created_at"),
                    "updated_at": proposal.get("updated_at")
                })
            
            logger.info(f"Found {len(proposals)} proposals matching search query for user {user_id}")
            return proposals
            
        except Exception as e:
            logger.error(f"Error searching proposals: {str(e)}")
            raise Exception(f"Failed to search proposals: {str(e)}")
    
    def get_proposals_stats(self, user_id):
        """
        Get statistics about user's proposals
        
        Args:
            user_id: str
            
        Returns:
            dict: Statistics data
        """
        try:
            # Get total count
            total_proposals = self.proposals_collection.count_documents({"user_id": user_id})
            
            # Get proposals from last 30 days
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_proposals = self.proposals_collection.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": thirty_days_ago}
            })
            
            # Get most recent proposal
            latest_proposal = self.proposals_collection.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            
            stats = {
                "total_proposals": total_proposals,
                "recent_proposals_30_days": recent_proposals,
                "latest_proposal_date": latest_proposal.get("created_at") if latest_proposal else None
            }
            
            logger.info(f"Generated stats for user {user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating proposal stats: {str(e)}")
            raise Exception(f"Failed to generate stats: {str(e)}")