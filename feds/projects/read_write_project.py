from django.shortcuts import get_object_or_404

from projects.internal_representation_classes import FedsProject, \
    FedsNotionalTable
from projects.models import Project, AvailableBusinessAreaProjectSetting
from fieldsettings.models import FieldSetting
from businessareas.models import NotionalTable, BusinessArea


def read_project(project_id):
    """
    Return a representation of a project, using the internal representation
    classes.
    """
    project_default = load_project_defaults(project_id)


def load_project_defaults(project_id):
    """
    Load the default rep of a project.
    :param project_id: Id of the project.
    :return: FedsProject
    """
    # Get project's basic deets from the DB.
    project_db = get_object_or_404(Project, pk=project_id)
    business_area = get_object_or_404(BusinessArea, pk=project_db.business_area)
    project = FedsProject(
        project_db.pk,
        project_db.title,
        project_db.description,
        project_db.slug,
        business_area.title
    )
    add_default_project_settings(project)
    # Get the tables from the DB.
    tables_db = NotionalTable.objects.filter(
        business_area=project_db.business_area
    )
    for table_db in tables_db:
        # Create the
        table = FedsNotionalTable(
            table_db.pk,
            table_db.title,
            table_db.description
        )

    return project


def add_default_project_settings(project):
    """
    Add default settings for a project.
    :param project: The project.
    """
    settings = FieldSetting.objects.filter(
        availablebusinessareaprojectsetting__project__pk=project.db_id
    )
    f=5

def merge_user_choices(project_default):
    """
    Merge user's choices for a project into the default for the project.
    :param project_default: The default representation of the project.
    """
    pass
