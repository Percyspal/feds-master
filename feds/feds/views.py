from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.management import execute_from_command_line
from django.contrib import messages
from .secrets import secret_superuser_deets, secret_users, secret_pages
from accounts.models import Profile
from sitepages.models import SitePage


def init_database(request):
    """ Initialize database """
    # If users can be fetched, and there are some, then abort with 404.
    try:
        users = User.objects.all()
        if users.count() == 0:
            raise SystemError
        return HttpResponseNotFound('Page not found.')
    except:
        # TODO: find what the exception is for undefined tables.
        pass
    # Create and run migrations.
    execute_from_command_line(['makemigrations'])
    execute_from_command_line(['migrate'])
    # Make the superuser.
    make_superuser()
    # Make other users.
    make_regular_users()
    # Make some pages.
    make_pages()
    messages.success(request, 'Database initialized. Hopefully.')
    # Back to home page.
    return redirect('/')


def make_superuser():
    """ Make the superuser. """
    # TODO: set other user fields.
    superuser_deets = secret_superuser_deets()
    superuser = User.objects.create_superuser(
        superuser_deets['username'],
        superuser_deets['email'],
        superuser_deets['password']
    )
    profile = Profile()
    profile.user = superuser
    profile.save()


def make_regular_users():
    """ Make other users. """
    # TODO: set other user fields.
    users = secret_users()
    for username, user_deets in users.items():
        user = User.objects.create_user(
            username,
            email=user_deets['email'],
            password=user_deets['password'],
        )
        profile = Profile()
        profile.user = user
        profile.save()


def make_pages():
    """ Make some pages. """
    # Erase existing pages first.
    SitePage.objects.all().delete()
    # Get specs for pages.
    page_specs = secret_pages()
    # Make them.
    for page_spec in page_specs:
        site_page = SitePage()
        site_page.title = page_spec['title']
        site_page.slug = page_spec['slug']
        site_page.content = page_spec['content']
        site_page.save()
