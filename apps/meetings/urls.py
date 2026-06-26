from django.urls import path

from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.MeetingListView.as_view(), name='meeting_list'),
    path('add/', views.MeetingCreateView.as_view(), name='meeting_create'),
    path('<int:pk>/', views.MeetingDetailView.as_view(), name='meeting_detail'),
    path('<int:pk>/edit/', views.MeetingUpdateView.as_view(), name='meeting_update'),
    path('<int:pk>/sessions/add/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/close/', views.SessionCloseView.as_view(), name='session_close'),
    path('sessions/<int:pk>/notes/add/', views.QuickNoteView.as_view(), name='quick_note'),
    path('notes/<int:pk>/clarify/', views.NoteClarifyView.as_view(), name='note_clarify'),
]
