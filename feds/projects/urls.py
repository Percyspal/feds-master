from django.conf.urls import url
from .views import create_project, show_project, \
    delete_project, clone_project, request_setting_widget, save_setting, \
    load_setting_deets, request_title_description_widget, save_title_description

app_name = 'projects'
urlpatterns = [
   url(r'^new/$', create_project, name='create_project'),
   url(r'^(?P<project_id>[0-9]+)/$', show_project, name='show_project'),
   url(r'^(?P<project_id>[0-9]+)/delete$', delete_project,
       name='delete_project'),
   url(r'^(?P<project_id>[0-9]+)/clone$', clone_project, name='clone_project'),
   url(r'^ajax/requestsettingwidget/$', request_setting_widget,
       name='request_setting_widget'),
   url(r'^ajax/savesetting/$', save_setting, name='save_setting'),
   url(r'^ajax/savetitledescription/$', save_title_description,
       name='save_title_description'),
   url(r'^ajax/loadsettingdeets/$', load_setting_deets,
       name='load_setting_deets'),
   url(r'^ajax/requesttitledescriptionwidget/$',
       request_title_description_widget,
       name='request_title_description_widget'),
]
