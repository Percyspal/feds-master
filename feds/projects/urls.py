from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import create_project


app_name = 'projects'
urlpatterns = [
    # login / logout urls
   url(r'^create-project/$', create_project, name='create_project'),
#    url(r'^login/$', feds_login_view, name='login'),
#     url(r'^change-password/$',
#         feds_password_change,
#         {
#             'post_change_redirect': 'accounts:password_change_done',
#             'template_name': 'registration/change_password.html',
#         },
#         name='password_change'),
]
