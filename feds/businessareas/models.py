from django.db import models
from jsonfield import JSONField
from django.core.exceptions import ValidationError
from fieldsettings.models import FieldSetting


class BusinessArea(models.Model):
    """ Accounting problem domain. """
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='E.g., Invoicing.'
    )
    description = models.TextField(
        blank=True,
    )
    # default_params = JSONField(
    #     blank=True,
    #     default={},
    #     help_text='Default parameters for this business area. JSON.'
    # )

    def save(self, *args, **kwargs):
        """ Validate and trimming. """
        # Trim title whitespace.
        self.title = self.title.strip()
        if not self.title:
            raise ValidationError('Business area title cannot be empty.')
        # Trim description whitespace.
        self.description = self.description.strip()
        # TODO: does description trimming harm ReST?
        super().save(*args, **kwargs)

    def __str__(self):
        """ Stringified business area is its title. """
        return self.title


class NotionalTable(models.Model):
    """ Table in a business area, e.g., customer. """
    business_area = models.ForeignKey(
        BusinessArea,
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
    description = models.TextField(
        blank=True,
    )
    available_table_settings = models.ManyToManyField(
        FieldSetting,
        through='AvailableNotionalTableSetting',
        related_name='available_table_settings',
        help_text='Settings that this table can have.',
    )

    def save(self, *args, **kwargs):
        """ Validate and trimming. """
        # Trim title whitespace.
        self.title = self.title.strip()
        if not self.title:
            raise ValidationError('Notional table title cannot be empty.')
        # Trim description whitespace.
        self.description = self.description.strip()
        # TODO: does description trimming harm ReST?
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AvailableNotionalTableSetting(models.Model):
    """ A setting that a notional table can have. """
    table = models.ForeignKey(
        NotionalTable,
        null=False,
        blank=False,
        help_text='Notional table can have the setting.'
    )
    table_setting = models.ForeignKey(
        FieldSetting,
        null=False,
        blank=False,
        help_text='A setting the notional table can have.'
    )
    table_setting_order = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        help_text='Order of the setting in the settings list for the field.'
    )
    table_setting_params = JSONField(
        blank=True,
        default={},
        help_text='JSON parameters to initialize the table setting.'
    )

    def __str__(self):
        return '{setting} for table {table}'.format(
            setting=self.table_setting.title,
            table=self.table_setting.title
        )
