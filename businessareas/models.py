from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from fieldsettings.models import FieldSettingDb
from helpers.model_helpers import is_legal_json, stringify_json


"""
These classes are representations of objects as they are stored in the DB.
They need to be flattened and have their JSON params merged before they are
ready for display.
"""


class BusinessAreaDb(models.Model):
    """ Accounting problem domain. """
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='E.g., Invoicing.'
    )
    description = models.TextField(
        blank=True,
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this business area, e.g., ba_revenue.'
    )
    available_business_area_settings = models.ManyToManyField(
        FieldSettingDb,
        through='AvailableBusinessAreaSettingDb',
        related_name='available_business_area_settings',
        help_text='Settings projects for this business area can have.'
    )

    def save(self, *args, **kwargs):
        """ Validate and trimming. """
        # Trim title whitespace.
        self.title = self.title.strip()
        if not self.title:
            raise ValidationError('Business area title cannot be empty.')
        # Trim description whitespace.
        self.description = self.description.strip()
        if not self.machine_name:
            raise ValidationError(
                'BusinessAreaDb: Machine name empty for title "{title}".'
                .format(title=self.title))
        # TODO: does description trimming harm ReST?
        super().save(*args, **kwargs)

    def __str__(self):
        """ Stringified business area is its title. """
        return self.title


class NotionalTableDb(models.Model):
    """ Table in a business area, e.g., customer. """
    business_area = models.ForeignKey(
        BusinessAreaDb,
        related_name='notional_table_business_area',
        blank=False,
        null=False,
        help_text='What business area is this notional table part of?'
    )
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='E.g., Customers.'
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this table, e.g., tbl_invoices.'
    )
    description = models.TextField(
        blank=True,
    )
    display_order = models.IntegerField(
        blank=False,
        null=False,
        default=1,
        help_text='Order table is displayed, from left to right.'
    )
    available_notional_table_settings = models.ManyToManyField(
        FieldSettingDb,
        through='AvailableNotionalTableSettingDb',
        related_name='available_notional_table_settings',
        help_text='Settings that this table can have.',
    )

    def save(self, *args, **kwargs):
        """ Validate and trimming. """
        # Trim title whitespace.
        self.title = self.title.strip()
        if not self.title:
            raise ValidationError('Notional table title cannot be empty.')
        # Check machine name.
        if not self.machine_name:
            raise ValidationError(
                'NotionalTableDbMachine: Machine name MT for title "{title}".'
                .format(title=self.title))
        # Trim description whitespace.
        self.description = self.description.strip()
        # TODO: does description trimming harm ReST?
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AvailableNotionalTableSettingDb(models.Model):
    """ A setting that a notional table can have. """
    table = models.ForeignKey(
        NotionalTableDb,
        null=False,
        blank=False,
        help_text='Notional table can have the setting.'
    )
    table_setting = models.ForeignKey(
        FieldSettingDb,
        null=False,
        blank=False,
        help_text='A setting the notional table can have.'
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this setting, e.g., tbl_invoices_total_bt.'
    )
    table_setting_order = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        help_text='Order of the setting in the settings list for the field.'
    )
    table_setting_params = models.TextField(
        blank=True,
        default='{}',
        help_text='JSON parameters to initialize the table setting.'
    )

    def save(self, *args, **kwargs):
        if not self.machine_name:
            raise ValidationError(
                'AvailableNotionalTableSettingDb: Machine name MT.'
            )
        # Check params format.
        self.table_setting_params = stringify_json(self.table_setting_params)
        if self.table_setting_params:
            if not is_legal_json(self.table_setting_params):
                message = 'Notional table setting: Params not JSON: {params}'
                raise ValidationError(message.format(
                    params=self.table_setting_params
                ))
        super().save(*args, **kwargs)

    def __str__(self):
        return '{setting} for table {table}'.format(
            setting=self.table_setting.title,
            table=self.table_setting.title
        )


class AvailableBusinessAreaSettingDb(models.Model):
    """ A setting available for projects in a business area. """
    business_area = models.ForeignKey(
        BusinessAreaDb,
        blank=False,
        null=False,
        help_text='What business area is this setting available for?'
    )
    business_area_setting = models.ForeignKey(
        FieldSettingDb,
        null=False,
        blank=False,
        help_text='The setting that is available.'
    )
    machine_name = models.TextField(
        max_length=50,
        blank=False,
        default='',
        help_text='Machine name of this setting, e.g., ba_revenue_sales_tax.'
    )
    business_area_setting_order = models.IntegerField(
        null=False,
        blank=False,
        help_text='Order of the setting in the list for the business area.'
    )
    business_area_setting_params = models.TextField(
        blank=True,
        default='{}',
        help_text='JSON parameters to initialize the setting.'
    )

    def save(self, *args, **kwargs):
        if not self.machine_name:
            raise ValidationError(
                'AvailableBusinessAreaSettingDb: Machine name MT.')
        # Check params format.
        self.business_area_setting_params \
            = stringify_json(self.business_area_setting_params)
        if self.business_area_setting_params:
            if not is_legal_json(self.business_area_setting_params):
                message = 'AvailableBusinessAreaSetting table setting: ' \
                          'Params not JSON: {params}'
                raise ValidationError(message.format(
                    params=self.business_area_setting_params
                ))
        super().save(*args, **kwargs)

    def __str__(self):
        return '{setting} for projects in {business_area}'.format(
            setting=self.business_area_setting.title,
            business_area=self.business_area.title
        )
