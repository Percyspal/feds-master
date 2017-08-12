from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import feds_logout_view, feds_login_view, \
    feds_password_change, register, user_edit, user_deets


app_name = 'accounts'
urlpatterns = [
    # login / logout urls
    url(r'^login/$', feds_login_view, name='login'),
    url(r'^logout/$', feds_logout_view, name='logout'),
    # url(r'^logout-then-login/$', auth_views.logout_then_login, name='logout_then_login'),
    # change password urls
    url(r'^change-password/$',
        feds_password_change,
        {
            'post_change_redirect': 'accounts:password_change_done',
            'template_name': 'registration/change_password.html',
        },
        name='password_change'),
    url(r'^change-password-done/$',
        auth_views.password_change_done,
        {
            'template_name': 'registration/change_password_done.html',
        },
        name='password_change_done'
        ),
    url(r'^register/$',
        register,
        name='register'
        ),
    url(r'^edit/$', user_edit, name='user_edit'),
    url(r'^deets/$', user_deets, name='user_deets'),
]
