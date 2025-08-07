from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class DashboardView(TemplateView):
    """
    Main dashboard overview page
    """
    template_name = 'proposal_generator/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Dashboard Overview',
            'active_page': 'dashboard'
        })
        return context


class PortfolioView(TemplateView):
    """
    Portfolio management page
    """
    template_name = 'proposal_generator/portfolio.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Portfolio Management',
            'active_page': 'portfolio'
        })
        return context


class GenerateView(TemplateView):
    """
    Proposal generation page
    """
    template_name = 'proposal_generator/generate.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Generate Proposal',
            'active_page': 'generate'
        })
        return context


# API endpoint for dashboard statistics (if needed for more complex stats)
def dashboard_stats(request):
    """
    API endpoint to get dashboard statistics
    """
    try:
        # This could be expanded to include more complex statistics
        # For now, the frontend handles stats via the existing portfolio API
        
        stats = {
            'success': True,
            'message': 'Use the portfolio API endpoints for detailed statistics'
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 