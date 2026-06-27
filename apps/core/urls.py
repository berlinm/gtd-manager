from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('settings/areas/', views.AreaListView.as_view(), name='area_list'),
    path('settings/areas/add/', views.AreaCreateView.as_view(), name='area_add'),
    path('settings/areas/<int:pk>/edit/', views.AreaUpdateView.as_view(), name='area_edit'),
]
