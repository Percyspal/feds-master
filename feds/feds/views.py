from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .db_initializer import DbInitializer


def init_database(request):
    """ Initialize database. Migrations have to be run first. """
    users = User.objects.all()
    if users.count() > 0:
        return HttpResponseNotFound('Page not found.')
    db_initializer = DbInitializer()
    db_initializer.init_database()
    messages.success(request, 'Database initialized. Hopefully.')
    # Back to home page.
    return redirect('/')
