from django.db import models
from anomalies.models import Anomaly
from businessareas.models import NotionalTable


class FieldSpec(models.Model):
    """ Base class for all field specifications. """
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
        related_name='%(app_label)s_%(class)s_related_notional_tables',
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
    possible_anomalies = models.ManyToManyField(
        Anomaly,
        through='PossibleFieldAnomaly',
        related_name='possible_anomalies',
        help_text='Anomalies that this field specification can have.',
    )
    field_type = models.CharField(
        max_length=10,
        help_text='Field type',
        blank=False,
        null=False,
    )
    field_spec_params = models.TextField(
        blank=True,
        help_text='Parameters for this field specification. JSON.'
    )

    def __str__(self):
        return self.title


class NotionalTableMembership(models.Model):
    """
        Middle table in M (notional table):N (field spec).

        See https://docs.djangoproject.com/en/1.11/topics/db/models/#many-to-many-relationships.
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


class PossibleFieldAnomaly(models.Model):
    """ An anomaly that a field can have. """
    field_spec = models.ForeignKey(
        FieldSpec,
        null=False,
        blank=False,
        help_text='Field that can have an anomaly.'
    )
    anomaly = models.ForeignKey(
        Anomaly,
        null=False,
        blank=False,
        help_text='An anomaly the field can have .'
    )
    field_order = models.IntegerField(
        null=False,
        blank=False,
        help_text='Order of the anomaly in the anomaly list for the field.'
    ),
    anomaly_params = models.TextField(
        blank=True,
        help_text='JSON parameters to initialize the anomaly.'
    )

    def __str__(self):
        return '{anomaly} for field {field_spec}'.format(
            anomaly=self.anomaly.title,
            field_spec=self.field_spec.title
        )
