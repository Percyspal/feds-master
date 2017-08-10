from django.conf.urls import url
from .views import create_project, show_project, edit_project, delete_project

app_name = 'projects'
urlpatterns = [
   url(r'^(?P<id>[0-9]+)/$', show_project),
   url(r'^new/$', create_project, name='create_project'),
   url(r'^(?P<id>[0-9]+)/edit$', edit_project),
   url(r'^(?P<id>[0-9]+)/delete$', delete_project),
]
