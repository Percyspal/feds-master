from django.db import models
from jsonfield import JSONField
from feds.settings import FEDS_SETTING_GROUPS, FEDS_SETTING_TYPES, \
    FEDS_BASIC_SETTING_GROUP
# from fieldspecs.models import FieldSpec
# from projects.models import Project, AvailableProjectSetting
# from businessareas.models import NotionalTable


class FieldSetting(models.Model):
    """ A setting that a field can have. """
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this setting.'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of this setting.'
    )
    setting_group = models.CharField(
        max_length=10,
        blank=False,
        choices=FEDS_SETTING_GROUPS,
        help_text='What setting is this? Basic setting, or anomaly.',
        default=FEDS_BASIC_SETTING_GROUP
    )
    setting_type = models.CharField(
        max_length=20,
        blank=False,
        choices=FEDS_SETTING_TYPES,
        help_text='What type of setting is this?'
    )
    setting_params = JSONField(
        blank=True,
        default={},
        help_text='Parameters for this setting. JSON.'
    )

    def __str__(self):
        return self.title
