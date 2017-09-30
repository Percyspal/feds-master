import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from .models import ProjectDb
from .internal_representation_classes import FedsProject, FedsFieldSpec, \
    FedsSetting, FedsBusinessArea, FedsNotionalTable


class FedsInternalRepresentationClassesTests(TestCase):

    def setUp(self):
        """ Make some users to be project owners. """
        # self.u1 = User.objects.create_user('u1', 'u1@example.com', 'u1')
        # self.u2 = User.objects.create_user('u2', 'u2@example.com', 'u2')

    def test_project_title_ok(self):
        t = 'This title is OK'
        ba = FedsBusinessArea(1, 'Revenue')
        p = FedsProject(db_id=1, title=t, business_area=ba)
        # slug='sluggy',
        self.assertEqual(p.title, t)

    def test_project_title_blank(self):
        with self.assertRaises(ValueError):
            t = ''
            ba = FedsBusinessArea(1, 'Revenue')
            p = FedsProject(db_id=1, title=t, business_area=ba)
            # slug='sluggy',

    def test_project_title_whitespace(self):
        with self.assertRaises(ValueError):
            t = '  '
            ba = FedsBusinessArea(1, 'Revenue')
            p = FedsProject(db_id=1, title=t, business_area=ba)
            # slug='sluggy',

    def test_project_title_none(self):
        with self.assertRaises(TypeError):
            ba = FedsBusinessArea(1, 'Revenue')
            t = None
            p = FedsProject(db_id=1, title=t, business_area=ba)
            # slug='sluggy',

    def test_db_id_ok(self):
        ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
        id = 1
        p = FedsProject(db_id=1, title='Project of doom',
                        business_area=ba)
        # slug='sluggy',
        self.assertEqual(p.db_id, id)

    def test_db_id_missing(self):
        ba = FedsBusinessArea(1, 'Revenue')
        with self.assertRaises(TypeError):
            p = FedsProject(title='This title is OK', business_area=ba)
            # slug='sluggy',

    def test_bad_ba_missing(self):
        ba = 1
        with self.assertRaises(TypeError):
            p = FedsProject(db_id=1, title='This title is OK')
            # slug='sluggy',

    def test_db_id_string(self):
        with self.assertRaises(TypeError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id='DUCK!', title='This title is OK',
                            business_area=ba)
            # slug='sluggy',

    def test_db_id_zero(self):
        with self.assertRaises(ValueError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id=0, title='This title is OK',
                            business_area=ba)
            # slug='sluggy',

    def test_db_id_neg(self):
        with self.assertRaises(ValueError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id=-1, title='This title is OK',
                            business_area=ba)
            # slug='sluggy',

    # def test_project_slug_ok(self):
    #     ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
    #     s = 'slug_fest'
    #     p = FedsProject(db_id=1, title='DOG!', slug=s, business_area=ba)
    #     self.assertEqual(p.slug, s)
    #
    # def test_project_slug_blank(self):
    #     with self.assertRaises(ValueError):
    #         ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
    #         s = ''
    #         p = FedsProject(db_id=1, title='DOG!', slug=s, business_area=ba)
    #
    # def test_project_slug_whitespace(self):
    #     with self.assertRaises(ValueError):
    #         ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
    #         s = '  '
    #         p = FedsProject(db_id=1, title='DOG!', slug=s, business_area=ba)
    #
    # def test_project_slug_none(self):
    #     with self.assertRaises(TypeError):
    #         ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
    #         s = None
    #         p = FedsProject(db_id=1, title='DOG!', slug=s, business_area=ba)

    def test_project_description_ok(self):
        ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
        d = 'DOGZ!'
        p = FedsProject(db_id=1, title='DOG!',
                        business_area=ba, description=d)
        # slug='sluggy',
        self.assertEqual(p.description, d)

    def test_project_business_area_ok(self):
        ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
        p = FedsProject(db_id=1, title='This title is OK', description='Desc',
                        business_area=ba)
        # slug='sluggy',
        self.assertEqual(p.business_area, ba)

    def test_project_business_area_missing(self):
        with self.assertRaises(TypeError):
            p = FedsProject(db_id=1, title='This title is OK')
            # slug='sluggy',

    def test_project_business_area_string(self):
        with self.assertRaises(TypeError):
            p = FedsProject(db_id=1, title='This title is OK',
                            business_area='Cows are funny')
            # slug='sluggy',

    def test_project_add_setting_wrong_type(self):
        with self.assertRaises(TypeError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id=1, title='This title is OK', business_area=ba)
            # slug='sluggy',
            s = 666
            p.add_setting(s)

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
        p = FedsFieldSpec(db_id=1, title='This title is OK',
                          machine_name='dog',
                          description='Desc',
                          field_type='pk')
        for t in ft:
            p.field_type = t
            self.assertEqual(p.field_type, t)
        del p

    def test_notional_tables(self):
        ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
        p = FedsProject(db_id=1, title='This title is OK',
                        business_area=ba)
        # slug='sluggy',
        t1 = FedsNotionalTable(db_id=1, title='T1')
        t2 = FedsNotionalTable(db_id=2, title='T2')
        p.add_notional_table(t1)
        p.add_notional_table(t2)
        self.assertEqual(t1.title, 'T1')

    def test_project_add_notional_table_wrong_type(self):
        with self.assertRaises(TypeError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id=1, title='This title is OK',
                            business_area=ba)
            # slug='sluggy',
            t = 666
            p.add_notional_table(t)

    def test_duplicate_machine_names(self):
        with self.assertRaises(ValueError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id=1, title='This title is OK',
                            business_area=ba)
            # slug='sluggy',
            t1 = FedsNotionalTable(db_id=1, title='T1',
                                   description='', machine_name='mn1')
            t2 = FedsNotionalTable(db_id=2, title='T2',
                                   description='', machine_name='mn1')
            p.add_notional_table(t1)
            p.add_notional_table(t2)

    def test_duplicate_implied_machine_names(self):
        with self.assertRaises(ValueError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id=1, title='This title is OK',
                            business_area=ba)
            # slug='sluggy',
            t1 = FedsNotionalTable(db_id=1, title='T1',
                                   description='')
            t2 = FedsNotionalTable(db_id=2, title='T1',
                                   description='')
            p.add_notional_table(t1)
            p.add_notional_table(t2)

    def test_duplicate_machine_names2(self):
        with self.assertRaises(ValueError):
            ba = FedsBusinessArea(1, 'Revenue', 'DOGOS!')
            p = FedsProject(db_id=1, title='This title is OK',
                            # slug='sluggy',
                            business_area=ba)
            t1 = FedsNotionalTable(db_id=1, title='T1',
                                   description='', machine_name='fred')
            t2 = FedsNotionalTable(db_id=2, title='Fred',
                                   description='')
            p.add_notional_table(t1)
            p.add_notional_table(t2)
