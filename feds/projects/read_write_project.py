from django.shortcuts import get_object_or_404
from projects.internal_representation_classes import FedsProject, \
    FedsNotionalTable, FedsBusinessArea, FedsFieldSpec, FedsBase
from projects.models import ProjectDb, AvailableBusinessAreaSettingDb, \
    UserSettingDb
from fieldsettings.models import FieldSettingDb
from businessareas.models import NotionalTableDb, BusinessAreaDb, \
    AvailableNotionalTableSettingDb
from fieldspecs.models import FieldSpecDb, AvailableFieldSpecSettingDb
from projects.settings_gatherer import SettingsGatherer


def read_project(project_id):
    """
    Return a representation of a project, using the internal representation
    classes.
    """
    # Erase existing machines names.
    FedsBase.machine_name_list = list()
    # Load the project's default settings.
    project = load_project_defaults(project_id)
    # Merge the user's settings
    merge_user_settings(project)
    return project


def load_project_defaults(project_id):
    """
    Load the default rep of a project.
    :param project_id: Id of the project.
    :return: FedsProject
    """
    # Get project's basic deets from the DB.
    project_db = get_object_or_404(ProjectDb, pk=project_id)
    business_area_db = get_object_or_404(
        BusinessAreaDb, pk=project_db.business_area.pk)
    business_area = FedsBusinessArea(
        db_id=business_area_db.pk,
        title=business_area_db.title,
        machine_name=business_area_db.machine_name,
        description=business_area_db.description
    )
    project = FedsProject(
        db_id=project_db.pk,
        title=project_db.title,
        machine_name='spiders!', # Not needed.
        description=project_db.description,
        slug=project_db.slug,
        business_area=business_area
    )
    # Add settings to the project, merging setting and relationship params.
    add_default_project_settings(project, business_area_db)

    # Get the tables from the DB.
    tables_db_records = NotionalTableDb.objects.filter(
        business_area=project_db.business_area
    ).order_by('display_order')
    for table_db_record in tables_db_records:
        # Create the internal rep of the table
        table = FedsNotionalTable(
            db_id=table_db_record.pk,
            title=table_db_record.title,
            machine_name=table_db_record.machine_name,
            description=table_db_record.description
        )
        # Add settings to the table, merging setting and relationship params.
        add_default_table_settings(table, table_db_record)
        # Get the field specs referenced in the table.
        field_specs_db_records = FieldSpecDb.objects.filter(
            notional_tables=table_db_record
        )
        for field_spec_db_record in field_specs_db_records:
            field_spec = FedsFieldSpec(
                db_id=field_spec_db_record.pk,
                title=field_spec_db_record.title,
                machine_name=field_spec_db_record.machine_name,
                description=field_spec_db_record.description,
                field_type=field_spec_db_record.field_type
            )
            # Add settings to the field spec, merging setting
            # and relationship params.
            add_default_field_spec_settings(field_spec, field_spec_db_record)
            table.add_field_spec(field_spec)
        project.add_notional_table(table)
    return project


def add_default_project_settings(project, business_area_db):
    """
    Add default settings for a project.
    :param project: The project's internal rep.
    :param business_area_db: The DB record for the business area.
    """
    base_settings_db = FieldSettingDb.objects.filter(
        availablebusinessareasettingdb__business_area=business_area_db).values()
    relationship_settings = AvailableBusinessAreaSettingDb.objects.filter(
        business_area=business_area_db).order_by('business_area_setting_order').values()
    settings_gatherer = SettingsGatherer(
        base_settings=base_settings_db,
        relationship_settings=relationship_settings,
        relationship_setting_id_field='business_area_setting_id',
        relationship_setting_order_field='business_area_setting_order',
        relationship_setting_params_field='business_area_setting_params',
    )
    project.settings = settings_gatherer.gather_settings()


def add_default_table_settings(table, table_db_rec):
    """
    Add default settings for a table.
    :param table: The table's internal rep.
    :param table_db_rec: The DB record for the table.
    """
    base_settings_db = FieldSettingDb.objects.filter(
        availablenotionaltablesettingdb__table=table_db_rec
    ).values()
    relationship_settings = AvailableNotionalTableSettingDb.objects.filter(
        table=table_db_rec).order_by('table_setting_order').values()
    settings_gatherer = SettingsGatherer(
        base_settings=base_settings_db,
        relationship_settings=relationship_settings,
        relationship_setting_id_field='table_setting_id',
        relationship_setting_order_field='table_setting_order',
        relationship_setting_params_field='table_setting_params',
    )
    table.settings = settings_gatherer.gather_settings()


def add_default_field_spec_settings(field_spec_model, field_spec_db_rec):
    """
    Add default settings for field spec.
    :param field_spec_model: Internal rep of the field spec.
    :param field_spec_db_rec: The DB record for the field spec.
    """
    base_settings_db = FieldSettingDb.objects.filter(
        availablefieldspecsettingdb__field_spec=field_spec_db_rec
    ).values()
    relationship_settings = AvailableFieldSpecSettingDb.objects.filter(
        field_spec=field_spec_db_rec).order_by('field_setting_order').values()
    settings_gatherer = SettingsGatherer(
        base_settings=base_settings_db,
        relationship_settings=relationship_settings,
        relationship_setting_id_field='field_setting_id',
        relationship_setting_order_field='field_setting_order',
        relationship_setting_params_field='field_setting_params',
    )
    field_spec_model.settings = settings_gatherer.gather_settings()


def merge_user_settings(project):
    """
    Merge the user's settings into the project.
    :param project: The project, default settings.
    """
    # Load user's settings
    user_settings_db = UserSettingDb.objects.filter(project=project.db_id)
    # Make a dict for fast reference.
    user_settings = dict()
    for user_setting_db in user_settings_db:
        user_settings[user_setting_db.pk] = {
            'params': user_setting_db.setting_params
        }
    # Merge the project settings.
    for setting in project.settings:
        # Get a setting id.
        setting_id = setting.db_id
        # Is there user data for it?
        if setting_id in user_settings:
            # Merge them.
            pass
