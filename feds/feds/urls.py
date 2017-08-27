from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from sitepages.views import home, site_page
from .views import init_database
from contact.views import contact_page

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^about-us/$', site_page, {'slug': 'about-us'},
                      name='about_us'),
                  url(r'^faqs/$', site_page, {'slug': 'faqs'}, name='faqs'),
                  url(r'^contact/$', contact_page, name='contact'),
                  url(r'^$', home, name='home'),
                  url(r'^accounts/',
                      include('accounts.urls', namespace='accounts')),
                  url(r'^projects/',
                      include('projects.urls', namespace='projects')),
                  url(r'^generate/',
                      include('generate.urls', namespace='generate')),
                  url(r'^init$', init_database),
                  # url(r'^carla$', carla),
              ] + static(settings.STATIC_URL,
                         document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    # import debug_toolbar
    # urlpatterns = [
    #                   url(r'^__debug__/', include(debug_toolbar.urls)),
    #               ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
