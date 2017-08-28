import os
import zipfile

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseServerError, \
    HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from generate.feds_generator import FedsGenerator
from projects.models import ProjectDb


def generate(request):
    # Get the project id from the post.
    project_id = request.POST.get('projectid', None)
    if project_id is None:
        return JsonResponse({'status': 'Error: project id missing'})
    # Check that the user has generate access.
    if not user_can_generate(request, project_id):
        return JsonResponse({'status': 'Error: access denied'})
    try:
        generator = FedsGenerator(project_id)
        # Create each of the tables.
        generator.create_customer_table()
        # First pass: correct data with given settings.
        generator.create_customers()
        # Create a temp dir.
        module_dir = os.path.dirname(__file__)  # get current directory
        export_dir_path = os.path.join(module_dir,
                                       'generated/project' + str(project_id))
        # Make the dir if it does not exist.
        if not os.path.exists(export_dir_path):
            os.makedirs(export_dir_path)
        # Erase all files in it.
        erase_files_in_dir(export_dir_path)
        # Save project description file.
        # Save customer file.
        generator.save_customer_data(export_dir_path, 'customers.csv')
        # Zip all the things. Zip file is above the project dir, named
        # projectXXX.zip
        zip_file_path = get_path_to_project_archive(project_id)
        zip_dir(export_dir_path, zip_file_path)
        # Erase the files that were just zipped.
        erase_files_in_dir(export_dir_path)
        # Send the archive's path to the client.
        response = {
            'status': 'ok',
            'archiveurl': '/uploads/project' + str(project_id) + '.zip'
        }
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'status': 'Error: ' + e.__str__()})


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


def get_path_to_project_archive(project_id):
    module_dir = os.path.dirname(__file__)  # get current directory
    path = os.path.realpath(module_dir + '/../uploads/project' + project_id + '.zip')
    return path


def zip_dir(export_dir_path, zip_file_path):
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    zipf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(export_dir_path):
        for file in files:
            zipf.write(os.path.join(root, file), file)
    zipf.close()


def delete_archive(request):
    # Get the project id from the post.
    project_id = request.POST.get('projectid', None)
    if project_id is None:
        return JsonResponse({'status': 'Error: project id missing'})
    # Check that the user has generate access.
    if not user_can_generate(request, project_id):
        return JsonResponse({'status': 'Error: access denied'})
    try:
        zip_file_path = get_path_to_project_archive(project_id)
        os.unlink(zip_file_path)
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'Error: ' + e.__str__()})
