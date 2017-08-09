from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    about = models.TextField(blank=True)
    web_site = models.URLField(blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)
