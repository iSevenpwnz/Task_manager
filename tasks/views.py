from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Task, Tag, Project, Team

from .task_views import (
    TaskListView, TaskDetailView, TaskCreateView,
    TaskUpdateView, TaskDeleteView, TaskCompleteView,
    MyTasksView, TagTasksView, TagListView
)

from .project_views import (
    ProjectListView, ProjectDetailView, ProjectCreateView,
    ProjectUpdateView, ProjectDeleteView, ProjectsDashboardView
)

from .team_views import (
    TeamListView, TeamDetailView, TeamCreateView,
    TeamUpdateView, TeamDeleteView
)

from .auth_views import (
    LoginView, LogoutView, RegisterView, VerifyCodeView
)

from .mixins import TaskQuerysetMixin, OptimizedQuerySetMixin

class IndexView(LoginRequiredMixin, OptimizedQuerySetMixin, TemplateView):
    template_name = 'tasks/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_users'] = User.objects.count()
        context['num_projects'] = Project.objects.count()
        context['num_tasks'] = Task.objects.count()
        context['num_teams'] = Team.objects.count()
        context['num_tags'] = Tag.objects.count()
        context['tasks_by_status'] = dict(Task.objects.values_list('status').annotate(count=Count('id')))
        context['recent_tasks'] = self.get_optimized_task_queryset().order_by('-created_at')[:5]
        return context

class TaskStatsDashboardView(LoginRequiredMixin, TaskQuerysetMixin, View):
    def get_context_data(self):
        return self.get_stats()

    def get_stats(self):
        user = self.request.user
        today = timezone.now().date()
        week_ago = timezone.now() - timedelta(days=7)

        today_start = timezone.datetime.combine(today, timezone.datetime.min.time())
        today_start = timezone.make_aware(today_start)
        today_end = timezone.datetime.combine(today, timezone.datetime.max.time())
        today_end = timezone.make_aware(today_end)

        base_queryset = self.get_optimized_task_queryset().filter(assigned_to=user)

        task_stats = base_queryset.aggregate(
            assigned_tasks_count=Count('id'),
            completed_tasks_count=Count('id', filter=Q(status='done'))
        )

        not_done_queryset = base_queryset.filter(~Q(status='done'))

        urgency_stats = not_done_queryset.aggregate(
            due_today_count=Count('id', filter=Q(deadline__gte=today_start, deadline__lte=today_end)),
            overdue_count=Count('id', filter=Q(deadline__lt=today_start))
        )

        weekly_stats = base_queryset.filter(
            status='done',
            updated_at__gte=week_ago
        ).aggregate(
            completed_last_week=Count('id')
        )

        return {
            'assigned_tasks_count': task_stats['assigned_tasks_count'] or 0,
            'completed_tasks_count': task_stats['completed_tasks_count'] or 0,
            'due_today_count': urgency_stats['due_today_count'] or 0,
            'overdue_tasks_count': urgency_stats['overdue_count'] or 0,
            'completed_last_week': weekly_stats['completed_last_week'] or 0
        }

class TaskListsDashboardView(LoginRequiredMixin, TaskQuerysetMixin, View):
    def get_context_data(self):
        return self.get_stats()

    def get_stats(self):
        user = self.request.user

        user_tasks = self.get_user_tasks(user)

        in_progress_tasks = [task for task in user_tasks if task.status == 'in_progress']
        in_progress_tasks.sort(key=lambda task: task.deadline if task.deadline else timezone.now() + timedelta(days=365))

        return {
            'in_progress_tasks': in_progress_tasks[:5],
            'urgent_tasks': self.get_urgent_tasks(user)[:5],
            'recent_tasks': self.get_recent_tasks(user, 10)
        }

class DashboardView(LoginRequiredMixin, OptimizedQuerySetMixin, TemplateView):
    template_name = 'tasks/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        project_view = ProjectsDashboardView()
        project_view.request = self.request

        task_stats_view = TaskStatsDashboardView()
        task_stats_view.request = self.request

        task_lists_view = TaskListsDashboardView()
        task_lists_view.request = self.request

        # Отримуємо дані з усіх представлень напряму
        context.update(project_view.get_context_data())
        context.update(task_stats_view.get_context_data())
        context.update(task_lists_view.get_context_data())

        # Переконуємося, що всі завдання містять метод is_overdue
        for task in context.get('urgent_tasks', []):
            if not hasattr(task, 'is_overdue'):
                now = timezone.now()
                today_start = timezone.datetime.combine(now.date(), timezone.datetime.min.time())
                today_start = timezone.make_aware(today_start)
                task.is_overdue = task.deadline and task.deadline < today_start and task.status != 'done'

        # Гарантуємо, що всі необхідні змінні існують в контексті
        if 'assigned_tasks_count' not in context:
            context['assigned_tasks_count'] = 0
        if 'completed_tasks_count' not in context:
            context['completed_tasks_count'] = 0
        if 'due_today_count' not in context:
            context['due_today_count'] = 0
        if 'overdue_tasks_count' not in context:
            context['overdue_tasks_count'] = 0
        if 'completed_last_week' not in context:
            context['completed_last_week'] = 0
        if 'projects_count' not in context:
            context['projects_count'] = 0
        if 'active_projects_count' not in context:
            context['active_projects_count'] = 0

        return context
