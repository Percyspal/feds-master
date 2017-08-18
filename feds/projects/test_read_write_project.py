import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from .models import Project
from .internal_representation_classes import FedsProject, FedsFieldSpec, FedsSetting
from .read_write_project import read_project
from businessareas.models import BusinessArea

class FedsReadWriteProjectTests(TestCase):

    def setUp(self):
        # Make some users to be project owners.
        self.u1 = User.objects.create_user('u1', 'u1@example.com', 'u1')
        self.u2 = User.objects.create_user('u2', 'u2@example.com', 'u2')
        # Make a business area.
        self.ba = BusinessArea()
        self.ba.title = "Dogs!"
        self.ba.save()
        # Make a business area setting.

        # Make a project.
        self.project = Project()

    def test_things(self):


        t = 'This title is OK'
        p = FedsProject(db_id=1, title=t, description='Desc',
                        slug='sluggy', business_area=1)
        self.assertEqual(p.title, t)