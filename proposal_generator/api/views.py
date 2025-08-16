from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.proposal_service import ProposalService
from .services.portfolio_service import PortfolioAnalysisService
from .services.mongo_proposal_service import MongoProposalService
from .services.mongo_portfolio_service import MongoPortfolioService
from .services.mongo_proposal_tracking_service import MongoProposalTrackingService
from .models import JobProposal, Portfolio, ProposalTracking
from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__name__)


class GenerateCustomProposalView(APIView):
    """
    API endpoint to generate job proposals with custom portfolio selection and external links
    
    POST /proposals/api/generate/custom/
    {
        "job_description": "Your job description here...",
        "client_name": "John Smith",
        "selected_projects": [{"id": 1, "name": "Project 1", ...}, ...],
        "external_links": {
            "github": true,
            "stackoverflow": false,
            "website": true
        },
        "user_id": "user123"
    }
    """
    
    def post(self, request):
        try:
            job_description = request.data.get('job_description')
            client_name = request.data.get('client_name', '')
            selected_projects = request.data.get('selected_projects', [])
            external_links = request.data.get('external_links', {})
            user_id = request.data.get('user_id', 'user123')  # Default for backward compatibility
            
            # Validate required fields
            if not job_description:
                return Response(
                    {"error": "job_description is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate job description length
            if len(job_description.strip()) < 50:
                return Response(
                    {"error": "Job description must be at least 50 characters long"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize proposal service and generate proposal
            proposal_service = ProposalService()
            
            # Generate the custom proposal
            generated_proposal = proposal_service.generate_custom_proposal(
                job_description=job_description,
                client_name=client_name,
                selected_projects=selected_projects,
                external_links=external_links
            )
            
            # Save to MongoDB
            mongo_service = MongoProposalService()
            metadata = proposal_service.extract_job_metadata(job_description)
            
            proposal_data = {
                "job_description": job_description,
                "generated_proposal": generated_proposal,
                "user_id": user_id,
                "job_title": metadata.get("job_title"),
                "budget_range": metadata.get("budget_range"),
                "project_duration": metadata.get("project_duration")
            }
            
            proposal_id = mongo_service.create_proposal(proposal_data)
            
            logger.info(f"Generated custom proposal for user {user_id}, saved to MongoDB: {proposal_id}")
            
            # Prepare response
            response_data = {
                "proposal_id": proposal_id,
                "generated_proposal": generated_proposal,
                "selected_projects_count": len(selected_projects),
                "client_name": client_name,
                "external_links": external_links
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in GenerateCustomProposalView: {str(e)}")
            logger.error(f"Full traceback: {error_details}")
            return Response(
                {
                    "error": f"Failed to generate proposal: {str(e)}",
                    "details": str(e),
                    "type": type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GenerateProposalView(APIView):
    """
    API endpoint to generate job proposals based on job descriptions
    
    POST /proposals/api/generate/
    {
        "job_description": "Your job description here...",
        "user_id": "user123"
    }
    """
    
    def post(self, request):
        try:
            job_description = request.data.get('job_description')
            user_id = request.data.get('user_id', 'user123')  # Default for backward compatibility
            
            # Validate required fields
            if not job_description:
                return Response(
                    {"error": "job_description is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate job description length
            if len(job_description.strip()) < 50:
                return Response(
                    {"error": "Job description must be at least 50 characters long"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Search for relevant portfolio projects
            relevant_projects = []
            try:
                # Get user's portfolio projects with embeddings from MongoDB
                mongo_portfolio_service = MongoPortfolioService()
                similar_projects = mongo_portfolio_service.find_similar_projects(
                    user_id, job_description, top_k=2
                )
                
                # Filter projects with similarity > 0.6 (reasonably relevant)
                relevant_projects = [
                    item for item in similar_projects 
                    if item['similarity_score'] > 0.6
                ]
                
                logger.info(f"Found {len(relevant_projects)} relevant projects for user {user_id}")
                
            except Exception as e:
                logger.warning(f"Portfolio search failed for user {user_id}: {str(e)}")
                # Continue with proposal generation even if portfolio search fails
            
            # Initialize proposal service and generate proposal
            proposal_service = ProposalService()
            
            # Generate the proposal with relevant projects
            generated_proposal = proposal_service.generate_proposal_with_portfolio(
                job_description, relevant_projects
            )
            
            # Save to MongoDB
            mongo_service = MongoProposalService()
            metadata = proposal_service.extract_job_metadata(job_description)
            
            proposal_data = {
                "job_description": job_description,
                "generated_proposal": generated_proposal,
                "user_id": user_id,
                "job_title": metadata.get("job_title"),
                "budget_range": metadata.get("budget_range"),
                "project_duration": metadata.get("project_duration")
            }
            
            proposal_id = mongo_service.create_proposal(proposal_data)
            
            logger.info(f"Generated proposal for user {user_id}, saved to MongoDB: {proposal_id}")
            
            # Prepare response with relevant projects info
            response_data = {
                "proposal_id": proposal_id,
                "generated_proposal": generated_proposal,
                "relevant_projects_found": len(relevant_projects),
            }
            
            # Add relevant projects details for reference
            if relevant_projects:
                response_data["included_projects"] = [
                    {
                        "name": item['project']['name'],
                        "similarity_score": round(item['similarity_score'], 3),
                        "github_url": item['project'].get('github_url'),
                        "live_url": item['project'].get('live_url'),
                        "app_store_url": item['project'].get('app_store_url')
                    }
                    for item in relevant_projects
                ]
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in GenerateProposalView: {str(e)}")
            logger.error(f"Full traceback: {error_details}")
            return Response(
                {
                    "error": f"Failed to generate proposal: {str(e)}",
                    "details": str(e),
                    "type": type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProposalsView(APIView):
    """
    API endpoint to get all proposals for a specific user
    
    GET /proposals/api/user/{user_id}/
    """
    
    def get(self, request, user_id):
        try:
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Get proposals from MongoDB
            mongo_service = MongoProposalService()
            result = mongo_service.get_user_proposals(user_id, page, page_size)
            
            # Format proposals data for response
            proposals_data = []
            for proposal in result["proposals"]:
                # Truncate job description for list view
                job_desc = proposal.get("job_description", "")
                truncated_desc = job_desc[:200] + "..." if len(job_desc) > 200 else job_desc
                
                proposals_data.append({
                    "id": proposal["id"],
                    "job_title": proposal.get("job_title"),
                    "job_description": truncated_desc,
                    "generated_proposal": proposal.get("generated_proposal"),
                    "budget_range": proposal.get("budget_range"),
                    "project_duration": proposal.get("project_duration"),
                    "created_at": proposal.get("created_at"),
                    "updated_at": proposal.get("updated_at")
                })
            
            # Return paginated response
            return Response({
                "results": proposals_data,
                "count": result["pagination"]["total_count"],
                "next": f"?page={page + 1}" if result["pagination"]["has_next"] else None,
                "previous": f"?page={page - 1}" if result["pagination"]["has_previous"] else None,
                "total_pages": result["pagination"]["total_pages"],
                "current_page": result["pagination"]["current_page"]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in UserProposalsView: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve proposals: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProposalDetailView(APIView):
    """
    API endpoint to get a specific proposal by ID
    
    GET /proposals/api/detail/{proposal_id}/
    """
    
    def get(self, request, proposal_id):
        try:
            # Get proposal from MongoDB
            mongo_service = MongoProposalService()
            proposal = mongo_service.get_proposal_by_id(proposal_id)
            
            if not proposal:
                return Response(
                    {"error": "Proposal not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(proposal, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ProposalDetailView: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve proposal: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProposalSearchView(APIView):
    """
    API endpoint to search proposals
    
    POST /proposals/api/search/
    {
        "user_id": "user123",
        "search_query": "react development"
    }
    """
    
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            search_query = request.data.get('search_query')
            
            if not user_id or not search_query:
                return Response(
                    {"error": "user_id and search_query are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Search proposals in MongoDB
            mongo_service = MongoProposalService()
            proposals = mongo_service.search_proposals(user_id, search_query)
            
            return Response({
                "results": proposals,
                "count": len(proposals),
                "search_query": search_query
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ProposalSearchView: {str(e)}")
            return Response(
                {"error": f"Failed to search proposals: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProposalStatsView(APIView):
    """
    API endpoint to get proposal statistics for a user
    
    GET /proposals/api/stats/{user_id}/
    """
    
    def get(self, request, user_id):
        try:
            # Get stats from MongoDB
            mongo_service = MongoProposalService()
            stats = mongo_service.get_proposals_stats(user_id)
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ProposalStatsView: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve proposal stats: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteProposalView(APIView):
    """
    API endpoint to delete a proposal
    
    DELETE /proposals/api/delete/{proposal_id}/
    """
    
    def delete(self, request, proposal_id):
        try:
            # Delete proposal from MongoDB
            mongo_service = MongoProposalService()
            success = mongo_service.delete_proposal(proposal_id)
            
            if not success:
                return Response(
                    {"error": "Proposal not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "success": True,
                "message": "Proposal deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in DeleteProposalView: {str(e)}")
            return Response(
                {"error": f"Failed to delete proposal: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ===== PORTFOLIO MANAGEMENT VIEWS =====

class CreatePortfolioView(APIView):
    """
    API endpoint to create a new portfolio project with AI analysis
    
    POST /proposals/api/portfolio/create/
    {
        "name": "Project name",
        "description": "Detailed project description",
        "user_id": "user123",
        "github_url": "https://github.com/user/repo",
        "live_url": "https://project.com",
        "app_store_url": "https://apps.apple.com/app/project",
        "images": ["url1", "url2"],
        "is_featured": false
    }
    """
    
    def post(self, request):
        try:
            # Extract required fields
            name = request.data.get('name')
            description = request.data.get('description')
            user_id = request.data.get('user_id')
            
            # Validate required fields
            if not name:
                return Response(
                    {"error": "name is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not description:
                return Response(
                    {"error": "description is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not user_id:
                return Response(
                    {"error": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate description length
            if len(description.strip()) < 50:
                return Response(
                    {"error": "Project description must be at least 50 characters long"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize portfolio analysis service
            analysis_service = PortfolioAnalysisService()
            
            # Run AI analysis
            logger.info(f"Running AI analysis for project: {name}")
            ai_analysis = analysis_service.analyze_project(name, description)
            
            # Extract optional fields
            github_url = request.data.get('github_url')
            live_url = request.data.get('live_url')
            app_store_url = request.data.get('app_store_url')
            images = request.data.get('images', [])
            is_featured = request.data.get('is_featured', False)
            
            # Create portfolio project in MongoDB
            mongo_portfolio_service = MongoPortfolioService()
            
            project_data = {
                "name": name,
                "description": description,
                "user_id": user_id,
                "tags": ai_analysis['tags'],
                "ai_summary": ai_analysis['ai_summary'],
                "technologies": ai_analysis['technologies'],
                "project_type": ai_analysis['project_type'],
                "complexity_level": ai_analysis['complexity_level'],
                "embedding_vector": ai_analysis['embedding_vector'],
                "github_url": github_url,
                "live_url": live_url,
                "app_store_url": app_store_url,
                "images": images,
                "is_featured": is_featured
            }
            
            project_id = mongo_portfolio_service.create_portfolio_project(project_data)
            
            logger.info(f"Created portfolio project {project_id} for user {user_id}")
            
            return Response({
                "success": True,
                "project_id": project_id,
                "name": name,
                "ai_summary": ai_analysis['ai_summary'],
                "tags": ai_analysis['tags'],
                "technologies": ai_analysis['technologies'],
                "project_type": ai_analysis['project_type'],
                "complexity_level": ai_analysis['complexity_level'],
                "message": "Portfolio project created successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in CreatePortfolioView: {str(e)}")
            return Response(
                {"error": f"Failed to create portfolio project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPortfolioView(APIView):
    """
    API endpoint to get all portfolio projects for a specific user
    
    GET /proposals/api/portfolio/user/{user_id}/
    """
    
    def get(self, request, user_id):
        try:
            # Get filter parameters
            project_type = request.query_params.get('project_type')
            is_featured = request.query_params.get('is_featured')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Convert is_featured to boolean if provided
            is_featured_bool = None
            if is_featured is not None:
                is_featured_bool = is_featured.lower() == 'true'
            
            # Get projects from MongoDB
            mongo_portfolio_service = MongoPortfolioService()
            result = mongo_portfolio_service.get_user_portfolio_projects(
                user_id=user_id,
                page=page,
                page_size=page_size,
                project_type=project_type,
                is_featured=is_featured_bool
            )
            
            # Format projects data for response
            projects_data = []
            for project in result["projects"]:
                # Truncate description for list view
                description = project.get("description", "")
                truncated_desc = description[:200] + "..." if len(description) > 200 else description
                
                projects_data.append({
                    "id": project["id"],
                    "name": project.get("name"),
                    "description": truncated_desc,
                    "ai_summary": project.get("ai_summary"),
                    "tags": project.get("tags", []),
                    "technologies": project.get("technologies", []),
                    "project_type": project.get("project_type"),
                    "complexity_level": project.get("complexity_level"),
                    "github_url": project.get("github_url"),
                    "live_url": project.get("live_url"),
                    "app_store_url": project.get("app_store_url"),
                    "images": project.get("images", []),
                    "is_featured": project.get("is_featured", False),
                    "created_at": project.get("created_at"),
                    "updated_at": project.get("updated_at")
                })
            
            # Return paginated response
            return Response({
                "results": projects_data,
                "count": result["pagination"]["total_count"],
                "next": f"?page={page + 1}" if result["pagination"]["has_next"] else None,
                "previous": f"?page={page - 1}" if result["pagination"]["has_previous"] else None,
                "total_pages": result["pagination"]["total_pages"],
                "current_page": result["pagination"]["current_page"]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in UserPortfolioView: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve portfolio projects: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PortfolioDetailView(APIView):
    """
    API endpoint to get, update, or delete a specific portfolio project
    
    GET /proposals/api/portfolio/detail/{project_id}/
    PUT /proposals/api/portfolio/detail/{project_id}/
    DELETE /proposals/api/portfolio/detail/{project_id}/
    """
    
    def get(self, request, project_id):
        try:
            # Get project from MongoDB
            mongo_portfolio_service = MongoPortfolioService()
            project = mongo_portfolio_service.get_portfolio_project_by_id(project_id)
            
            if not project:
                return Response(
                    {"error": "Portfolio project not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(project, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in PortfolioDetailView GET: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve portfolio project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, project_id):
        try:
            # Get current project from MongoDB
            mongo_portfolio_service = MongoPortfolioService()
            current_project = mongo_portfolio_service.get_portfolio_project_by_id(project_id)
            
            if not current_project:
                return Response(
                    {"error": "Portfolio project not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Prepare update data
            update_data = {}
            
            # Update basic fields if provided
            if 'name' in request.data:
                update_data['name'] = request.data['name']
            if 'github_url' in request.data:
                update_data['github_url'] = request.data['github_url']
            if 'live_url' in request.data:
                update_data['live_url'] = request.data['live_url']
            if 'app_store_url' in request.data:
                update_data['app_store_url'] = request.data['app_store_url']
            if 'images' in request.data:
                update_data['images'] = request.data['images']
            if 'is_featured' in request.data:
                update_data['is_featured'] = request.data['is_featured']
            
            # Check if description changed (requires AI re-analysis)
            new_description = request.data.get('description')
            if new_description and new_description != current_project.get('description'):
                logger.info(f"Re-analyzing project {project_id} due to description change")
                analysis_service = PortfolioAnalysisService()
                ai_analysis = analysis_service.analyze_project(
                    update_data.get('name', current_project.get('name')), 
                    new_description
                )
                
                update_data.update({
                    'description': new_description,
                    'tags': ai_analysis['tags'],
                    'ai_summary': ai_analysis['ai_summary'],
                    'technologies': ai_analysis['technologies'],
                    'project_type': ai_analysis['project_type'],
                    'complexity_level': ai_analysis['complexity_level'],
                    'embedding_vector': ai_analysis['embedding_vector']
                })
            elif new_description:
                update_data['description'] = new_description
            
            # Update in MongoDB
            success = mongo_portfolio_service.update_portfolio_project(project_id, update_data)
            
            if not success:
                return Response(
                    {"error": "Failed to update portfolio project"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Get updated project
            updated_project = mongo_portfolio_service.get_portfolio_project_by_id(project_id)
            
            logger.info(f"Updated portfolio project {project_id}")
            
            return Response({
                "success": True,
                "project_id": project_id,
                "name": updated_project.get('name'),
                "ai_summary": updated_project.get('ai_summary'),
                "tags": updated_project.get('tags'),
                "technologies": updated_project.get('technologies'),
                "project_type": updated_project.get('project_type'),
                "complexity_level": updated_project.get('complexity_level'),
                "updated_at": updated_project.get('updated_at'),
                "message": "Portfolio project updated successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in PortfolioDetailView PUT: {str(e)}")
            return Response(
                {"error": f"Failed to update portfolio project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, project_id):
        try:
            # Get project info before deletion
            mongo_portfolio_service = MongoPortfolioService()
            project = mongo_portfolio_service.get_portfolio_project_by_id(project_id)
            
            if not project:
                return Response(
                    {"error": "Portfolio project not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            project_name = project.get('name', 'Unknown')
            
            # Delete from MongoDB
            success = mongo_portfolio_service.delete_portfolio_project(project_id)
            
            if not success:
                return Response(
                    {"error": "Failed to delete portfolio project"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logger.info(f"Deleted portfolio project {project_id}: {project_name}")
            
            return Response({
                "success": True,
                "message": f"Portfolio project '{project_name}' deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in PortfolioDetailView DELETE: {str(e)}")
            return Response(
                {"error": f"Failed to delete portfolio project: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimilarProjectsView(APIView):
    """
    API endpoint to find portfolio projects similar to a job description
    
    POST /proposals/api/portfolio/similar/
    {
        "job_description": "Job description text",
        "user_id": "user123",
        "top_k": 3
    }
    """
    
    def post(self, request):
        try:
            job_description = request.data.get('job_description')
            user_id = request.data.get('user_id')
            top_k = request.data.get('top_k', 3)
            
            # Validate required fields
            if not job_description:
                return Response(
                    {"error": "job_description is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not user_id:
                return Response(
                    {"error": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user's portfolio projects with embeddings from MongoDB
            mongo_portfolio_service = MongoPortfolioService()
            similar_projects = mongo_portfolio_service.find_similar_projects(
                user_id, job_description, top_k
            )
            
            # Format response
            result = []
            for item in similar_projects:
                project = item['project']
                result.append({
                    "project_id": project['id'],
                    "name": project['name'],
                    "ai_summary": project['ai_summary'],
                    "tags": project['tags'],
                    "technologies": project['technologies'],
                    "project_type": project['project_type'],
                    "complexity_level": project['complexity_level'],
                    "github_url": project['github_url'],
                    "live_url": project['live_url'],
                    "app_store_url": project['app_store_url'],
                    "is_featured": project['is_featured'],
                    "similarity_score": round(item['similarity_score'], 4)
                })
            
            logger.info(f"Found {len(similar_projects)} similar projects for user {user_id}")
            
            return Response({
                "similar_projects": result,
                "total_found": len(result),
                "job_description": job_description[:100] + "..." if len(job_description) > 100 else job_description
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in SimilarProjectsView: {str(e)}")
            return Response(
                {"error": f"Failed to find similar projects: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ===== PROPOSAL TRACKING VIEWS =====

class SaveProposalTrackingView(APIView):
    """
    API endpoint to save proposal tracking data
    
    POST /proposals/api/tracking/save/
    {
        "proposal_id": "60f7c1234567890abcdef123",
        "user_id": "user123",
        "proposal_link": "https://upwork.com/jobs/job-id",
        "connected": "10 connects",
        "posted_ago": "2 hours ago",
        "is_viewed": false,
        "is_hired": false
    }
    """
    
    def post(self, request):
        try:
            # Extract required fields
            proposal_id = request.data.get('proposal_id')
            user_id = request.data.get('user_id')
            proposal_link = request.data.get('proposal_link')
            connected = request.data.get('connected')
            posted_ago = request.data.get('posted_ago')
            
            # Validate required fields
            if not proposal_id:
                return Response(
                    {"error": "proposal_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not user_id:
                return Response(
                    {"error": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not proposal_link:
                return Response(
                    {"error": "proposal_link is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not connected:
                return Response(
                    {"error": "connected is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not posted_ago:
                return Response(
                    {"error": "posted_ago is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate URL format
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(proposal_link):
                return Response(
                    {"error": "proposal_link must be a valid URL"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if tracking already exists for this proposal
            tracking_service = MongoProposalTrackingService()
            existing_tracking = tracking_service.get_tracking_by_proposal_id(proposal_id)
            
            if existing_tracking:
                return Response(
                    {"error": "Tracking data already exists for this proposal"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare tracking data
            tracking_data = {
                "proposal_id": proposal_id,
                "user_id": user_id,
                "proposal_link": proposal_link,
                "connected": connected,
                "posted_ago": posted_ago,
                "is_viewed": request.data.get('is_viewed', False),
                "is_hired": request.data.get('is_hired', False)
            }
            
            # Save to MongoDB
            tracking_id = tracking_service.save_proposal_tracking(tracking_data)
            
            logger.info(f"Saved proposal tracking for proposal {proposal_id}, tracking ID: {tracking_id}")
            
            return Response({
                "success": True,
                "tracking_id": tracking_id,
                "proposal_id": proposal_id,
                "message": "Proposal tracking saved successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in SaveProposalTrackingView: {str(e)}")
            logger.error(f"Full traceback: {error_details}")
            return Response(
                {
                    "error": f"Failed to save proposal tracking: {str(e)}",
                    "details": str(e),
                    "type": type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserTrackedProposalsView(APIView):
    """
    API endpoint to get all tracked proposals for a specific user
    
    GET /proposals/api/tracking/user/{user_id}/
    """
    
    def get(self, request, user_id):
        try:
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Get tracking records from MongoDB
            tracking_service = MongoProposalTrackingService()
            result = tracking_service.get_user_tracked_proposals(user_id, page, page_size)
            
            # Return paginated response
            return Response({
                "results": result["tracking_records"],
                "count": result["pagination"]["total_count"],
                "next": f"?page={page + 1}" if result["pagination"]["has_next"] else None,
                "previous": f"?page={page - 1}" if result["pagination"]["has_previous"] else None,
                "total_pages": result["pagination"]["total_pages"],
                "current_page": result["pagination"]["current_page"]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in UserTrackedProposalsView: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve tracked proposals: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateTrackingStatusView(APIView):
    """
    API endpoint to update tracking status (viewed/hired)
    
    PUT /proposals/api/tracking/update/{tracking_id}/
    {
        "is_viewed": true,
        "is_hired": false
    }
    """
    
    def put(self, request, tracking_id):
        try:
            is_viewed = request.data.get('is_viewed')
            is_hired = request.data.get('is_hired')
            
            # At least one field should be provided
            if is_viewed is None and is_hired is None:
                return Response(
                    {"error": "At least one of is_viewed or is_hired must be provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update tracking status
            tracking_service = MongoProposalTrackingService()
            success = tracking_service.update_tracking_status(
                tracking_id, is_viewed, is_hired
            )
            
            if not success:
                return Response(
                    {"error": "Tracking record not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get updated record
            updated_record = tracking_service.get_tracking_by_id(tracking_id)
            
            return Response({
                "success": True,
                "tracking_id": tracking_id,
                "updated_record": updated_record,
                "message": "Tracking status updated successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in UpdateTrackingStatusView: {str(e)}")
            return Response(
                {"error": f"Failed to update tracking status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrackingStatsView(APIView):
    """
    API endpoint to get tracking statistics for a user
    
    GET /proposals/api/tracking/stats/{user_id}/
    """
    
    def get(self, request, user_id):
        try:
            # Get stats from MongoDB
            tracking_service = MongoProposalTrackingService()
            stats = tracking_service.get_tracking_stats(user_id)
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in TrackingStatsView: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve tracking stats: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 