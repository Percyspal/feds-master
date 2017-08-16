from django.db import models
from fieldsettings.models import FieldSetting
from businessareas.models import NotionalTable
from projects.models import Project
from jsonfield import JSONField


class FieldSpec(models.Model):
    """ A specification of a field in a notional table. """
    FIELD_TYPES = (
        ('pk', 'Primary key'),
        ('fk', 'Foreign key'),
        ('text', 'Text'),
        ('zip', "Zip code"),
        ('phone', "Phone"),
        ('email', "Email address"),
        ('date', 'Date'),
        ('choice', 'Choice from a list'),
        ('currency', 'Currency'),
        ('int', 'Integer'),
    )
    notional_tables = models.ManyToManyField(
        NotionalTable,
        through='NotionalTableMembership',
        # related_name='%(app_label)s_%(class)s_related_notional_tables',
    )
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this field specification.'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of this field specification.'
    )
    available_field_settings = models.ManyToManyField(
        FieldSetting,
        through='AvailableFieldSetting',
        related_name='available_settings',
        help_text='Settings that this field specification can have.',
    )
    field_type = models.CharField(
        max_length=10,
        choices=FIELD_TYPES,
        help_text='Field type',
        blank=False,
        null=False,
    )
    # field_spec_params = JSONField(
    #     blank=True,
    #     default={},
    #     help_text='Parameters for this field specification. JSON.'
    # )

    def __str__(self):
        return self.title


class NotionalTableMembership(models.Model):
    """
        Middle table in M (notional table):N (field spec).

        See https://docs.djangoproject.com/en/1.11/topics/db/models/
            #many-to-many-relationships.
     """
    # TODO: on_delete=models.CASCADE?
    field_spec = models.ForeignKey(
        FieldSpec,
        null=False,
        blank=False,
        help_text='Field in notional table.'
    )
    notional_table = models.ForeignKey(
        NotionalTable,
        null=False,
        blank=False,
        help_text='Notional table the field is in.'
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


class AvailableFieldSetting(models.Model):
    """ A setting that a field can have. """
    field_spec = models.ForeignKey(
        FieldSpec,
        null=False,
        blank=False,
        help_text='Field that can have the setting.'
    )
    field_setting = models.ForeignKey(
        FieldSetting,
        null=False,
        blank=False,
        help_text='A setting the field can have.'
    )
    field_setting_order = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        help_text='Order of the setting in the settings list for the field.'
    )
    field_setting_params = JSONField(
        blank=True,
        default={},
        help_text='JSON parameters to initialize the field setting.'
    )

    def __str__(self):
        return '{setting} for field {field_spec}'.format(
            setting=self.field_setting.title,
            field_spec=self.field_spec.title
        )


class ProjectFieldSetting(models.Model):
    """ A field spec setting for a particular project. """
    project = models.ForeignKey(
        Project,
        null=False,
        blank=False,
        help_text='Project the setting data is for.'
    )
    available_field_setting = models.ForeignKey(
        AvailableFieldSetting,
        null=False,
        blank=False,
        help_text='Available field setting the data is for.'
    )
    setting_params = JSONField(
        blank=True,
        default={},
        help_text='JSON parameters for this field setting, for this project.'
    )
