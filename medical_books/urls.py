"""
URL configuration for medical_books project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from django.conf.urls import handler404
# from .views import custom_404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/books/', include('books.urls')),
    path('api/assessments/', include('assessments.urls')),
    path('api/egogram/', include('egogram.urls')),
    path('api/counsellor/', include('counsellor.urls')),
    path('api/hospital/', include('hospital_management.urls')),
    path('api/', include('chatbot_ws.urls')),
       
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = "medical_books.views.custom_404_view"

