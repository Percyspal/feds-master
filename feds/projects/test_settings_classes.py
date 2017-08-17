import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from .models import Project
from .settings_classes import FedsProject


class FedsSettingsClassesTests(TestCase):

    def setUp(self):
        """ Make some users to be project owners. """
        # self.u1 = User.objects.create_user('u1', 'u1@example.com', 'u1')
        # self.u2 = User.objects.create_user('u2', 'u2@example.com', 'u2')

    def test_project_title_ok(self):
        t = 'This title is OK'
        p = FedsProject(db_id=1, title=t, description='Desc',
                        slug='sluggy', business_area=1)
        self.assertEqual(p.title, t)

    # def test_need_user_for_project(self):
    #     """ Project must have a user. """
    #     with self.assertRaises(ObjectDoesNotExist):
    #         p = Project()
    #         p.title = "DOG"
    #         p.save()

