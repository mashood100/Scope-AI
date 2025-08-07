from django.db import models
from django.utils import timezone
import json


class JobProposal(models.Model):
    """Model to store job proposals and their metadata"""
    
    job_description = models.TextField(help_text="The original job description provided")
    generated_proposal = models.TextField(help_text="The AI-generated proposal")
    user_id = models.CharField(max_length=255, help_text="ID of the user who requested the proposal")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional metadata fields
    job_title = models.CharField(max_length=500, blank=True, null=True)
    budget_range = models.CharField(max_length=100, blank=True, null=True)
    project_duration = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'job_proposals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Proposal {self.id} - {self.job_title or 'Untitled'}"


class Portfolio(models.Model):
    """Model to store portfolio projects with AI-generated metadata"""
    
    name = models.CharField(max_length=255, help_text="Project name")
    description = models.TextField(help_text="Detailed project description")
    user_id = models.CharField(max_length=255, help_text="ID of the user who owns this project")
    
    # AI-generated fields
    tags = models.JSONField(default=list, help_text="AI-generated tags for the project")
    ai_summary = models.TextField(blank=True, null=True, help_text="AI-generated project summary")
    technologies = models.JSONField(default=list, help_text="AI-extracted technologies used")
    project_type = models.CharField(max_length=100, blank=True, null=True, help_text="AI-determined project type")
    complexity_level = models.CharField(max_length=50, blank=True, null=True, help_text="AI-assessed complexity")
    
    # Vector embeddings for similarity matching
    embedding_vector = models.JSONField(default=list, help_text="Vector embedding of project description")
    
    # Optional manual fields
    github_url = models.URLField(blank=True, null=True, help_text="GitHub repository URL")
    live_url = models.URLField(blank=True, null=True, help_text="Live project URL")
    app_store_url = models.URLField(blank=True, null=True, help_text="App store URL (iOS/Android)")
    images = models.JSONField(default=list, help_text="List of project image URLs")
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False, help_text="Whether to feature this project prominently")
    
    class Meta:
        db_table = 'portfolio_projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['project_type']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user_id}"
    
    def get_tags_display(self):
        """Return tags as a comma-separated string"""
        return ', '.join(self.tags) if self.tags else ''
    
    def get_technologies_display(self):
        """Return technologies as a comma-separated string"""
        return ', '.join(self.technologies) if self.technologies else '' 