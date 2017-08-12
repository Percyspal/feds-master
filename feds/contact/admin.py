from django.contrib import admin
from .models import ContactFormMessage


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('contact_name','contact_email','when_sent')
    search_fields = ('contact_name', 'contact_email', 'message')
    date_hierarchy = ('when_sent')

admin.site.register(ContactFormMessage, ContactMessageAdmin)
