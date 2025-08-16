import certifi
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MongoProposalTrackingService:
    """Service class for managing proposal tracking in MongoDB"""
    
    def __init__(self):
        # Initialize MongoDB connection (using same connection string as document_search)
        self.client = MongoClient(
            "mongodb+srv://mashood100:Mashood123*@cluster0.rbsqq.mongodb.net/?ssl=true&sslCAFile=/path/to/certifi/cacert.pem",
            tlsCAFile=certifi.where()
        )
        self.db = self.client["scope_test"]
        self.tracking_collection = self.db.proposal_tracking
    
    def save_proposal_tracking(self, tracking_data):
        """
        Save proposal tracking data to MongoDB
        
        Args:
            tracking_data: Dict containing tracking information
                - proposal_id: str (ID of the generated proposal)
                - user_id: str
                - proposal_link: str (Upwork job/proposal link)
                - connected: str (connection status/number)
                - posted_ago: str (time since posting)
                - is_viewed: bool (default: False)
                - is_hired: bool (default: False)
                
        Returns:
            str: Inserted document ID
        """
        try:
            # Prepare document with timestamps
            document = {
                "proposal_id": tracking_data.get("proposal_id"),
                "user_id": tracking_data.get("user_id"),
                "proposal_link": tracking_data.get("proposal_link"),
                "connected": tracking_data.get("connected"),
                "posted_ago": tracking_data.get("posted_ago"),
                "is_viewed": tracking_data.get("is_viewed", False),
                "is_hired": tracking_data.get("is_hired", False),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert into MongoDB
            result = self.tracking_collection.insert_one(document)
            
            logger.info(f"Created proposal tracking in MongoDB with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating proposal tracking in MongoDB: {str(e)}")
            raise Exception(f"Failed to create proposal tracking: {str(e)}")
    
    def get_user_tracked_proposals(self, user_id, page=1, page_size=10):
        """
        Get paginated tracked proposals for a specific user
        
        Args:
            user_id: str
            page: int (1-based)
            page_size: int
            
        Returns:
            dict: Contains tracking list, total count, and pagination info
        """
        try:
            # Calculate skip value for pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total_count = self.tracking_collection.count_documents({"user_id": user_id})
            
            # Get tracking records with pagination, sorted by created_at descending
            cursor = self.tracking_collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(page_size)
            
            # Convert cursor to list and serialize ObjectIds
            tracking_records = []
            for record in cursor:
                tracking_records.append({
                    "id": str(record["_id"]),
                    "proposal_id": record.get("proposal_id"),
                    "proposal_link": record.get("proposal_link"),
                    "connected": record.get("connected"),
                    "posted_ago": record.get("posted_ago"),
                    "is_viewed": record.get("is_viewed", False),
                    "is_hired": record.get("is_hired", False),
                    "user_id": record.get("user_id"),
                    "created_at": record.get("created_at"),
                    "updated_at": record.get("updated_at")
                })
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            logger.info(f"Retrieved {len(tracking_records)} tracking records for user {user_id} (page {page})")
            
            return {
                "tracking_records": tracking_records,
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
            logger.error(f"Error retrieving user tracking records: {str(e)}")
            raise Exception(f"Failed to retrieve tracking records: {str(e)}")
    
    def get_tracking_by_id(self, tracking_id):
        """
        Get a specific tracking record by ID
        
        Args:
            tracking_id: str
            
        Returns:
            dict: Tracking data or None if not found
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(tracking_id)
            
            # Find the tracking record
            record = self.tracking_collection.find_one({"_id": object_id})
            
            if not record:
                return None
            
            # Convert ObjectId to string for JSON serialization
            tracking_data = {
                "id": str(record["_id"]),
                "proposal_id": record.get("proposal_id"),
                "proposal_link": record.get("proposal_link"),
                "connected": record.get("connected"),
                "posted_ago": record.get("posted_ago"),
                "is_viewed": record.get("is_viewed", False),
                "is_hired": record.get("is_hired", False),
                "user_id": record.get("user_id"),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at")
            }
            
            logger.info(f"Retrieved tracking record {tracking_id}")
            return tracking_data
            
        except Exception as e:
            logger.error(f"Error retrieving tracking record {tracking_id}: {str(e)}")
            raise Exception(f"Failed to retrieve tracking record: {str(e)}")
    
    def update_tracking_status(self, tracking_id, is_viewed=None, is_hired=None):
        """
        Update tracking status fields
        
        Args:
            tracking_id: str
            is_viewed: bool (optional)
            is_hired: bool (optional)
            
        Returns:
            bool: True if updated successfully
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(tracking_id)
            
            # Prepare update data
            update_data = {"updated_at": datetime.utcnow()}
            
            if is_viewed is not None:
                update_data["is_viewed"] = is_viewed
            if is_hired is not None:
                update_data["is_hired"] = is_hired
            
            # Update the tracking record
            result = self.tracking_collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                logger.warning(f"No tracking record found with ID {tracking_id}")
                return False
            
            logger.info(f"Updated tracking record {tracking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating tracking record {tracking_id}: {str(e)}")
            raise Exception(f"Failed to update tracking record: {str(e)}")
    
    def delete_tracking(self, tracking_id):
        """
        Delete a tracking record
        
        Args:
            tracking_id: str
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(tracking_id)
            
            # Delete the tracking record
            result = self.tracking_collection.delete_one({"_id": object_id})
            
            if result.deleted_count == 0:
                logger.warning(f"No tracking record found with ID {tracking_id}")
                return False
            
            logger.info(f"Deleted tracking record {tracking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting tracking record {tracking_id}: {str(e)}")
            raise Exception(f"Failed to delete tracking record: {str(e)}")
    
    def get_tracking_stats(self, user_id):
        """
        Get statistics about user's tracked proposals
        
        Args:
            user_id: str
            
        Returns:
            dict: Statistics data
        """
        try:
            # Get total tracked proposals
            total_tracked = self.tracking_collection.count_documents({"user_id": user_id})
            
            # Get viewed proposals
            viewed_count = self.tracking_collection.count_documents({
                "user_id": user_id,
                "is_viewed": True
            })
            
            # Get hired proposals
            hired_count = self.tracking_collection.count_documents({
                "user_id": user_id,
                "is_hired": True
            })
            
            # Calculate rates
            view_rate = (viewed_count / total_tracked * 100) if total_tracked > 0 else 0
            hire_rate = (hired_count / total_tracked * 100) if total_tracked > 0 else 0
            
            stats = {
                "total_tracked": total_tracked,
                "viewed_count": viewed_count,
                "hired_count": hired_count,
                "view_rate": round(view_rate, 1),
                "hire_rate": round(hire_rate, 1)
            }
            
            logger.info(f"Generated tracking stats for user {user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating tracking stats: {str(e)}")
            raise Exception(f"Failed to generate tracking stats: {str(e)}")
    
    def get_tracking_by_proposal_id(self, proposal_id):
        """
        Get tracking record by proposal ID
        
        Args:
            proposal_id: str
            
        Returns:
            dict: Tracking data or None if not found
        """
        try:
            # Find the tracking record by proposal_id
            record = self.tracking_collection.find_one({"proposal_id": proposal_id})
            
            if not record:
                return None
            
            # Convert ObjectId to string for JSON serialization
            tracking_data = {
                "id": str(record["_id"]),
                "proposal_id": record.get("proposal_id"),
                "proposal_link": record.get("proposal_link"),
                "connected": record.get("connected"),
                "posted_ago": record.get("posted_ago"),
                "is_viewed": record.get("is_viewed", False),
                "is_hired": record.get("is_hired", False),
                "user_id": record.get("user_id"),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at")
            }
            
            logger.info(f"Retrieved tracking record for proposal {proposal_id}")
            return tracking_data
            
        except Exception as e:
            logger.error(f"Error retrieving tracking record for proposal {proposal_id}: {str(e)}")
            raise Exception(f"Failed to retrieve tracking record: {str(e)}")