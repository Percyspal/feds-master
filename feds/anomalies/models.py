from django.db import models


class Anomaly(models.Model):
    """ Base class for all anomaly specifications. """
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this anomaly.'
    )
    description = models.TextField(
        blank=True,
        help_text=' of this anomaly.'
    )

    def __str__(self):
        return self.title

    def anomalize_data(self, data_set):
        pass

    class Meta:
        abstract = True


class PrimaryKeyAnomaly(Anomaly):
    """ A primary key anomaly. """
    # The key can be zero.
    pk_can_be_zero = models.BooleanField(
        default=False,
        help_text="The primary key can be zero for some records."
    )
