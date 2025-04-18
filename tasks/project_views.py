from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Project, Task
from .forms import ProjectForm
from .mixins import ProjectAccessMixin, EntityFormMixin, DeleteConfirmationMixin, OptimizedQuerySetMixin


class ProjectListView(LoginRequiredMixin, OptimizedQuerySetMixin, ListView):
    model = Project
    template_name = 'tasks/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return self.get_optimized_project_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = self.get_queryset()
        user = self.request.user
        user_teams = user.teams.all().prefetch_related('projects')

        context['user_projects'] = self.get_optimized_project_queryset().filter(teams__in=user_teams).distinct()

        projects_with_stats = []
        for project in projects:
            task_stats = Task.objects.filter(project=project).aggregate(
                todo_count=Count('id', filter=Q(status='to_do')),
                in_progress_count=Count('id', filter=Q(status='in_progress')),
                done_count=Count('id', filter=Q(status='done')),
                total_count=Count('id')
            )

            stats = {
                'project': project,
                'todo_count': task_stats['todo_count'],
                'in_progress_count': task_stats['in_progress_count'],
                'done_count': task_stats['done_count'],
                'total_count': task_stats['total_count'],
                'is_user_project': project in context['user_projects']
            }
            projects_with_stats.append(stats)

        context['projects_with_stats'] = projects_with_stats
        return context


class ProjectDetailView(LoginRequiredMixin, ProjectAccessMixin, OptimizedQuerySetMixin, DetailView):
    model = Project
    template_name = 'tasks/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return self.get_optimized_project_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        user = self.request.user

        context['has_team_access'] = self.check_project_access(project, user)

        tasks = self.get_optimized_task_queryset().filter(project=project)

        task_stats = tasks.aggregate(
            todo_count=Count('id', filter=Q(status='to_do')),
            in_progress_count=Count('id', filter=Q(status='in_progress')),
            done_count=Count('id', filter=Q(status='done')),
            total_count=Count('id')
        )

        context.update(task_stats)

        context['tasks'] = tasks
        context['tasks_todo'] = [task for task in tasks if task.status == 'to_do']
        context['tasks_in_progress'] = [task for task in tasks if task.status == 'in_progress']
        context['tasks_done'] = [task for task in tasks if task.status == 'done']

        return context


class ProjectCreateView(LoginRequiredMixin, EntityFormMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    success_url = reverse_lazy('project_list')
    entity_name = 'проект'
    context_object_name = 'project'


class ProjectUpdateView(LoginRequiredMixin, EntityFormMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    entity_name = 'проект'
    context_object_name = 'project'

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})


@method_decorator(csrf_exempt, name='dispatch')
class ProjectDeleteView(LoginRequiredMixin, DeleteConfirmationMixin, DeleteView):
    model = Project
    template_name = 'tasks/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')
    entity_name = 'проект'

    def check_delete_permission(self, project, user):
        return True


class ProjectsDashboardView(LoginRequiredMixin, ProjectAccessMixin, View):

    def get_context_data(self, **kwargs):
        user = self.request.user

        user_projects = self.get_user_projects(user)

        project_stats = {
            'projects_count': len(user_projects),
            'active_projects_count': Project.objects.filter(
                id__in=[p.id for p in user_projects],
                tasks__status__in=['to_do', 'in_progress']
            ).distinct().count()
        }

        return {
            'projects': user_projects,
            'projects_count': project_stats['projects_count'],
            'active_projects_count': project_stats['active_projects_count']
        }
