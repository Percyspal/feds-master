import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseServerError, \
    HttpResponse
from django.shortcuts import get_object_or_404

from generate.feds_generator import FedsGenerator
from projects.models import ProjectDb


def generate(request, project_id):
    # Check that the user has view access.
    if not user_can_generate(request, project_id):
        return HttpResponseForbidden()
    try:
        generator = FedsGenerator(project_id)
        # Create each of the tables.
        generator.create_customer_table()
        # First pass: correct data with given settings.
        generator.create_customers()
        # Create a temp dir.
        module_dir = os.path.dirname(__file__)  # get current directory
        export_dir_path = os.path.join(module_dir, 'generated/project' + str(project_id))
        # Make the dir if it does not exist.
        if not os.path.exists(export_dir_path):
            os.makedirs(export_dir_path)
        # Erase all files in it.
        erase_files_in_dir(export_dir_path)
        # Save project description file.
        # Save customer file.
        generator.save_customer_data(export_dir_path, 'customers.csv')

    except Exception as e:
        return HttpResponseServerError(
            'Server error: {message}'.format(message=e.__str__()))


    return HttpResponse('Something happened.')


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


def erase_files_in_dir(dir_path):
    for the_file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            raise IOError('Could not erase "{fp}"'.format(fp=file_path))
