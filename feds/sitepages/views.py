from django.http import HttpResponse, Http404
from .models import SitePage
from projects.views import list_projects
from django.shortcuts import render, get_object_or_404


def home(request):
    """
    User asked for home page.
    """
    if request.user.is_authenticated():
        # If the user is logged in, show a list of projects.
        return list_projects(request)
    return site_page(request, 'home')


def site_page(request, slug):
    """
    Show page with a given slug.
    :param request: Request object.
    :param slug: Slug to find matching field in DB, e.g., about_us
    :return: Response.
    """
    page = get_object_or_404(SitePage, slug=slug)
    # Error if page has been blocked.
    if page.status == 'blocked':
        raise Http404('Page not found')
    return render(request, 'sitepages/sitepage.html', {
        'page_title': page.title,
        'content': page.content,
    })
