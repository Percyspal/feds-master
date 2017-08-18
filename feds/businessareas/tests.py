from django.test import TestCase
from django.core.exceptions import ValidationError

from businessareas.models import BusinessArea, \
    AvailableBusinessAreaProjectSetting
from fieldsettings.models import FieldSetting
from feds.settings import FEDS_BASIC_SETTING_GROUP, FEDS_INTEGER_SETTING


class FedsBusinessAreasTests(TestCase):
    def setUp(self):
        pass

    def test_make_business_area_ok(self):
        # Make a business area.
        t = "Dogs!"
        ba = BusinessArea()
        ba.title = t
        ba.save()

        ba2 = BusinessArea.objects.get(pk=ba.pk)
        self.assertEqual(ba2.title, t)

    def test_make_business_area_no_title(self):
        with self.assertRaises(ValidationError):
            ba = BusinessArea()
            ba.save()

    def test_make_business_area_whitespace_title(self):
        with self.assertRaises(ValidationError):
            ba = BusinessArea()
            ba.title = '   '
            ba.save()

    def test_make_business_area_setting(self):
        s = FieldSetting()
        s.title = 'DOGGGG'
        s.setting_group = FEDS_BASIC_SETTING_GROUP
        s.setting_type = FEDS_INTEGER_SETTING
        s.setting_params = '{"title": "Dogs are the best!"}'
        s.save()

        ba = BusinessArea()
        ba.title = "Dogs!"
        # Save before can use M:N relationship.
        ba.save()
        abps = AvailableBusinessAreaProjectSetting()
        abps.business_area = ba
        abps.business_area_setting = s
        abps.save()

        ba2 = BusinessArea.objects.get(pk=ba.pk)
        qs = ba2.available_business_area_project_settings.all()
        self.assertEqual(qs.count(), 1)

        s2 = qs[0]
        self.assertEqual(s2.title, s.title)
