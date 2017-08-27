from django.conf.urls import url
from .views import generate

app_name = 'generate'
urlpatterns = [
   url(r'^(?P<project_id>[0-9]+)/$', generate, name='generate'),
]
