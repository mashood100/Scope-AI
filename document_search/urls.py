from django.urls import path
from .api.views import DocumentCreateView, SearchView, UserDocumentsView, GmailCheckView

urlpatterns = [
    # path('api/documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('api/documents/search/', SearchView.as_view(), name='document-search'),
    path('api/documents/create/', DocumentCreateView.as_view(), name='document-create'),
    path('api/documents/user/<str:user_id>/', UserDocumentsView.as_view(), name='user-documents'),
    path('api/gmail/check/', GmailCheckView.as_view(), name='gmail-check'),
] 