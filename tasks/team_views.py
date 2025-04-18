from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse

from .models import Team, Task
from .forms import TeamForm
from .mixins import EntityFormMixin, DeleteConfirmationMixin, OptimizedQuerySetMixin


class TeamListView(LoginRequiredMixin, OptimizedQuerySetMixin, ListView):
    model = Team
    template_name = 'tasks/team_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        return self.get_optimized_team_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_teams'] = self.get_optimized_team_queryset().filter(members=user)
        return context


class TeamDetailView(LoginRequiredMixin, OptimizedQuerySetMixin, DetailView):
    model = Team
    template_name = 'tasks/team_detail.html'
    context_object_name = 'team'

    def get_queryset(self):
        return self.get_optimized_team_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object
        user = self.request.user

        context['is_member'] = user in team.members.all()

        projects = team.projects.all().prefetch_related('tasks')

        projects_with_stats = []
        for project in projects:
            task_stats = self.get_optimized_task_queryset().filter(project=project).aggregate(
                todo_count=Count('id', filter=Q(status='to_do')),
                in_progress_count=Count('id', filter=Q(status='in_progress')),
                done_count=Count('id', filter=Q(status='done')),
                total_count=Count('id')
            )

            progress = 0
            if task_stats['total_count'] > 0:
                progress = int((task_stats['done_count'] / task_stats['total_count']) * 100)

            projects_with_stats.append({
                'project': project,
                'stats': task_stats,
                'progress': progress
            })

        context['projects_with_stats'] = projects_with_stats

        project_ids = [project.id for project in projects]
        team_tasks = self.get_optimized_task_queryset().filter(project_id__in=project_ids)

        team_tasks_stats = team_tasks.aggregate(
            total=Count('id'),
            todo=Count('id', filter=Q(status='to_do')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            done=Count('id', filter=Q(status='done'))
        )

        context['team_tasks_stats'] = team_tasks_stats

        context['members'] = team.members.all()

        context['recent_tasks'] = team_tasks.order_by('-updated_at')[:5]

        return context


class TeamCreateView(LoginRequiredMixin, EntityFormMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'tasks/team_form.html'
    success_url = reverse_lazy('team_list')
    entity_name = 'команда'
    context_object_name = 'team'

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user not in self.object.members.all():
            self.object.members.add(self.request.user)
        return response


class TeamUpdateView(LoginRequiredMixin, EntityFormMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'tasks/team_form.html'
    entity_name = 'команда'
    context_object_name = 'team'

    def get_success_url(self):
        return reverse('team_detail', kwargs={'pk': self.object.pk})


class TeamDeleteView(LoginRequiredMixin, DeleteConfirmationMixin, DeleteView):
    model = Team
    template_name = 'tasks/team_confirm_delete.html'
    success_url = reverse_lazy('team_list')
    entity_name = 'команда'

    def check_delete_permission(self, team, user):
        return True
