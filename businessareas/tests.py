from django.test import TestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
from businessareas.models import BusinessAreaDb, \
    AvailableBusinessAreaSettingDb, NotionalTableDb, \
    AvailableNotionalTableSettingDb
from fieldsettings.models import FieldSettingDb
from feds.settings import FEDS_BASIC_SETTING_GROUP, FEDS_INTEGER_SETTING


class FedsBusinessAreasTests(TestCase):
    def setUp(self):
        pass

    def test_make_business_area_ok(self):
        # Make a business area.
        t = "Dogs!"
        ba = BusinessAreaDb()
        ba.title = t
        ba.save()

        ba2 = BusinessAreaDb.objects.get(pk=ba.pk)
        self.assertEqual(ba2.title, t)

    def test_make_business_area_no_title(self):
        with self.assertRaises(ValidationError):
            ba = BusinessAreaDb()
            ba.save()

    def test_make_business_area_whitespace_title(self):
        with self.assertRaises(ValidationError):
            ba = BusinessAreaDb()
            ba.title = '   '
            ba.save()

    def test_make_business_area_setting(self):
        s = FieldSettingDb()
        s.title = 'DOGGGG'
        s.setting_group = FEDS_BASIC_SETTING_GROUP
        s.setting_type = FEDS_INTEGER_SETTING
        s.setting_params = '{"title": "Dogs are the best!"}'
        s.save()

        ba = BusinessAreaDb()
        ba.title = "Dogs!"
        # Save before can use M:N relationship.
        ba.save()
        abps = AvailableBusinessAreaSettingDb()
        abps.business_area = ba
        abps.business_area_setting = s
        abps.save()

        ba2 = BusinessAreaDb.objects.get(pk=ba.pk)
        qs = ba2.available_business_area_settings.all()
        self.assertEqual(qs.count(), 1)

        s2 = qs[0]
        self.assertEqual(s2.title, s.title)

    def test_notional_table_ok(self):
        ba = BusinessAreaDb()
        ba.title = "Dogs!"
        ba.save()

        t = NotionalTableDb()
        t.title = 'More dogs'
        t.business_area = ba
        t.save()

        t2 = NotionalTableDb.objects.get(pk=t.pk)
        self.assertEqual(t2.title, t.title)

    def test_notional_table_no_title(self):
        with self.assertRaises(ValidationError):
            ba = BusinessAreaDb()
            ba.title = "Dogs!"
            ba.save()

            t = NotionalTableDb()
            # t.title = 'More dogs'
            t.business_area = ba
            t.save()

    def test_notional_table_whitespace_title(self):
        with self.assertRaises(ValidationError):
            ba = BusinessAreaDb()
            ba.title = "Dogs!"
            ba.save()

            t = NotionalTableDb()
            t.title = '   '
            t.business_area = ba
            t.save()

    def test_notional_table_no_ba(self):
        with self.assertRaises(Exception):
            t = NotionalTableDb()
            t.title = 'More dogs'
            t.save()

    def test_notional_table_setting_bad_params(self):
        with self.assertRaises(ValidationError):
            ba = BusinessAreaDb()
            ba.title = "Dogs!"
            ba.save()

            t = NotionalTableDb()
            t.title = 'More dogs'
            t.business_area = ba

            s = FieldSettingDb()
            s.title = 'DOGGGG'
            s.setting_group = FEDS_BASIC_SETTING_GROUP
            s.setting_type = FEDS_INTEGER_SETTING
            s.setting_params = '{"title": "Dogs are the best!"}'
            s.save()

            ants = AvailableNotionalTableSettingDb()
            ants.table = t
            ants.table_setting = s
            ants.table_setting_order = 1
            ants.table_setting_params = '{thing":"dog"}'
            ants.save()

    def test_notional_table_setting_ok(self):
        ba = BusinessAreaDb()
        ba.title = "Dogs!"
        ba.save()

        s = FieldSettingDb()
        s.title = 'DOGGGG'
        s.setting_group = FEDS_BASIC_SETTING_GROUP
        s.setting_type = FEDS_INTEGER_SETTING
        s.setting_params = '{"title": "Dogs are the best!"}'
        s.save()

        t = NotionalTableDb()
        t.title = 'More dogs'
        t.business_area = ba
        t.save()

        ants = AvailableNotionalTableSettingDb()
        ants.table = t
        ants.table_setting = s
        ants.table_setting_order = 1
        ants.table_setting_params = '{"thing":"dog"}'
        ants.save()

        sqs = NotionalTableDb.objects.get(pk=t.pk).available_notional_table_settings.all()
        s2 = sqs[0]
        self.assertEqual(s2.title, s.title)

