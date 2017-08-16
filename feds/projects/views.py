from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import SuspiciousOperation, ValidationError, \
    ImproperlyConfigured
from helpers.form_helpers import extract_model_field_meta_data
from businessareas.models import BusinessArea, NotionalTable
from fieldspecs.models import FieldSpec, AvailableFieldSetting
from feds.settings import FEDS_DATE_RANGE_SETTING, FEDS_BOOLEAN_SETTING
from .models import Project
from .forms import ProjectForm, ConfirmDeleteForm
from .settings_classes import FedsDateRangeSetting, FedsBooleanSetting

FORBIDDEN_MESSAGE = 'Forbidden'


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
    # Get project's basic deets.
    project = get_object_or_404(Project, pk=project_id)
    # Dict for the notional tables in the business area.
    tables = dict()
    # Dict for data extracted from fieldspecs for the business area.
    field_specs = dict()
    if project.business_area.title.lower() == 'revenue':
        revenue_tables = NotionalTable.objects.filter(
            business_area__title__iexact='revenue'
        )
        tables['customer'] = revenue_tables.get(title__iexact='customer')
        tables['invoice'] = revenue_tables.get(title__iexact='invoice')
        tables['invoice_detail'] = revenue_tables.get(
            title__iexact='invoicedetail'
        )
        tables['product'] = revenue_tables.get(title__iexact='product')
        field_specs['customer'] = get_available_field_specs(tables['customer'])
        field_specs['invoice'] = get_available_field_specs(tables['invoice'])
        field_specs['invoice_detail'] = get_available_field_specs(
            tables['invoice_detail']
        )
        field_specs['product'] = get_available_field_specs(tables['product'])
    return render(request, 'projects/show_project.html',
                  {
                      'project': project,
                      'tables': tables,
                      'field_specs': field_specs
                  })


def get_available_field_specs(table_model):
    """ Get available field specs for table_model. """
    # Get the field specs referenced in the table.
    field_specs = FieldSpec.objects.filter(notional_tables=table_model)
    # Create a list of them
    field_specs_extracts = list()
    for field_spec in field_specs:
        # Process a field spec
        field_specs_extract = dict()
        # Copy basic field spec properties.
        field_specs_extract['field_spec_id'] = field_spec.pk
        field_specs_extract['title'] = field_spec.title
        field_specs_extract['description'] = field_spec.description
        # Make a list of available settings
        field_specs_extract['available_settings'] = list()
        for field_setting in field_spec.available_field_settings.all():
            # Process one setting.
            setting_extract = dict()
            # Copy its basic properties.
            setting_extract['title'] = field_setting.title
            setting_extract['description'] = field_setting.description
            setting_extract['setting_group'] = field_setting.setting_group
            setting_extract['setting_type'] = field_setting.setting_type
            # Params from the field setting table.
            setting_base_params = field_setting.setting_params
            # Params from the relationship table
            relation_record = AvailableFieldSetting.objects.get(
                field_spec=field_spec, field_setting=field_setting
            )
            setting_relation_params = relation_record.field_setting_params
            # Create merged params.
            if not isinstance(setting_base_params, dict):
                setting_base_params = dict()
            if not isinstance(setting_relation_params, dict):
                setting_relation_params = dict()
            merged_params = {}
            merged_params.update(setting_base_params)
            merged_params.update(setting_relation_params)
            setting_extract['params'] = merged_params
            # Setting title might be overridden by params.
            if 'title' in setting_extract['params']:
                # Copy title from params to setting property.
                setting_extract['title'] = setting_extract['params']['title']
            # Setting description might be overridden.
            if 'description' in setting_extract['params']:
                setting_extract['description'] \
                    = setting_extract['params']['description']
            # Instantiate Python class used to represent this type of setting.
            setting_extract['class'] = create_setting_class(
                setting_extract['title'],
                setting_extract['description'],
                setting_extract['setting_group'],
                setting_extract['setting_type'],
                setting_extract['params']
            )
            setting_extract['display_deets'] = setting_extract['class']\
                .display_deets()
            # Append settings to field spec's settings list.
            field_specs_extract['available_settings'].append(setting_extract)
        # Append field spec to field specs list.
        field_specs_extracts.append(field_specs_extract)
    return field_specs_extracts


def create_setting_class(title, description, group, class_name, params):
    if class_name == FEDS_DATE_RANGE_SETTING:
        result = FedsDateRangeSetting(title, description, group, params)
    elif class_name == FEDS_BOOLEAN_SETTING:
        result = FedsBooleanSetting(title, description, group, params)
    else:
        raise ImproperlyConfigured('Unknown setting class: {class_name}'
                                   .format(class_name=class_name))
    return result


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
            project = get_object_or_404(Project, pk=project_id)
            form = ProjectForm(initial=project)
        else:
            # Create MT project form.
            # Get the first business area.
            business_area = BusinessArea.objects.all().order_by('title')[0]
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
            project = get_object_or_404(Project, pk=project_id)
        else:
            # New project, create MT object.
            project = Project()
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
            project = get_object_or_404(Project, pk=project_id)
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
