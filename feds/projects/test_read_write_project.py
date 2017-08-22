from django.test import TestCase
from django.contrib.auth.models import User
from feds.settings import FEDS_BASIC_SETTING_GROUP, FEDS_INTEGER_SETTING, \
    FEDS_TEXT_NOTIONAL_FIELD
from fieldsettings.models import FieldSettingDb
from fieldspecs.models import FieldSpecDb, NotionalTableMembershipDb, \
    AvailableFieldSpecSettingDb
from .models import ProjectDb
from .read_write_project import read_project
from businessareas.models import BusinessAreaDb, \
    AvailableBusinessAreaSettingDb, NotionalTableDb, \
    AvailableNotionalTableSettingDb


class FedsReadWriteProjectTests(TestCase):
    def setUp(self):
        # Make some users to be project owners.
        self.u1 = User.objects.create_user('u1', 'u1@example.com', 'u1')
        self.u2 = User.objects.create_user('u2', 'u2@example.com', 'u2')

        # Make a business area.
        self.ba = BusinessAreaDb(
            title="BA title Revenue",
            machine_name='ba'
        )
        self.ba.save()

        # Make a business area setting.
        self.sales_tax = FieldSettingDb(
            title='BA Setting 1 Sales tax',
            machine_name='sales_tax',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_INTEGER_SETTING,
            setting_params='{"title": "Sales tax", "value": "0.06"}'
        )
        self.sales_tax.save()
        # Attach setting to business area.
        self.ba_sales_tax = AvailableBusinessAreaSettingDb(
            business_area=self.ba,
            business_area_setting=self.sales_tax,
            machine_name='ba_sales_tax',
            business_area_setting_order=1,
            business_area_setting_params="{}"
        )
        self.ba_sales_tax.save()
        # Make a business area setting.
        self.lemurs = FieldSettingDb(
            title='BA Setting 2 Lemurs',
            machine_name='lemurs',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_INTEGER_SETTING,
            setting_params='{}'
        )
        self.lemurs.save()
        # Attach setting to business area.
        self.ba_lemurs = AvailableBusinessAreaSettingDb(
            business_area=self.ba,
            business_area_setting=self.lemurs,
            machine_name='ba_lemurs',
            business_area_setting_order=2,
            business_area_setting_params='{"title": "BA setting Lemurs", '
                                         '"value": 55}'
        )
        self.ba_lemurs.save()

        # Make a notional table
        self.tbl_dog = NotionalTableDb(
            business_area=self.ba,
            title='Table title Dog',
            machine_name='tbl_dogs',
        )
        self.tbl_dog.save()
        # Make a setting for it.
        self.pack_count = FieldSettingDb(
            title='Setting title Pack count',
            machine_name='pack_count',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_INTEGER_SETTING,
            setting_params='{"value": 7}'
        )
        self.pack_count.save()
        # Link setting to table
        self.tbl_dog_pack_count = AvailableNotionalTableSettingDb(
            table=self.tbl_dog,
            table_setting=self.pack_count,
            machine_name='tbl_dog_pack_count',
            table_setting_order=1,
            table_setting_params=''
        )
        self.tbl_dog_pack_count.save()
        # Make a field spec for the table.
        self.name = FieldSpecDb(
            title="Fieldspec Name",
            machine_name='name',
            field_type=FEDS_TEXT_NOTIONAL_FIELD,
        )
        self.name.save()
        self.tbl_dog_field_name = NotionalTableMembershipDb(
            field_spec=self.name,
            notional_table=self.tbl_dog,
            machine_name='tbl_dog_field_name',
            field_order=1
        )
        self.tbl_dog_field_name.save()

        # Make a setting for the spec.
        self.setting_complexity = FieldSettingDb(
            title="Setting title Complexity",
            machine_name='setting_complexity',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_INTEGER_SETTING,
        )
        self.setting_complexity.save()
        self.name_setting_complexity = AvailableFieldSpecSettingDb(
            field_spec=self.name,
            field_setting=self.setting_complexity,
            machine_name='name_setting_complexity',
            field_setting_order=1,
            field_setting_params='{"value": 11}'
        )
        self.name_setting_complexity.save()

        # Make a project.
        self.p = ProjectDb()
        self.p.user = self.u1
        self.p.title = "Project title This is a title"
        self.p.business_area = self.ba
        self.p.save()

    def test_things(self):
        p = read_project(self.p.pk)
        self.assertEqual(p.title, self.p.title)
