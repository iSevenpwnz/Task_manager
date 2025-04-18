from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta

from .models import Task, Project, Team, Tag


class OptimizedQuerySetMixin:
    @staticmethod
    def get_optimized_task_queryset():
        return Task.objects.select_related(
            'project',
            'assigned_to',
            'created_by'
        ).prefetch_related('tags')

    @staticmethod
    def get_optimized_project_queryset():
        return Project.objects.prefetch_related(
            'tasks',
            'teams'
        )

    @staticmethod
    def get_optimized_team_queryset():
        return Team.objects.prefetch_related(
            'members',
            'projects'
        )


class TaskPermissionMixin:
    def get_task_permissions(self, task, user):
        is_creator = task.created_by == user
        is_assignee = task.assigned_to == user

        has_team_access = False
        if task.project:
            user_teams = user.teams.all().prefetch_related('projects')
            for team in user_teams:
                if task.project in team.projects.all():
                    has_team_access = True
                    break

        can_edit = is_creator or is_assignee
        can_delete = is_creator

        return {
            'is_creator': is_creator,
            'is_assignee': is_assignee,
            'has_team_access': has_team_access,
            'can_edit': can_edit,
            'can_delete': can_delete
        }


class ProjectAccessMixin:
    def check_project_access(self, project, user):
        user_teams = user.teams.all().prefetch_related('projects')
        for team in user_teams:
            if project in team.projects.all():
                return True
        return False

    def get_user_projects(self, user):
        user_teams = user.teams.all().prefetch_related('projects')
        user_projects = set()
        for team in user_teams:
            for project in team.projects.all():
                user_projects.add(project)
        return list(user_projects)


class EntityFormMixin:
    entity_name = 'element'
    success_url_name = None
    parent_lookup_field = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['title'] = f'Редагувати {self.entity_name}'
            context[self.context_object_name] = self.object
        else:
            context['title'] = f'Створити новий {self.entity_name}'

        context['breadcrumbs'] = self.get_breadcrumbs()
        return context

    def get_breadcrumbs(self):
        return []

    def form_valid(self, form):
        action = 'оновлено' if self.object else 'створено'
        messages.success(self.request, f"{self.entity_name.capitalize()} успішно {action}")
        return super().form_valid(form)

    def get_success_url(self):
        if self.success_url_name:
            if self.object and hasattr(self.object, 'pk'):
                return reverse(self.success_url_name, kwargs={'pk': self.object.pk})
            else:
                return reverse(self.success_url_name)
        return super().get_success_url()


class TaskQuerysetMixin(OptimizedQuerySetMixin):
    @staticmethod
    def get_tasks_by_status(queryset, status=None):
        if status:
            return queryset.filter(status=status)
        return queryset

    @staticmethod
    def get_user_tasks(user, status=None):
        queryset = OptimizedQuerySetMixin.get_optimized_task_queryset().filter(
            Q(created_by=user) | Q(assigned_to=user)
        )

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    @staticmethod
    def get_urgent_tasks(user):
        now = timezone.now()
        today = now.date()
        today_start = timezone.datetime.combine(today, timezone.datetime.min.time())
        today_start = timezone.make_aware(today_start)
        today_end = timezone.datetime.combine(today, timezone.datetime.max.time())
        today_end = timezone.make_aware(today_end)

        base_queryset = OptimizedQuerySetMixin.get_optimized_task_queryset().filter(
            Q(created_by=user) | Q(assigned_to=user),
            status__in=['to_do', 'in_progress']
        )

        overdue_tasks = base_queryset.filter(deadline__lt=today_start)

        today_tasks = base_queryset.filter(
            deadline__gte=today_start,
            deadline__lte=today_end
        )

        return (overdue_tasks | today_tasks).order_by('deadline')

    @staticmethod
    def get_recent_tasks(user, limit=10):
        return OptimizedQuerySetMixin.get_optimized_task_queryset().filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).order_by('-updated_at')[:limit]


class FormUserKwargsMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class OwnershipMixin:
    ownership_field = 'created_by'

    def form_valid(self, form):
        if hasattr(form.instance, self.ownership_field):
            setattr(form.instance, self.ownership_field, self.request.user)
        return super().form_valid(form)


class FilterMixin:
    filter_form_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_filter_form()

        if form and form.is_valid():
            return self.apply_filters(queryset, form.cleaned_data)
        return queryset

    def get_filter_form(self):
        if not self.filter_form_class:
            return None

        return self.filter_form_class(self.request.GET, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.filter_form_class:
            context['filter_form'] = self.get_filter_form()

            context['projects'] = Project.objects.all()
            context['tags'] = Tag.objects.all()

        return context

    def apply_filters(self, queryset, cleaned_data):
        return queryset


class DeleteConfirmationMixin:
    entity_name = 'element'
    redirect_url = None

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        if hasattr(self, 'check_delete_permission'):
            if not self.check_delete_permission(self.object, request.user):
                messages.error(request, f"У вас немає прав на видалення цього {self.entity_name}")
                return HttpResponseRedirect(success_url)

        self.object.delete()
        messages.success(request, f"{self.entity_name.capitalize()} успішно видалено")
        return HttpResponseRedirect(success_url)


class StatsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_stats())
        return context

    def get_stats(self):
        return {}
