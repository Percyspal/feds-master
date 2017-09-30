import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from feds.settings import FEDS_BASIC_SETTING_GROUP, FEDS_INTEGER_SETTING
from .models import FieldSettingDb


class FedsFieldSettingsTests(TestCase):
    def setUp(self):
        # Make some users to be project owners.
        # self.u1 = User.objects.create_user('u1', 'u1@example.com', 'u1')
        # self.u2 = User.objects.create_user('u2', 'u2@example.com', 'u2')
        pass

    def test_make_setting_ok(self):
        t = "Dogs!"
        ba = FieldSettingDb()
        ba.title = t
        ba.setting_group = FEDS_BASIC_SETTING_GROUP
        ba.setting_type = FEDS_INTEGER_SETTING
        ba.setting_params = '{"title": "Dogs are the best!"}'
        ba.save()

        ba2 = FieldSettingDb.objects.get(pk=ba.pk)
        self.assertEqual(ba2.title, t)

    def test_make_setting_no_title(self):
        with self.assertRaises(ValidationError):
            ba = FieldSettingDb()
            ba.setting_group = FEDS_BASIC_SETTING_GROUP
            ba.setting_type = FEDS_INTEGER_SETTING
            ba.setting_params = '{"title": "Dogs are the best!"}'
            ba.save()

    def test_make_setting_whitespace_title(self):
        with self.assertRaises(ValidationError):
            ba = FieldSettingDb()
            ba.title = '   '
            ba.setting_group = FEDS_BASIC_SETTING_GROUP
            ba.setting_type = FEDS_INTEGER_SETTING
            ba.setting_params = '{"title": "Dogs are the best!"}'
            ba.save()

    def test_make_setting_bad_group(self):
        with self.assertRaises(ValidationError):
            ba = FieldSettingDb()
            ba.title = 'DOGS!'
            ba.setting_group = 'The Beatles'
            ba.setting_type = FEDS_INTEGER_SETTING
            ba.setting_params = '{"title": "Dogs are the best!"}'
            ba.save()

    def test_make_setting_bad_type(self):
        with self.assertRaises(ValidationError):
            ba = FieldSettingDb()
            ba.title = 'Rosie!'
            ba.setting_group = FEDS_BASIC_SETTING_GROUP
            ba.setting_type = 'Bad'
            ba.setting_params = '{"title": "Dogs are the best!"}'
            ba.save()

    def test_make_setting_bad_params(self):
        with self.assertRaises(ValidationError):
            ba = FieldSettingDb()
            ba.title = 'Rosie!'
            ba.setting_group = FEDS_BASIC_SETTING_GROUP
            ba.setting_type = FEDS_INTEGER_SETTING
            ba.setting_params = '{title": "Dogs are the best!"}'
            ba.save()

