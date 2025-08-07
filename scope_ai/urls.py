
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('documents/', include('document_search.urls')),
    path('proposals/', include('proposal_generator.urls')),
]
