from django.db import models
from anomalies.models import Anomaly
from businessareas.models import NotionalTable


class FieldSpec(models.Model):
    """ Base class for all field specifications. """
    notional_tables = models.ManyToManyField(
        NotionalTable,
        through='NotionalTableMembership',
    )
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this field spec'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of this field spec.'
    )
    possible_anomalies = models.ManyToManyField(
        Anomaly,
        through='PossibleFieldAnomaly',
        related_name='possible_anomalies',
        help_text='Anomalies that this field can have.',
    )

    class Meta:
        abstract = True

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


class PrimaryKeyFieldSpec(FieldSpec):
    """ A primary key field specification. """
    pass
