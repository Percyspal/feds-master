from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from feds.settings import FEDS_NOTIONAL_FIELD_TYPES
from businessareas.models import NotionalTableDb
from fieldsettings.models import FieldSettingDb
from helpers.model_helpers import stringify_json, is_legal_json, \
    check_field_type_known

"""
These classes are representations of objects as they are stored in the DB.
They need to be flattened and have their JSON params merged before they are
ready for display.
"""


class FieldSpecDb(models.Model):
    """ A specification of a field in a notional table. """
    notional_tables = models.ManyToManyField(
        NotionalTableDb,
        through='NotionalTableMembershipDb',
        related_name='notional_tables',
    )
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this field specification.'
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this field_spec, e.g., fld_spec_quantity.'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of this field specification.'
    )
    available_field_settings = models.ManyToManyField(
        FieldSettingDb,
        through='AvailableFieldSpecSettingDb',
        related_name='available_field_settings',
        help_text='Settings that this field specification can have.',
    )
    field_type = models.CharField(
        max_length=10,
        choices=FEDS_NOTIONAL_FIELD_TYPES,
        help_text='Field type',
        blank=False,
        null=False,
    )
    field_params = models.TextField(
        blank=True,
        default='{}',
        help_text='JSON parameters to describe field spec.'
    )

    def save(self, *args, **kwargs):
        """ Validate and trimming. """
        # Trim title whitespace.
        self.title = self.title.strip()
        if not self.title:
            raise ValidationError('Field spec title cannot be empty.')
        # Trim description whitespace.
        self.description = self.description.strip()
        # TODO: does description trimming harm ReST?
        # Check whether type is in valid list.
        if not check_field_type_known(self.field_type):
            raise ValueError('Field spec field type is unknown: {}'
                             .format(self.field_type))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NotionalTableMembershipDb(models.Model):
    """
        Middle table in M (notional table):N (field spec).

        See https://docs.djangoproject.com/en/1.11/topics/db/models/
            #many-to-many-relationships.
     """
    # TODO: on_delete=models.CASCADE?
    field_spec = models.ForeignKey(
        FieldSpecDb,
        null=False,
        blank=False,
        help_text='Field in notional table.'
    )
    notional_table = models.ForeignKey(
        NotionalTableDb,
        null=False,
        blank=False,
        help_text='Notional table the field is in.'
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this table field spec, e.g., cust_cname.'
    )
    field_order = models.IntegerField(
        null=False,
        blank=False,
        help_text='Order of the field in the notional table.'
    )

    def __str__(self):
        return '{field_spec} in table {notional_table}'.format(
            field_spec=self.field_spec.title,
            notional_table=self.notional_table.title
        )

    def save(self, *args, **kwargs):
        """ Validate and trimming. """
        # Check machine name.
        if not self.machine_name:
            message = 'NotionalTableMembershipDb machine name cannot be empty.'
            raise ValidationError(message)
        super().save(*args, **kwargs)


class AvailableFieldSpecSettingDb(models.Model):
    """ A setting that a field can have. """
    field_spec = models.ForeignKey(
        FieldSpecDb,
        null=False,
        blank=False,
        help_text='Field that can have the setting.'
    )
    field_setting = models.ForeignKey(
        FieldSettingDb,
        null=False,
        blank=False,
        help_text='A setting the field can have.'
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this setting, e.g., quantity_min.'
    )
    field_setting_order = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        help_text='Order of the setting in the settings list for the field.'
    )
    field_setting_params = models.TextField(
        blank=True,
        default='{}',
        help_text='JSON parameters to initialize the field setting.'
    )

    def save(self, *args, **kwargs):
        # Check machine name.
        if not self.machine_name:
            message = 'AvailableFieldSpecSettingDb machine name cannot be MT.'
            raise ValidationError(message)
        # Check params format.
        self.field_setting_params = stringify_json(self.field_setting_params)
        if self.field_setting_params:
            if not is_legal_json(self.field_setting_params):
                message = 'AvailableFieldSettingDb: Params not JSON: {params}'
                raise ValidationError(message.format(
                    params=self.field_setting_params
                ))
        super().save(*args, **kwargs)

    def __str__(self):
        return '{setting} for field {field_spec}'.format(
            setting=self.field_setting.title,
            field_spec=self.field_spec.title
        )
