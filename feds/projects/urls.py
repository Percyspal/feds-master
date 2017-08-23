from django.conf.urls import url
from .views import create_project, show_project, edit_project, \
   delete_project, clone_project, request_setting_widget

app_name = 'projects'
urlpatterns = [
   url(r'^new/$', create_project, name='create_project'),
   url(r'^(?P<project_id>[0-9]+)/$', show_project, name='show_project'),
   url(r'^(?P<project_id>[0-9]+)/edit$', edit_project, name='edit_project'),
   url(r'^(?P<project_id>[0-9]+)/delete$', delete_project,
       name='delete_project'),
   url(r'^(?P<project_id>[0-9]+)/clone$', clone_project, name='clone_project'),
   url(r'^ajax/requestsettingwidget/$', request_setting_widget,
       name='request_setting_widget'),

]
