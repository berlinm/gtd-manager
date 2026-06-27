from django.urls import path

from . import views

app_name = 'gtd'

urlpatterns = [
    # Next actions
    path('actions/', views.NextActionListView.as_view(), name='next_actions'),
    path('actions/today/', views.TodayView.as_view(), name='today'),
    path('actions/add/', views.NextActionCreateView.as_view(), name='action_add'),
    path('actions/<int:pk>/edit/', views.NextActionUpdateView.as_view(), name='action_edit'),
    path('actions/<int:pk>/done/', views.NextActionDoneView.as_view(), name='action_done'),
    path('actions/<int:pk>/cancel/', views.NextActionCancelView.as_view(), name='action_cancel'),
    path('actions/<int:pk>/delegate/', views.DelegateActionView.as_view(), name='action_delegate'),
    # Projects
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('projects/add/', views.ProjectCreateView.as_view(), name='project_add'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    # Waiting For
    path('waiting/', views.WaitingForListView.as_view(), name='waiting_for_list'),
    path('waiting/add/', views.WaitingForCreateView.as_view(), name='waiting_for_add'),
    path('waiting/<int:pk>/edit/', views.WaitingForUpdateView.as_view(), name='waiting_for_edit'),
    path('waiting/<int:pk>/receive/', views.WaitingForReceiveView.as_view(), name='waiting_for_receive'),
    path('waiting/<int:pk>/cancel/', views.WaitingForCancelView.as_view(), name='waiting_for_cancel'),
    path('waiting/<int:pk>/followup/', views.WaitingForFollowUpView.as_view(), name='waiting_for_followup'),
    # Someday / Maybe
    path('someday/', views.SomedayMaybeListView.as_view(), name='someday_list'),
    path('someday/add/', views.SomedayMaybeCreateView.as_view(), name='someday_add'),
    path('someday/<int:pk>/edit/', views.SomedayMaybeUpdateView.as_view(), name='someday_edit'),
    path('someday/<int:pk>/promote/', views.SomedayPromoteView.as_view(), name='someday_promote'),
    # Reference
    path('reference/', views.ReferenceListView.as_view(), name='reference_list'),
    path('reference/add/', views.ReferenceCreateView.as_view(), name='reference_add'),
    path('reference/<int:pk>/', views.ReferenceDetailView.as_view(), name='reference_detail'),
    path('reference/<int:pk>/edit/', views.ReferenceUpdateView.as_view(), name='reference_edit'),
    # Areas
    path('areas/<int:pk>/', views.AreaDetailView.as_view(), name='area_detail'),
    # Agenda
    path('agenda/', views.AgendaListView.as_view(), name='agenda_list'),
    path('agenda/add/', views.AgendaItemCreateView.as_view(), name='agenda_item_add'),
    path('agenda/<int:pk>/edit/', views.AgendaItemUpdateView.as_view(), name='agenda_item_edit'),
    path('agenda/<int:pk>/done/', views.AgendaItemDoneView.as_view(), name='agenda_item_done'),
]
