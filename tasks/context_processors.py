from .models import Team, Project


def user_teams_and_projects(request):
    context = {
        'user_teams': [],
        'user_projects': []
    }

    if request.user.is_authenticated:
        context['user_teams'] = Team.objects.filter(members=request.user)
        context['user_projects'] = Project.objects.filter(teams__members=request.user).distinct()

    return context
