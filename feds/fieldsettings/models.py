from django.db import models
from jsonfield import JSONField


class FieldSetting(models.Model):
    """ A setting that a field can have. """

    SETTING_TYPES = (
        ('setting', 'Normal setting'),
        ('anomaly', 'Anomaly'),
    )
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Title of this setting.'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of this setting.'
    )
    setting_type = models.CharField(
        max_length=10,
        blank=False,
        choices=SETTING_TYPES,
        help_text='What type of setting is this?'
    )
    setting_params = JSONField(
        blank=True,
        default={},
        help_text='Parameters for this setting. JSON.'
    )

    def __str__(self):
        return self.title

    # def anomalize_data(self, data_set):
    #     pass


