from django.shortcuts import render, get_object_or_404, redirect, \
    HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import SuspiciousOperation, ValidationError, \
    ImproperlyConfigured
from helpers.form_helpers import extract_model_field_meta_data
from businessareas.models import BusinessAreaDb, NotionalTableDb, \
    AvailableNotionalTableSettingDb
from projects.read_write_project import read_project
from .models import ProjectDb, UserSettingDb
from .forms import ProjectForm, ConfirmDeleteForm
from .internal_representation_classes import FedsDateSetting, FedsSetting

FORBIDDEN_MESSAGE = 'Forbidden'


@login_required
def list_projects(request):
    try:
        projects = ProjectDb.objects.filter(user=request.user)
    except ProjectDb.DoesNotExist:
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
    # Get project's basic deets.
    project_db = get_object_or_404(ProjectDb, pk=project_id)
    project = read_project(project_db.pk)
    setting_values = FedsSetting.generate_js_settings_values_object()
    visibility_testers = FedsSetting.generate_js_visibility_testers_object()
    return render(request, 'projects/show_project.html',
                  {
                      'project': project,
                      'settings_values': setting_values,
                      'visibility_testers': visibility_testers,
                  })


def user_can_view_project(request, project_id):
    # Check whether the user has access to the project.
    # TODO: replace with permission check?
    # Is the owner of the project, or is staff.
    current_user = request.user
    project = get_object_or_404(ProjectDb, pk=project_id)
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
        return HttpResponseForbidden(FORBIDDEN_MESSAGE)
    return create_edit_project(request, 'new')


@login_required
def edit_project(request, project_id):
    """ Edit a project. Send 'edit' operation and the project's id to
    create_edit view. """
    if not user_can_edit_project(request, project_id):
        return HttpResponseForbidden(FORBIDDEN_MESSAGE)
    return create_edit_project(request, 'edit', project_id)


@login_required
def create_edit_project(request, operation, project_id=0):
    """ Create or edit a project, depending on the operation. """
    if request.method == 'GET':
        # A GET is either for a new project, or to edit one.
        if operation == 'edit':
            # Edit, so load current data.
            project = get_object_or_404(ProjectDb, pk=project_id)
            form = ProjectForm(initial=project)
        else:
            # Create MT project form.
            # Get the first business area.
            business_area = BusinessAreaDb.objects.all().order_by('title')[0]
            # Set initial, otherwise form fields have 'None' in them. Strange.
            form = ProjectForm(
                initial={'title': '', 'slug': '', 'description': '',
                         'business_area': business_area}
            )
            # form.business_area.choices \
            #     = BusinessArea.objects.all().order_by('title')
        return render(
            request,
            'projects/create_edit_project.html',
            {'operation': operation,
             'project_id': project_id,  # id is passed for Cancel link.
             'form': form,
             'model_field_meta_data':
                 extract_model_field_meta_data(form,
                                               ['help_text', 'max_length']),
             }
        )
    if request.method != 'POST':
        raise SuspiciousOperation(
            'Bad HTTP op in create_edit_project: {op}'.format(
                op=request.method))
    # It's a POST.
    form = ProjectForm(request.POST)
    # Apply form validation. This does not apply model validation.
    if form.is_valid():
        if operation == 'edit':
            # Edit, so load current data.
            project = get_object_or_404(ProjectDb, pk=project_id)
        else:
            # New project, create MT object.
            project = ProjectDb()
        # Copy data from form fields into model instance.
        cleaned_data = form.cleaned_data
        project.user = request.user
        project.title = cleaned_data['title']
        project.description = cleaned_data['description']
        project.slug = cleaned_data['slug']
        project.business_area = cleaned_data['business_area']
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
        return HttpResponseForbidden(FORBIDDEN_MESSAGE)
    if request.method == 'GET':
        # User is asking to delete. Show the confirmation form.
        form = ConfirmDeleteForm()
        return render(
            request,
            'projects/delete_project.html',
            {
                'form': form,
                'project_id': project_id,  # id is passed for Cancel link.
                'model_field_meta_data':
                    extract_model_field_meta_data(form, ['help_text']),
            }
        )
    if request.method != 'POST':
        raise SuspiciousOperation(
            'Bad HTTP op in delete_project: {op}'.format(op=request.method))
    # It's a POST.
    form = ConfirmDeleteForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        confirm_is_checked = cleaned_data['confirm']
        if confirm_is_checked:
            # TODO: delete linked records.
            project = get_object_or_404(ProjectDb, pk=project_id)
            project.delete()
            messages.success(request, 'Project deleted.')
            # TODO: replace explicit link.
            return redirect('home')
        # Not confirmed.
        messages.info(request, 'Deletion not confirmed.')
        return redirect('projects:show_project', project_id=project_id)
    # Form was not valid. This should not happen.
    raise ValidationError('Huh? Delete form not is_valid().')


@login_required
def clone_project(request):
    return HttpResponse('Heretical!')


@login_required
def request_setting_widget(request):
    """ Get a widget for a setting to show in a form. """
    # Identify the project and setting.
    project_id, setting_machine_name, project = get_setting_info(request)
    # Get the widget code.
    widget_html, validators = FedsSetting.setting_machine_names[
        setting_machine_name].display_widget()
    result = {
        'status': 'ok',
        'widgethtml': widget_html,
        'validators': validators,
    }
    return JsonResponse(result)


def get_setting_info(request):
    """
    Get info identifying the setting from the request.
    :param request:
    :return:
    """
    # Is the project id given?
    project_id = request.POST.get('projectid', None)
    if project_id is None:
        return HttpResponse(status=404, reason='Projectid missing')
    # Can use user edit the project?
    if not user_can_edit_project(request, project_id):
        return HttpResponse(
            status=403,
            reason='You do not have permission to change this project.'
        )
    # Is the settings's machine name given?
    setting_machine_name = request.POST.get('machinename', None)
    if setting_machine_name is None:
        return HttpResponse(status=404, reason='Machinename missing')
    # Load the FedsXXXSettings for the project.
    project = read_project(project_id)
    # Is the machine name defined?
    if setting_machine_name not in FedsSetting.setting_machine_names:
        return HttpResponse(status=404, reason='Machinename unknown')
    return project_id, setting_machine_name, project


@login_required
def save_setting(request):
    """ Get a widget for a setting to show in a form. """
    try:
        # Identify the project and setting.
        project_id, setting_machine_name, project = get_setting_info(request)
        # Get the new value
        new_value = request.POST.get('newValue', None)
        if new_value is None:
            msg = 'New value missing. Proj: {proj_id}, machine name: {mn}.'
            raise ValueError(msg.format(proj_id=project_id,
                                         mn=setting_machine_name))
        # Get project DB record.
        project_db = ProjectDb.objects.get(pk=project_id)
        # Lookup existing records with given project and machine name.
        user_setting_db_recs = UserSettingDb.objects.filter(
            project=project_db,
            machine_name=setting_machine_name
        )
        # There should only be one.
        if user_setting_db_recs.count() > 1:
            msg = 'Too many user settings. Proj: {proj_id}, machine name: {mn}.'
            raise LookupError(msg.format(proj_id=project_id,
                                         mn=setting_machine_name))
        if user_setting_db_recs.count() == 0:
            # Make a new record.
            user_setting_db = UserSettingDb(
                project=project_db,
                machine_name=setting_machine_name,
                value=new_value
            )
        else:
            # Update
            user_setting_db = user_setting_db_recs[0]
            user_setting_db.value = new_value
        user_setting_db.save()
        # Done.
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponse(status=500, reason='Error: ' + e.__str__())


@login_required
def load_setting_deets(request):
    """
    Load the deets for a single setting.
    :param request:
    :return: HTML to show the deets.
    """
    # Identify the project and setting.
    project_id, setting_machine_name, project = get_setting_info(request)
    # Is it in the machine names list?
    if setting_machine_name not in FedsSetting.setting_machine_names:
        raise ReferenceError('load_setting_deets: cannot find "{mn}"'
                             .format(mn=setting_machine_name))
    # Get the deets.
    html = FedsSetting.setting_machine_names[
        setting_machine_name].display_deets()
    return JsonResponse({'deets': html})