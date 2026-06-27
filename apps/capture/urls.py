from django.urls import path

from . import views

app_name = 'capture'

urlpatterns = [
    path('', views.InboxView.as_view(), name='inbox'),
    path('capture/', views.QuickCaptureView.as_view(), name='quick_capture'),
    path('<int:pk>/clarify/', views.ClarifyView.as_view(), name='clarify'),
]
