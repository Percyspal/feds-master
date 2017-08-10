from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.exceptions import SuspiciousOperation
from .models import Project
from .forms import ProjectForm


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


@login_required
def show_project(request, project_id):
    # Check that the user has view access.
    if not user_can_view_project(request, project_id):
        return HttpResponseForbidden()
    # Show a project's deets.
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projects/show_project.html', {'project': project})


def user_can_view_project(request, project_id):
    # Check whether the user has access to the project.
    # TODO: replace with permission check?
    # Is the owner of the project, or is staff.
    current_user = request.user
    project = get_object_or_404(Project, pk=project_id)
    project_owner = project.user
    if current_user == project_owner:
        return True
    if current_user.is_staff():
        return True
    return False


def user_can_delete_project(request, project_id):
    return user_can_view_project(request, project_id)


def user_can_edit_project(request, project_id):
    return user_can_view_project(request, project_id)


def user_can_create_project(request):
    # Any user can create a project.
    return True


@login_required
def create_project(request):
    """ Create a new project. Send 'create' operation to create_edit view. """
    if not user_can_create_project(request):
        return HttpResponseForbidden()
    return create_edit_project(request, 'new')


@login_required
def edit_project(request, project_id):
    """ Edit a project. Send 'edit' operation and the project's id to create_edit view. """
    if not user_can_edit_project(request, project_id):
        return HttpResponseForbidden()
    return create_edit_project(request, 'edit', project_id)


@login_required
def create_edit_project(request, operation, project_id=0):
    """ Create or edit a project, depending on the operation. """
    if request.method == 'GET':
        # A GET is either for a new project, or to edit one.
        if operation == 'edit':
            # Edit, so load current data.
            project = get_object_or_404(Project, pk=project_id)
            form = ProjectForm(instance=project)
        else:
            # Create MT project form.
            form = ProjectForm()
        return render(
            request,
            'projects/create_edit_project.html',
            {'operation': operation,
             'project_id': project_id,  # id is passed for making the Cancel link.
             'form': form,
             }
        )
    if request.method != 'POST':
        raise SuspiciousOperation('Bad HTTP op in create_edit_project: {op}'.format(op=request.method))
    # It's a POST.
    form = ProjectForm(request.POST)
    # Apply form validation. This does not apply model validation.
    if form.is_valid():
        if operation == 'edit':
            # Edit, so load current data.
            project = Project.objects.get(pk=id)
        else:
            # New project, create MT object.
            project = Project()
        # Copy data from form fields into model instance.
        cleaned_data = form.cleaned_data
        project.user = request.user
        project.title = cleaned_data['title']
        project.description = cleaned_data['description']
        project.slug = cleaned_data['slug']
        project.save()
        # For new record, save will add the new id to the model instance.
        # TODO: Replace explicit link.
        return redirect('/projects/{project_id}'.format(project_id=project.pk))
    # There were data errors.
    # Render the form again.
    return render(
        request,
        'projects/create_edit_project.html',
        {'operation': operation,
         'project_id': project_id, 'form': form}
    )


@login_required
def delete_project(request, project_id):
    """ Delete a project. """
    if not user_can_delete_project(request, project_id):
        return HttpResponseForbidden()
    project = get_object_or_404(Project, pk=project_id)
    # TODO: confirm delete.
    project.delete()
    # TODO: replace explicit link.
    return redirect('/projects/')
