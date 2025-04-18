from django.contrib import admin
from .models import Task, Project, Team, Tag, VerificationCode


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'project', 'deadline', 'created_at')
    list_filter = ('status', 'priority', 'project', 'tags')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('assigned_to', 'created_by')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_members_count')
    filter_horizontal = ('members', 'projects')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


admin.site.register(Task, TaskAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(VerificationCode)
