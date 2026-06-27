from django.urls import path

from . import views

app_name = 'reviews'

urlpatterns = [
    path('daily/', views.DailyReviewView.as_view(), name='daily_review'),
    path('focus/', views.FocusListView.as_view(), name='focus_list'),
    path('weekly/', views.WeeklyReviewView.as_view(), name='weekly_review'),
    path('history/', views.ReviewHistoryView.as_view(), name='review_history'),
]
