from django.urls import path
from . import views
from .views import (
    IndexView, DashboardView,
    TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView, TaskCompleteView, MyTasksView,
    ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    TeamListView, TeamDetailView, TeamCreateView, TeamUpdateView, TeamDeleteView,
    TagListView, TagTasksView
)

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('index/', IndexView.as_view(), name='index'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/complete/', TaskCompleteView.as_view(), name='task_complete'),
    path('tasks/<int:pk>/quick-update/', TaskCompleteView.as_view(), name='task_quick_update'),
    path('my-tasks/', MyTasksView.as_view(), name='my_tasks'),

    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    path('teams/', TeamListView.as_view(), name='team_list'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('teams/create/', TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/update/', TeamUpdateView.as_view(), name='team_update'),
    path('teams/<int:pk>/delete/', TeamDeleteView.as_view(), name='team_delete'),

    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tags/<int:pk>/tasks/', TagTasksView.as_view(), name='tag_tasks'),
]
