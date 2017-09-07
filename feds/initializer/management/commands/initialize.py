import sys
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from initializer.db_initializer import DbInitializer


# The class must be named Command, and subclass BaseCommand
class Command(BaseCommand):

    # Show this when the user types help
    help = "Initialize the FEDS database."

    # A command must define handle()
    def handle(self, *args, **options):
        """ Initialize database. Migrations have to be run first. """
        try:
            users = User.objects.all()
        except Exception as e:
            self.stdout.write('Exception: ' + e.__str__()
                              + '\nDid you run migrate?')
            sys.exit(1)
        if users.count() > 0:
            self.stdout.write('Current user data found. Maybe you already '
                              'initialized the DB?')
            sys.exit(1)
        db_initializer = DbInitializer()
        db_initializer.init_database()
        self.stdout.write('Database initialized. Hopefully.')
