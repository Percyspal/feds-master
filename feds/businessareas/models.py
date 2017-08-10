from django.db import models


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

    def __str__(self):
        return self.title


class NotionalTable(models.Model):
    """ Table in a business area, e.g., customer. """
    business_area = models.ForeignKey(
        BusinessArea,
        related_name='business_areas',
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

    def __str__(self):
        return self.title
