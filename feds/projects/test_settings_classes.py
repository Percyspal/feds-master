import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from .models import Project
from .settings_classes import FedsProject, FedsFieldSpec, FedsSetting


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

    def test_project_title_blank(self):
        with self.assertRaises(ValueError):
            t = ''
            p = FedsProject(db_id=1, title=t, description='Desc',
                        slug='sluggy', business_area=1)

    def test_project_title_whitespace(self):
        with self.assertRaises(ValueError):
            t = '  '
            p = FedsProject(db_id=1, title=t, description='Desc',
                        slug='sluggy', business_area=1)

    def test_project_title_none(self):
        with self.assertRaises(TypeError):
            t = None
            p = FedsProject(db_id=1, title=t, description='Desc',
                            slug='sluggy', business_area=1)

    def test_db_id_ok(self):
        id = 1
        p = FedsProject(db_id=id, title='This title is OK', description='Desc',
                        slug='sluggy', business_area=1)
        self.assertEqual(p.db_id, id)

    def test_db_id_missing(self):
        with self.assertRaises(TypeError):
            p = FedsProject(title='This title is OK', description='Desc',
                            slug='sluggy', business_area=1)

    def test_db_id_string(self):
        with self.assertRaises(TypeError):
            p = FedsProject(db_id='DUCK!', title='This title is OK', description='Desc',
                            slug='sluggy', business_area=1)

    def test_db_id_zero(self):
        with self.assertRaises(ValueError):
            p = FedsProject(db_id=0, title='This title is OK', description='Desc',
                            slug='sluggy', business_area=1)

    def test_db_id_neg(self):
        with self.assertRaises(ValueError):
            p = FedsProject(db_id=-1, title='This title is OK', description='Desc',
                            slug='sluggy', business_area=1)

    def test_project_slug_ok(self):
        s = 'slug_fest'
        p = FedsProject(db_id=1, title='DOG!', description='Desc',
                        slug=s, business_area=1)
        self.assertEqual(p.slug, s)

    def test_project_slug_blank(self):
        with self.assertRaises(ValueError):
            s = ''
            p = FedsProject(db_id=1, title='DOG!', description='Desc',
                        slug=s, business_area=1)

    def test_project_slug_whitespace(self):
        with self.assertRaises(ValueError):
            s = '  '
            p = FedsProject(db_id=1, title='DOG!', description='Desc',
                        slug=s, business_area=1)

    def test_project_slug_none(self):
        with self.assertRaises(TypeError):
            s = None
            p = FedsProject(db_id=1, title='DOG!', description='Desc',
                            slug=s, business_area=1)

    def test_project_description_ok(self):
        d = 'DOGZ!'
        p = FedsProject(db_id=1, title='DOG!', description=d,
                        slug='slug_fest', business_area=1)
        self.assertEqual(p.description, d)

    def test_project_business_area_ok(self):
        ba = 1
        p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                        slug='sluggy', business_area=ba)
        self.assertEqual(p.business_area, ba)

    def test_project_business_area_missing(self):
        with self.assertRaises(TypeError):
            p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                            slug='sluggy')

    def test_project_business_area_string(self):
        with self.assertRaises(TypeError):
            p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                            slug='sluggy', business_area='Cows are funny')

    def test_project_business_area_zero(self):
        with self.assertRaises(ValueError):
            p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                            slug='sluggy', business_area=0)

    def test_project_db_id_neg(self):
        with self.assertRaises(ValueError):
            p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                            slug='sluggy', business_area=-1)

    def test_project_add_setting_wrong_type(self):
        with self.assertRaises(TypeError):
            p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                            slug='sluggy', business_area=1)
            s = 666
            p.add_setting(s)

    def test_project_add_notional_table_wrong_type(self):
        with self.assertRaises(TypeError):
            p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                            slug='sluggy', business_area=1)
            t = 666
            p.add_notional_table(t)

    def test_field_spec_types_ok(self):
        ft = [
            'pk',
            'fk',
            'text',
            'zip',
            'phone',
            'email',
            'date',
            'choice',
            'currency',
            'int',
        ]
        p = FedsFieldSpec(db_id=1, title='This title is OK', description='Desc',
                         field_type='pk')
        for t in ft:
            p.field_type = t
            self.assertEqual(p.field_type, t)




        # result = list()
        # result.append(s)
        # self.assertEqual(p.settings, result)
