from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from datetime import timedelta

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#000000")
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return self.name
    
    def task_count(self):
        return self.tasks.count()
    
    def active_task_count(self):
        return self.tasks.exclude(status='done').count()


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекти'
    
    def __str__(self):
        return self.name
    
    def get_tasks_count(self):
        return self.tasks.count()
    
    def get_tasks_by_status(self, status):
        return self.tasks.filter(status=status).count()
    
    def get_progress_percentage(self):
        total = self.get_tasks_count()
        if total > 0:
            done = self.get_tasks_by_status('done')
            return int((done / total) * 100)
        return 0


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='teams')
    projects = models.ManyToManyField(Project, related_name='teams', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Команда'
        verbose_name_plural = 'Команди'
    
    def __str__(self):
        return self.name
    
    def get_members_count(self):
        return self.members.count()
    
    def get_projects_count(self):
        return self.projects.count()
    
    def get_active_tasks_count(self):
        projects = self.projects.all()
        tasks_count = 0
        for project in projects:
            tasks_count += project.tasks.exclude(status='done').count()
        return tasks_count


class Task(models.Model):
    STATUS_CHOICES = [
        ('to_do', 'До виконання'),
        ('in_progress', 'В процесі'),
        ('done', 'Виконано'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Низький'),
        ('medium', 'Середній'),
        ('high', 'Високий'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    deadline = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    tags = models.ManyToManyField('Tag', blank=True, related_name='tasks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def is_overdue(self):
        if self.deadline and self.status != 'done':
            now = timezone.now()
            today_start = timezone.datetime.combine(now.date(), timezone.datetime.min.time())
            today_start = timezone.make_aware(today_start)
            return self.deadline < today_start
        return False
    
    def days_until_deadline(self):
        if not self.deadline:
            return None
        
        now = timezone.now()
        if self.is_overdue():
            return (now - self.deadline).days * -1
        
        return (self.deadline - now).days
    
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})


class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Код підтвердження'
        verbose_name_plural = 'Коди підтвердження'
    
    @classmethod
    def generate_code(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        return not self.is_used and self.created_at > timezone.now() - timedelta(hours=24)
