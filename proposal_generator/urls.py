from django.urls import path
from .api.views import (
    GenerateProposalView, UserProposalsView, ProposalDetailView,
    CreatePortfolioView, UserPortfolioView, PortfolioDetailView, SimilarProjectsView
)
from .api.ui_views import DashboardView, PortfolioView, GenerateView, dashboard_stats

urlpatterns = [
    # UI Dashboard pages
    path('', DashboardView.as_view(), name='dashboard'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('generate/', GenerateView.as_view(), name='generate'),
    path('api/dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    
    # Proposal API endpoints
    path('api/generate/', GenerateProposalView.as_view(), name='generate-proposal'),
    path('api/user/<str:user_id>/', UserProposalsView.as_view(), name='user-proposals'),
    path('api/detail/<int:proposal_id>/', ProposalDetailView.as_view(), name='proposal-detail'),
    
    # Portfolio API endpoints
    path('api/portfolio/create/', CreatePortfolioView.as_view(), name='create-portfolio'),
    path('api/portfolio/user/<str:user_id>/', UserPortfolioView.as_view(), name='user-portfolio'),
    path('api/portfolio/detail/<int:project_id>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('api/portfolio/similar/', SimilarProjectsView.as_view(), name='similar-projects'),
] 