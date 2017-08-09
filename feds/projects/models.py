from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='projects'
    )
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='E.g., ACC 450 invoicing basic'
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        help_text='URL slug, e.g., acc-450-invoicing-basic. Auto-generated if blank.',
    )
    description = models.TextField(
        blank=True,
        help_text='Remind your future self what this project is about.'
    )
    created = models.DateField(
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if needed.
        # TODO: check for uniqueness within user?
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
