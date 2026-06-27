from django.contrib import admin

from .models import (
    AreaOfResponsibility, Context, Meeting, NextAction,
    Person, Project, Reference, SomedayMaybe, Tag, WaitingFor,
)

admin.site.register(AreaOfResponsibility)
admin.site.register(Context)
admin.site.register(Tag)
admin.site.register(Person)
admin.site.register(Meeting)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'deadline', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'desired_outcome']


@admin.register(NextAction)
class NextActionAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'defer_until', 'scheduled_for', 'deadline']
    list_filter = ['status']
    search_fields = ['title']
    filter_horizontal = ['contexts']


@admin.register(WaitingFor)
class WaitingForAdmin(admin.ModelAdmin):
    list_display = ['title', 'person', 'status', 'expected_by', 'follow_up_on']
    list_filter = ['status']


admin.site.register(SomedayMaybe)
admin.site.register(Reference)
