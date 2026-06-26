from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from apps.core import views as core_views

urlpatterns = [
    path('', core_views.DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('inbox/', include('apps.capture.urls', namespace='capture')),
    path('meetings/', include('apps.meetings.urls', namespace='meetings')),
    path('', include('apps.gtd.urls', namespace='gtd')),
    path('', include('apps.core.urls', namespace='core')),
    path('admin/', admin.site.urls),
]
