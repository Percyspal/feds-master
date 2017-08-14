from django.db import models
from jsonfield import JSONField
from django.core.exceptions import ValidationError


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
