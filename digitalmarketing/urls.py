"""
URL configuration for digitalmarketing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from market import views
# urls.py
from django.conf import settings
from django.conf.urls.static import static
import os


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login),
    path('homepage/', views.homepage, name='homepage'),
    path('userhomepage/', views.userhomepage, name='userhomepage'),
    path('campaign_details/', views.campaign_details, name='campaign_details'),
    path('viewclientdetails/', views.viewclientdetails, name='viewclientdetails'),
    path('clientform/', views.get_client_data, name='clientform'),
    path('login/', views.login, name='login'),
    path('taskcreation/', views.taskcreation, name='taskcreation'),
    path('taskdata/', views.taskdata, name='taskdata'),
    path('u_report/', views.u_report, name='report'),
    path('reportdata/', views.reportdata, name='reportdata'),

    path('taskcreation_user/', views.taskcreation_user, name='taskcreation_user'),
    path('report_user/', views.report_user, name='report_user')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)