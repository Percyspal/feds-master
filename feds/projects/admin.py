from django.contrib import admin
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    # Fields to show on the list.
    list_display = ['user', 'title', 'slug', 'created']
    # Let admin user filter by these fields.
    list_filter = ['user', 'title']

admin.site.register(Project, ProjectAdmin)
