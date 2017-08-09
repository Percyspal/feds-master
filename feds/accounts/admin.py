from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'web_site']

admin.site.register(Profile, ProfileAdmin)
