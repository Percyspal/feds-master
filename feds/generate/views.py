from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render, get_object_or_404

from generate.feds_generator import FedsGenerator
from projects.models import ProjectDb
from projects.read_write_project import read_project


def generate(request, project_id):
    # Check that the user has view access.
    if not user_can_generate(request, project_id):
        return HttpResponseForbidden()
    try:
        generator = FedsGenerator(project_id)
    except Exception as e:
        return HttpResponseServerError(
            'Server error: {message}'.format(message=e.__str__()))



    # Create a temp dir.

    # Save project description file.


@login_required
def user_can_generate(request, project_id):
    # Check whether the user has permission.
    # TODO: replace with permission check?
    # Is the owner of the project, or is staff?
    current_user = request.user
    project_db = get_object_or_404(ProjectDb, pk=project_id)
    project_owner = project_db.user
    if current_user == project_owner:
        return True
    if current_user.is_staff():
        return True
    return False


def create_valid_customer_table()
