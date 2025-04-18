from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import Task, Project, Team


def get_user_projects(user):
    user_teams = user.teams.all().prefetch_related('projects')
    user_projects = set()

    for team in user_teams:
        for project in team.projects.all():
            user_projects.add(project)

    return list(user_projects)


def get_project_stats(projects):
    stats = {
        'projects_count': len(projects),
        'active_projects_count': 0
    }

    for project in projects:
        if Task.objects.filter(project=project).exclude(status='done').exists():
            stats['active_projects_count'] += 1

    return stats


def get_user_task_stats(user):
    task_stats = Task.objects.filter(assigned_to=user).aggregate(
        assigned_tasks_count=Count('id'),
        completed_tasks_count=Count('id', filter=Q(status='done')),
        in_progress_count=Count('id', filter=Q(status='in_progress')),
    )

    today = timezone.now().date()
    urgency_stats = Task.objects.filter(
        Q(assigned_to=user) & ~Q(status='done')
    ).aggregate(
        due_today_count=Count('id', filter=Q(deadline__date=today)),
        overdue_count=Count('id', filter=Q(deadline__lt=timezone.now())),
    )

    week_ago = timezone.now() - timedelta(days=7)
    weekly_stats = Task.objects.filter(
        assigned_to=user,
        status='done',
        updated_at__gte=week_ago
    ).aggregate(
        completed_last_week=Count('id')
    )

    stats = {**task_stats, **urgency_stats, **weekly_stats}
    return stats


def get_user_tasks_by_category(user):
    today = timezone.now().date()

    tasks = {
        'in_progress_tasks': Task.objects.filter(
            assigned_to=user,
            status='in_progress'
        ).select_related('project').order_by('deadline')[:5],

        'urgent_tasks': Task.objects.filter(
            Q(assigned_to=user) &
            ~Q(status='done') &
            (Q(deadline__date=today) | Q(deadline__lt=timezone.now()))
        ).select_related('project').order_by('deadline')[:5],

        'recent_tasks': Task.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).select_related('project', 'assigned_to').order_by('-updated_at')[:10]
    }

    return tasks
