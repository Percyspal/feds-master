from django.db import models


class Anomaly(models.Model):
    """ An anomaly that a field or project can have. """
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this anomaly.'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of this anomaly.'
    )
    anomaly_params = models.TextField(
        blank=True,
        help_text='Parameters for this anomaly. JSON.'
    )

    def __str__(self):
        return self.title

    # def anomalize_data(self, data_set):
    #     pass


