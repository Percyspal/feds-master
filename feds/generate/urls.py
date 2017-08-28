from django.conf.urls import url
from .views import generate, delete_archive

app_name = 'generate'
urlpatterns = [
   url(r'^$', generate, name='generate'),
   url(r'^ajax/deletearchive/$', delete_archive, name='delete_archive'),
]
