from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from .models import Task, Tag, Project
from .forms import TaskForm, TaskFilterForm, TagForm
from .mixins import (
    TaskPermissionMixin, TaskQuerysetMixin,
    EntityFormMixin, FormUserKwargsMixin, OwnershipMixin,
    FilterMixin, DeleteConfirmationMixin, StatsMixin
)
from .services import get_user_tasks_by_category


class TaskListView(LoginRequiredMixin, FilterMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    filter_form_class = TaskFilterForm

    def get_queryset(self):
        return super().get_queryset().select_related('project', 'assigned_to', 'created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['tags'] = Tag.objects.all()
        return context

    def apply_filters(self, queryset, cleaned_data):
        status = cleaned_data.get('status')
        assigned_to = cleaned_data.get('assigned_to')
        tags = cleaned_data.get('tags')
        project = cleaned_data.get('project')

        if status:
            queryset = queryset.filter(status=status)
        if assigned_to:
            queryset = queryset.filter(assigned_to=assigned_to)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags=tag)
        if project:
            queryset = queryset.filter(project=project)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if self.request.GET.get('overdue') == 'true':
            now = timezone.now()
            today_start = timezone.datetime.combine(now.date(), timezone.datetime.min.time())
            today_start = timezone.make_aware(today_start)
            queryset = queryset.filter(
                status__in=['to_do', 'in_progress'],
                deadline__lt=today_start
            )

        if self.request.GET.get('due') == 'today':
            now = timezone.now()
            today_start = timezone.datetime.combine(now.date(), timezone.datetime.min.time())
            today_end = timezone.datetime.combine(now.date(), timezone.datetime.max.time())
            today_start = timezone.make_aware(today_start)
            today_end = timezone.make_aware(today_end)
            queryset = queryset.filter(
                deadline__gte=today_start,
                deadline__lte=today_end
            )

        return queryset

    def get_breadcrumbs(self):
        return [
            {'title': 'Список завдань'}
        ]


class TaskDetailView(LoginRequiredMixin, TaskPermissionMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        user = self.request.user

        permissions = self.get_task_permissions(task, user)
        context.update(permissions)

        context['breadcrumbs'] = self.get_breadcrumbs()
        return context

    def get_breadcrumbs(self):
        return [
            {'title': 'Список завдань', 'url': reverse('task_list')},
            {'title': self.object.title}
        ]


class TaskCreateView(LoginRequiredMixin, FormUserKwargsMixin, OwnershipMixin, EntityFormMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    entity_name = 'завдання'
    success_url_name = 'task_detail'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_breadcrumbs(self):
        return [
            {'title': 'Список завдань', 'url': reverse('task_list')},
            {'title': 'Створення завдання'}
        ]


class TaskUpdateView(LoginRequiredMixin, TaskPermissionMixin, FormUserKwargsMixin, EntityFormMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    entity_name = 'завдання'
    success_url_name = 'task_detail'

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        permissions = self.get_task_permissions(task, user)

        if not permissions['can_edit']:
            messages.error(request,
                           "Ви не можете редагувати це завдання. Редагувати може тільки творець або виконавець.")
            return redirect('task_detail', pk=task.pk)

        set_status = request.GET.get('set_status')
        if set_status in ['to_do', 'in_progress', 'done']:
            task.status = set_status
            task.save()

            status_names = {
                'to_do': 'До виконання',
                'in_progress': 'В процесі',
                'done': 'Виконано'
            }

            messages.success(request, f"Статус завдання змінено на '{status_names[set_status]}'")
            return redirect('task_detail', pk=task.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs(self):
        return [
            {'title': 'Список завдань', 'url': reverse('task_list')},
            {'title': self.object.title, 'url': reverse('task_detail', kwargs={'pk': self.object.pk})},
            {'title': 'Редагування'}
        ]


class TaskDeleteView(LoginRequiredMixin, TaskPermissionMixin, DeleteConfirmationMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    entity_name = 'завдання'

    def check_delete_permission(self, task, user):
        permissions = self.get_task_permissions(task, user)
        return permissions['can_delete']

    def get_breadcrumbs(self):
        return [
            {'title': 'Список завдань', 'url': reverse('task_list')},
            {'title': self.object.title, 'url': reverse('task_detail', kwargs={'pk': self.object.pk})},
            {'title': 'Видалення'}
        ]


class TaskCompleteView(LoginRequiredMixin, TaskPermissionMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        permissions = self.get_task_permissions(task, request.user)

        if not (permissions['is_assignee'] or permissions['is_creator']):
            messages.error(request, "Ви не можете позначити це завдання як виконане")
            return redirect('task_list')

        task.status = 'done'
        task.save()
        messages.success(request, "Завдання позначено як виконане")

        return redirect('task_detail', pk=task.pk)


class MyTasksView(LoginRequiredMixin, TaskQuerysetMixin, StatsMixin, ListView):
    model = Task
    template_name = 'tasks/my_tasks.html'

    def get_stats(self):
        user = self.request.user
        user_tasks = self.get_user_tasks(user)

        todo_tasks = self.get_tasks_by_status(user_tasks, 'to_do')
        in_progress_tasks = self.get_tasks_by_status(user_tasks, 'in_progress')
        completed_tasks = self.get_tasks_by_status(user_tasks, 'done')

        now = timezone.now()
        today_start = timezone.datetime.combine(now.date(), timezone.datetime.min.time())
        today_start = timezone.make_aware(today_start)

        overdue_tasks = user_tasks.filter(
            status__in=['to_do', 'in_progress'],
            deadline__lt=today_start
        ).order_by('deadline')

        return {
            'todo_tasks': todo_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'breadcrumbs': self.get_breadcrumbs()
        }

    def get_breadcrumbs(self):
        return [
            {'title': 'Мої завдання'}
        ]


class TagTasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        tag_id = self.kwargs.get('pk')
        return Task.objects.filter(tags__id=tag_id).select_related('project', 'assigned_to', 'created_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('pk')
        tag = get_object_or_404(Tag, pk=tag_id)
        context['tag'] = tag
        context['title'] = f'Завдання з тегом "{tag.name}"'
        context['breadcrumbs'] = self.get_breadcrumbs(tag)
        context['filter_form'] = TaskFilterForm(self.request.GET, user=self.request.user)
        return context

    def get_breadcrumbs(self, tag):
        return [
            {'title': 'Список завдань', 'url': reverse('task_list')},
            {'title': f'Тег: {tag.name}'}
        ]


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'tasks/tag_list.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.annotate(
            task_count=Count('tasks'),
            active_task_count=Count('tasks', filter=~Q(tasks__status='done'))
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TagForm()
        context['total_tasks_count'] = Task.objects.count()
        return context

    def post(self, request, *args, **kwargs):
        if 'action' in request.POST and request.POST['action'] == 'delete' and 'tag_id' in request.POST:
            tag_id = request.POST['tag_id']
            try:
                tag = Tag.objects.get(pk=tag_id)
                tag_name = tag.name
                tag.delete()
                messages.success(request, f"Тег '{tag_name}' успішно видалено")
                return redirect('tag_list')
            except Tag.DoesNotExist:
                messages.error(request, "Тег не знайдено")
                return redirect('tag_list')

        if 'tag_id' in request.POST and 'name' in request.POST and 'action' not in request.POST:
            tag_id = request.POST['tag_id']
            try:
                tag = Tag.objects.get(pk=tag_id)
                tag.name = request.POST['name']
                if 'color' in request.POST and request.POST['color']:
                    tag.color = request.POST['color']
                tag.save()
                messages.success(request, f"Тег успішно оновлено")
                return redirect('tag_list')
            except Tag.DoesNotExist:
                messages.error(request, "Тег не знайдено")
                return redirect('tag_list')

        if 'name' in request.POST:
            try:
                name = request.POST['name']
                if not name:
                    messages.error(request, "Ім'я тегу не може бути порожнім")
                    return self.get(request, *args, **kwargs)

                tag = Tag.objects.create(name=name)
                messages.success(request, "Тег успішно створено")
                return redirect('tag_list')
            except Exception as e:
                messages.error(request, f"Помилка при створенні тегу: {str(e)}")

        messages.error(request, "Помилка при створенні тегу. Перевірте чи не дублюється назва.")
        return self.get(request, *args, **kwargs)
