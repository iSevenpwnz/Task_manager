from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Task, Project, Team, Tag


class TaskForm(forms.ModelForm):
    priority = forms.CharField(
        widget=forms.HiddenInput(),
        initial='medium',
        required=False
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'deadline', 'assigned_to', 'project', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['project'].queryset = Project.objects.all()
            self.fields['assigned_to'].queryset = User.objects.all().order_by('username')

        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget,
                                                                                    forms.CheckboxSelectMultiple) and not isinstance(
                    field.widget, forms.HiddenInput):
                field.widget.attrs.update({'class': 'form-control'})


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'members', 'projects']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'members': forms.SelectMultiple(attrs={'class': 'select2'}),
            'projects': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})


class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'Всі статуси')] + list(Task.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'Всі пріоритети')] + list(Task.PRIORITY_CHOICES)

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False,
                               widget=forms.Select(attrs={'class': 'form-select'}))
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="Всі виконавці",
                                         widget=forms.Select(attrs={'class': 'form-select'}))
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False,
                                          widget=forms.SelectMultiple(attrs={'class': 'form-select select2'}))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False, empty_label="Всі проекти",
                                     widget=forms.Select(attrs={'class': 'form-select'}))
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False,
                                 widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['assigned_to'].queryset = User.objects.filter(teams__in=user.teams.all()).distinct()

            user_teams = user.teams.all().prefetch_related('projects')
            available_projects = []
            for team in user_teams:
                available_projects.extend(list(team.projects.all()))

            self.fields['project'].queryset = Project.objects.filter(
                id__in=[project.id for project in available_projects])


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введіть email'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class VerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введіть 6-значний код'})
    )


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control color-picker', 'type': 'color'})
        }
