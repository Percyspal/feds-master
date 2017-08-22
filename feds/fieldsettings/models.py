from django.db import models
from django.utils.text import slugify

from feds.settings import FEDS_SETTING_GROUPS, FEDS_SETTING_TYPES, \
    FEDS_BASIC_SETTING_GROUP
from django.core.exceptions import ValidationError
from helpers.model_helpers import is_legal_json, stringify_json

"""
These classes are representations of objects as they are stored in the DB.
They need to be flattened and have their JSON params merged before they are
ready for display.
"""


class FieldSettingDb(models.Model):
    """ A setting that a field/table/business area can have. """
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this setting.'
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this setting, e.g., quantity.'
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
    setting_params = models.TextField(
        blank=True,
        default='{}',
        help_text='Parameters for this setting. JSON.'
    )

    def save(self, *args, **kwargs):
        """ Validate. """
        # Check title.
        self.title = self.title.strip()
        if not self.title:
            raise ValidationError('Setting title cannot be empty.')
        # Trim description whitespace.
        self.description = self.description.strip()
        # TODO: does description trimming harm ReST?
        # Check setting_group.
        self.setting_group = self.setting_group.strip()
        if not self.setting_group:
            message = 'Setting "{title}": Setting group cannot be empty.'
            raise ValidationError(message.format(title=self.title))
        group_ok = False
        for group_tuple in FEDS_SETTING_GROUPS:
            if self.setting_group == group_tuple[0]:
                group_ok = True
                break
        if not group_ok:
            message = 'Setting "{title}": Unknown setting group: {group}'
            raise ValidationError(message.format(
                title=self.title,
                group=self.setting_group))
        # Check setting_type.
        self.setting_type = self.setting_type.strip()
        if not self.setting_type:
            message = 'Setting "{title}": Setting type cannot be empty.'
            raise ValidationError(message.format(title=self.title))
        type_ok = False
        for setting_tuple in FEDS_SETTING_TYPES:
            if self.setting_type == setting_tuple[0]:
                type_ok = True
                break
        if not type_ok:
            message = 'Setting "{title}": Unknown setting type: {type}'
            raise ValidationError(message.format(
                title=self.title, type=self.setting_type))
        # Make params into string for storage.
        # Check params format.
        self.setting_params = stringify_json(self.setting_params)
        if self.setting_params:
            if not is_legal_json(self.setting_params):
                message = 'Setting "{title}": Params not valid JSON: {params}'
                raise ValidationError(message.format(
                    title=self.title, params=self.setting_params
                ))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
