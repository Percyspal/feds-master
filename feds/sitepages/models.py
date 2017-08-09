from django.db import models
from datetime import datetime

# Statuses the page can have.
status_choices = [
    ('published', 'Published'),
    ('blocked', 'Blocked'),
]
markdown_syntax_url = 'https://daringfireball.net/projects/markdown/syntax'


class SitePage(models.Model):
    """
        A static page on the site.
    """
    title = models.CharField(
        max_length=50,
        blank=False,
        help_text='Page title, e.g., "Owls like vegemite". Plain text.',
    )
    slug = models.SlugField(
        unique=True,
        blank=False,
        help_text='Friendly URL of the page, e.g., "owls-like-vegemite". Lowercase, digits, and -.',
    )
    # Content to show. ReST.
    content = models.TextField(
        blank=True,
        help_text='Page content. <a href="{0}" target="_blank">Markdown</a>.'.format(markdown_syntax_url),
    )
    # Status of the page.
    status = models.CharField(
        max_length=12,
        choices=status_choices,
        default='published',
    )
    # Does this page need work?
    needs_work = models.BooleanField(default=False)
    # Notes about the page for staff, e.g., changes that are needed. ReST.
    notes = models.TextField(
        blank=True,
        help_text='Notes for editors. <a href="{0}" target="_blank">Markdown</a>.'.format(markdown_syntax_url),
    )

    def __str__(self):
        return self.title

    def content_trimmed(self, num_chars=100):
        return self.content[:num_chars]
