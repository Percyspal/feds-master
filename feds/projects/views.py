from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Project


@login_required
def list_projects(request):
    try:
        projects = Project.objects.filter(user=request.user)
    except Project.DoesNotExist:
        projects = False
    return render(
        request,
        'projects/list_projects.html',
        {'projects': projects}
    )


def create_project(request):
    return HttpResponse('Create')
