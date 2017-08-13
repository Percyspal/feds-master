from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from feds.settings import FEDS_REST_HELP_URL


# TODO: Add project-level anomalies?
class Project(models.Model):
    """
        Data model for a project.

        See self.make_slug_unique_for_user() for an attribute self.slug_changed, set to True if
        make_slug_unique_for_user() automatically changed the slug.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        blank=False,
    )
    # TODO: check that Django trims the field before the blank check.
    title = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        help_text='E.g., ACC 450 invoicing basic'
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        help_text='URL slug, e.g., acc-450-invoicing-basic. Auto-generated if blank.',
    )
    description = models.TextField(
        blank=True,
        help_text='What this project is about. <a href="{0}" target="_new">ReStructuredText</a>'
            .format(FEDS_REST_HELP_URL)
    )
    when_created = models.DateField(
        auto_now=True,
        db_index=True
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Trim title whitespace.
        self.title = self.title.strip()
        if not self.title:
            raise ValidationError('Project title cannot be empty.')
        # Trim description whitespace.
        self.description = self.description.strip()
        # TODO: does description trimming harm ReST?
        # Trim slug whitespace.
        self.slug = self.slug.strip()
        # Generate slug if needed.
        if not self.slug:
            self.slug = slugify(self.title)
        # Adjust slug if another project for this user is already using that slug.
        self.make_slug_unique_for_user()
        super().save(*args, **kwargs)

    def make_slug_unique_for_user(self):
        """ Make sure that the slug is unique for the projects owned by this user.

        Adds attribute self.slug_changed to record whether the slug was changed to make
        it unique within user.

        """
        slug_ok = False
        self.slug_changed = False  # Show whether the code changed the slug.
        while not slug_ok:
            # Find project with the current slug for the project's user.
            projects_with_slug = Project.objects.filter(user=self.user, slug=self.slug)
            # If there is more than one, there's a problem.
            if projects_with_slug.count() > 1:
                raise ValidationError(
                    'Danger, Will Robinson! Too many slugs for user {user_id} with value {slug}!'
                        .format(user_id=self.user.pk, slug=self.slug)
                )
            # Found any?
            if projects_with_slug.count() == 0:
                # No, so slug is OK.
                slug_ok = True
                # Exit slug checking loop
                break
            if projects_with_slug.count() == 1:
                # Found one project with the slug.
                if self.pk is None:
                    # Saving a new record, so slug is already being used.
                    # Append stuff, to try to make the slug unique.
                    self.add_slug_extra_piece()
                    slug_ok = False
                    # Flag that the slug was changed.
                    self.slug_changed = True
                    # Try the check again.
                    continue
                # Slug already exists, and this is not a new project.
                # Is the project with the slug the same as self?
                project_with_slug = projects_with_slug[0]
                if project_with_slug.pk == self.pk:
                    # Same thing. No problem.
                    slug_ok = True
                    # Exit slug checking loop.
                    break
                # The project with the slug is not self.
                # Append stuff, to try to make the slug unique.
                self.add_slug_extra_piece()
                # Flag that the slug was changed.
                self.slug_changed = True

    def add_slug_extra_piece(self):
        """ Add an extra piece to a slug to try to make it unique. """
        self.slug += '-another'
