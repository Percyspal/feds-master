from django.contrib.auth.models import User
import datetime
from helpers.model_helpers import stringify_date
from .secrets import secret_superuser_deets, secret_users, secret_pages
from accounts.models import Profile
from sitepages.models import SitePage
from businessareas.models import BusinessAreaDb, NotionalTableDb, \
    AvailableNotionalTableSettingDb, AvailableBusinessAreaSettingDb
from fieldspecs.models import FieldSpecDb, NotionalTableMembershipDb
from fieldspecs.models import FieldSettingDb, AvailableFieldSpecSettingDb
from feds.settings import FEDS_BOOLEAN_SETTING, \
    FEDS_CHOICE_SETTING, FEDS_CURRENCY_SETTING, FEDS_FLOAT_SETTING, \
    FEDS_BASIC_SETTING_GROUP, FEDS_ANOMALY_GROUP, \
    FEDS_VALUE_PARAM, FEDS_BOOLEAN_VALUE_FALSE, \
    FEDS_INTEGER_SETTING, FEDS_MIN_PARAM, FEDS_MAX_PARAM, \
    FEDS_NORMAL_DISTRIBUTION, \
    FEDS_STAT_DISTRIBUTION_CHOCIES, \
    FEDS_NORMAL_DISTRIBUTION_MEAN_TOTAL_BEFORE_TAX_DEFAULT, \
    FEDS_CHOICES_PARAM, \
    FEDS_SALES_TAX_SETTING_DEFAULT, FEDS_CHOICE_NOTIONAL_FIELD, \
    FEDS_PAYMENT_TYPES, FEDS_WORKING_DAYS, FEDS_WORKING_DAYS_WEEKDAYS, \
    FEDS_EXPORT_TABLES, FEDS_EXPORT_TABLES_JOINED, FEDS_NUMBER_STYLE, \
    FEDS_NUMBER_STYLE_SIMPLE, FEDS_MIN_NUMBER_CUSTOMERS, \
    FEDS_MAX_NUMBER_CUSTOMERS, FEDS_PROJECT_DATES_OPTIONS, \
    FEDS_LAST_CALENDAR_YEAR, \
    FEDS_NUM_CUSTOMERS_OPTIONS, \
    FEDS_NUM_CUSTOMERS_STANDARD, FEDS_NUM_INVOICES_PER_CUST_OPTIONS, \
    FEDS_NUM_INVOICES_PER_CUST_STANDARD, FEDS_CUST_INVOICES_PER_CUST_DEFAULT, \
    FEDS_MIN_CUST_INVOICES_PER_CUST, FEDS_MAX_CUST_INVOICES_PER_CUST, \
    FEDS_NUM_CUSTOMERS_CUSTOM_DEFAULT, FEDS_NUM_PRODUCTS_STANDARD, \
    FEDS_NUM_PRODUCTS_CUSTOM, FEDS_NUM_PRODUCTS_CUSTOM_DEFAULT, \
    FEDS_MIN_PRODUCTS, FEDS_MAX_PRODUCTS, \
    FEDS_CUSTOM_DATE_RANGE, FEDS_MACHINE_NAME_PARAM, \
    FEDS_DETERMINING_VALUE_PARAM, FEDS_VISIBILITY_TEST_PARAM, \
    FEDS_DATE_SETTING, FEDS_START_DATE_DEFAULT, FEDS_END_DATE_DEFAULT, \
    FEDS_MIN_DATE, FEDS_NUM_CUSTOMERS_CUSTOM, FEDS_NUM_INVOICES_PER_CUST_CUSTOM


# noinspection PyAttributeOutsideInit,PyMethodMayBeStatic
class DbInitializer:
    """ Initialize the database with starting data. """

    def init_database(self):
        self.make_superuser()
        # Make other users.
        self.make_regular_users()
        # Make some pages.
        self.make_pages()
        self.erase_field_settings()
        self.make_business_area()
        self.make_business_area_settings()
        self.make_notional_tables()
        self.make_customer_fields()
        self.make_invoice_fields()
        self.make_invoice_detail_fields()
        self.make_product_fields()
        self.make_field_settings_customer()
        self.make_table_settings_customer()
        self.make_field_settings_invoice()
        self.make_table_settings_invoice()

    def make_superuser(self):
        """ Make the superuser. """
        # TODO: set other user fields.
        superuser_deets = secret_superuser_deets()
        superuser = User.objects.create_superuser(
            superuser_deets['username'],
            superuser_deets['email'],
            superuser_deets['password']
        )
        profile = Profile()
        profile.user = superuser
        profile.save()

    def make_regular_users(self):
        """ Make other users. """
        # TODO: set other user fields.
        users = secret_users()
        for username, user_deets in users.items():
            user = User.objects.create_user(
                username,
                email=user_deets['email'],
                password=user_deets['password'],
            )
            profile = Profile()
            profile.user = user
            profile.save()

    def make_pages(self):
        """ Make some pages. """
        # Erase existing pages first.
        SitePage.objects.all().delete()
        # Get specs for pages.
        page_specs = secret_pages()
        # Make them.
        for page_spec in page_specs:
            site_page = SitePage()
            site_page.title = page_spec['title']
            site_page.slug = page_spec['slug']
            site_page.content = page_spec['content']
            site_page.save()

    def make_business_area(self):
        BusinessAreaDb.objects.all().delete()
        self.revenue_business_area = BusinessAreaDb(
            title='Revenue',
            description='Sell products to customers.',
            machine_name='revenue'
        )
        self.revenue_business_area.save()

    def make_common_settings(self):
        # Make settings that are used in several places. They are
        # partially defined here, and partially in their relationships
        # with tables and fields.

        self.anomaly_arithmetic_errors = FieldSettingDb(
            title='Arithmetic errors',
            description='Errors in calculated fields.',
            machine_name='anomaly_arithmetic_errors',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_arithmetic_errors.save()

        self.anomaly_violates_benfords_law = FieldSettingDb(
            title='Violates Benford\'s law',
            description='The data violates Benford\'s law.',
            machine_name='anomaly_violates_benfords_law',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_violates_benfords_law.save()

        self.anomaly_negative_numbers = FieldSettingDb(
            title='Negative numbers',
            description='There are negative numbers in the data.',
            machine_name='anomaly_negative_numbers',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_negative_numbers.save()

        self.anomaly_missing = FieldSettingDb(
            title='Missing',
            description='Sometimes the data is missing.',
            machine_name='anomaly_missing',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_missing.save()

        self.anomaly_out_of_range = FieldSettingDb(
            title='Out of project range',
            description='Some values are outside the project\'s range.',
            machine_name='anomaly_out_of_range',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_out_of_range.save()

        self.anomaly_duplicate_values = FieldSettingDb(
            title='Duplicate values',
            description='Some values are duplicated.',
            machine_name='anomaly_duplicate_values',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_duplicate_values.save()


    def make_business_area_settings(self):
        # Add settings for the business areas.

        # Project dates choices
        self.project_date_choices = FieldSettingDb(
            title='Project date options',
            machine_name='project_date_choices',
            description='Date range for the project.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            setting_params={
                FEDS_CHOICES_PARAM: FEDS_PROJECT_DATES_OPTIONS,
                FEDS_VALUE_PARAM: FEDS_LAST_CALENDAR_YEAR,
            }
        )
        self.project_date_choices.save()
        # Link setting to business area.
        self.ba_revenue_setting_project_date_choices \
            = AvailableBusinessAreaSettingDb(
              business_area=self.revenue_business_area,
              business_area_setting=self.project_date_choices,
              machine_name='ba_revenue_setting_project_date_choices',
              business_area_setting_order=1,
            )
        self.ba_revenue_setting_project_date_choices.save()

        # Custom start date range.
        # Todo: make sure end date > start date.
        self.project_custom_start_date = FieldSettingDb(
            title='Project date range: start',
            machine_name='project_custom_start_date',
            description='Start date. Format YYYY/MM/DD.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_DATE_SETTING,
            setting_params={
                FEDS_VALUE_PARAM: FEDS_START_DATE_DEFAULT,
                # Setting visible when machine name given equals value given.
                FEDS_VISIBILITY_TEST_PARAM: {
                    FEDS_MACHINE_NAME_PARAM:
                        'ba_revenue_setting_project_date_choices',
                    FEDS_DETERMINING_VALUE_PARAM: FEDS_CUSTOM_DATE_RANGE,
                },
                FEDS_MIN_PARAM: FEDS_MIN_DATE,
            }
        )
        self.project_custom_start_date.save()
        # Link start date setting to business area.
        self.ba_revenue_setting_project_custom_start_date \
            = AvailableBusinessAreaSettingDb(
              business_area=self.revenue_business_area,
              business_area_setting=self.project_custom_start_date,
              machine_name='ba_revenue_setting_project_custom_start_date',
              business_area_setting_order=2,
            )
        self.ba_revenue_setting_project_custom_start_date.save()

        # Custom end date.
        self.project_custom_end_date = FieldSettingDb(
            title='Project date range: end',
            machine_name='project_custom_end_date',
            description='End date. Format YYYY/MM/DD.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_DATE_SETTING,
            setting_params={
                # Default date plus a month.
                FEDS_VALUE_PARAM: FEDS_END_DATE_DEFAULT,
                # Setting visible when machine name given equals value given.
                FEDS_VISIBILITY_TEST_PARAM: {
                    FEDS_MACHINE_NAME_PARAM: 'ba_revenue_setting_project_date_choices',
                    FEDS_DETERMINING_VALUE_PARAM: FEDS_CUSTOM_DATE_RANGE,
                FEDS_MIN_PARAM: FEDS_MIN_DATE,
                }
            }
        )
        self.project_custom_end_date.save()
        # Link setting to business area.
        self.ba_revenue_setting_project_custom_end_date \
            = AvailableBusinessAreaSettingDb(
              business_area=self.revenue_business_area,
              business_area_setting=self.project_custom_end_date,
              machine_name='ba_revenue_setting_project_custom_end_date',
              business_area_setting_order=3,
            )
        self.ba_revenue_setting_project_custom_end_date.save()

        # Working days.
        self.working_days = FieldSettingDb(
            title='Working days',
            machine_name='working_days',
            description='What days are sales made?',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            setting_params={
                FEDS_CHOICES_PARAM: FEDS_WORKING_DAYS,
                FEDS_VALUE_PARAM: FEDS_WORKING_DAYS_WEEKDAYS,
            }
        )
        self.working_days.save()
        # Link setting to business area.
        self.ba_revenue_setting_working_days \
            = AvailableBusinessAreaSettingDb(
              business_area=self.revenue_business_area,
              business_area_setting=self.working_days,
              machine_name='ba_revenue_setting_working_days',
              business_area_setting_order=4,
            )
        self.ba_revenue_setting_working_days.save()

        # Export objects.
        self.export_objects = FieldSettingDb(
            title='Export objects',
            machine_name='export_objects',
            description='What objects are exported.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            setting_params={
                FEDS_CHOICES_PARAM: FEDS_EXPORT_TABLES,
                FEDS_VALUE_PARAM: FEDS_EXPORT_TABLES_JOINED
            }
        )
        self.export_objects.save()
        # Link setting to business area.
        self.ba_revenue_setting_export_objects \
            = AvailableBusinessAreaSettingDb(
              business_area=self.revenue_business_area,
              business_area_setting=self.export_objects,
              machine_name='ba_revenue_setting_export_objects',
              business_area_setting_order=5,
            )
        self.ba_revenue_setting_export_objects.save()

        # Sales tax for the revenue area.
        self.sales_tax = FieldSettingDb(
            title='Sales tax rate',
            machine_name='setting_sales_tax',
            description='Sales tax rate, e.g., 0.06',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_FLOAT_SETTING,
            # Set default.
            setting_params={
                FEDS_VALUE_PARAM: FEDS_SALES_TAX_SETTING_DEFAULT,
                FEDS_MIN_PARAM: 0,
                FEDS_MAX_PARAM: 0.90,
            }
        )
        self.sales_tax.save()
        # Link setting to business area.
        self.ba_revenue_setting_sales_tax \
            = AvailableBusinessAreaSettingDb(
              business_area=self.revenue_business_area,
              business_area_setting=self.sales_tax,
              machine_name='ba_revenue_setting_sales_tax',
              business_area_setting_order=6,
            )
        self.ba_revenue_setting_sales_tax.save()

        # Number style.
        self.number_style = FieldSettingDb(
            title='Number style',
            machine_name='number_style',
            description='Number style.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            setting_params={
                FEDS_CHOICES_PARAM: FEDS_NUMBER_STYLE,
                FEDS_VALUE_PARAM: FEDS_NUMBER_STYLE_SIMPLE
            }
        )
        self.number_style.save()
        # Link setting to business area.
        self.ba_revenue_setting_number_style \
            = AvailableBusinessAreaSettingDb(
              business_area=self.revenue_business_area,
              business_area_setting=self.number_style,
              machine_name='ba_revenue_setting_number_style',
              business_area_setting_order=7,
            )
        self.ba_revenue_setting_number_style.save()

    def make_notional_tables(self):
        NotionalTableDb.objects.all().delete()
        self.tbl_customer = NotionalTableDb(
            business_area=self.revenue_business_area,
            title='Customer',
            machine_name='tbl_customer',
            description='Customers buying products.',
            display_order=1,
        )
        self.tbl_customer.save()

        self.tbl_invoice = NotionalTableDb(
            business_area=self.revenue_business_area,
            title='Invoice',
            machine_name='tbl_invoice',
            description='Invoices sent to customers.',
            display_order=2,
        )
        self.tbl_invoice.save()

        self.tbl_invoice_detail = NotionalTableDb(
            business_area=self.revenue_business_area,
            title='InvoiceDetail',
            machine_name='tbl_invoice_detail',
            description='Lines on invoices.',
            display_order=3,
        )
        self.tbl_invoice_detail.save()

        self.tbl_product = NotionalTableDb(
            business_area=self.revenue_business_area,
            title='Product',
            machine_name='tbl_product',
            description='Products purchased by customers',
            display_order=4,
        )
        self.tbl_product.save()

    def make_customer_fields(self):
        # Clear existing FieldSpecs for the customer table, and their table
        # membership records.
        FieldSpecDb.objects.filter(notional_tables=self.tbl_customer).delete()
        NotionalTableMembershipDb.objects \
            .filter(notional_table=self.tbl_customer).delete()

        # Make field for customer PK.
        self.customer_pk = FieldSpecDb(
            title='CustomerId',
            machine_name='fld_spec_cust_pk',
            description='Customer table primary key.',
            field_type='pk',
        )
        self.customer_pk.save()
        # Record that customer PK is in the customer table.
        self.customer_pk_table_membership = NotionalTableMembershipDb(
            field_spec=self.customer_pk,
            notional_table=self.tbl_customer,
            machine_name='tbl_cust_fld_spec_cust_pk',
            field_order=1
        )
        self.customer_pk_table_membership.save()

        # Make a FieldSpec for the customer name.
        self.customer_name = FieldSpecDb(
            title='CName',
            machine_name='fld_spec_cust_name',
            description="Customer's first and last name",
            field_type='text',
        )
        self.customer_name.save()
        # Record that customer name is in the customer table.
        self.customer_name_table_membership = NotionalTableMembershipDb(
            field_spec=self.customer_name,
            notional_table=self.tbl_customer,
            machine_name='tbl_cust_fld_spec_cust_name',
            field_order=2
        )
        self.customer_name_table_membership.save()

        # Make a FieldSpec for the customer address.
        self.customer_address = FieldSpecDb(
            title='CAddress',
            machine_name='fld_spec_cust_addr',
            description="Customer's address",
            field_type='text',
        )
        self.customer_address.save()
        # Record that customer address is in the customer table.
        self.customer_address_table_membership = NotionalTableMembershipDb(
            field_spec=self.customer_address,
            notional_table=self.tbl_customer,
            machine_name='tbl_cust_fld_spec_cust_addr',
            field_order=3
        )
        self.customer_address_table_membership.save()

        # Make a FieldSpec for the customer zip code.
        self.customer_zip = FieldSpecDb(
            title='CZipCode',
            machine_name='fld_spec_zip',
            description="Customer's zip code",
            field_type='text',
        )
        self.customer_zip.save()
        # Record that customer zip is in the customer table.
        self.customer_zip_table_membership = NotionalTableMembershipDb(
            field_spec=self.customer_zip,
            notional_table=self.tbl_customer,
            machine_name='tbl_cust_fld_spec_zip',
            field_order=4
        )
        self.customer_zip_table_membership.save()

        # Make a FieldSpec for the customer phone number.
        self.customer_phone = FieldSpecDb(
            title='CPhone',
            machine_name='fld_spec_phone',
            description="Customer's phone number",
            field_type='text',
        )
        self.customer_phone.save()
        # Record that customer phone is in the customer table.
        self.customer_phone_table_membership = NotionalTableMembershipDb(
            field_spec=self.customer_phone,
            notional_table=self.tbl_customer,
            machine_name='tbl_cust_fld_spec_phone',
            field_order=5
        )
        self.customer_phone_table_membership.save()

        # Make a FieldSpec for the customer email.
        self.customer_email = FieldSpecDb(
            title='CEmail',
            machine_name='fld_spec_email',
            description="Customer's email address",
            field_type='email',
        )
        self.customer_email.save()
        # Record that customer email is in the customer table.
        self.customer_email_table_membership = NotionalTableMembershipDb(
            field_spec=self.customer_email,
            notional_table=self.tbl_customer,
            machine_name='tbl_cust_fld_spec_email',
            field_order=6
        )
        self.customer_email_table_membership.save()

    def make_invoice_fields(self):
        # Clear existing FieldSpecs for the customer table, and their table
        # membership records.
        FieldSpecDb.objects.filter(notional_tables=self.tbl_invoice).delete()
        NotionalTableMembershipDb.objects \
            .filter(notional_table=self.tbl_invoice).delete()

        # Make a FieldSpec for the invoice id.
        self.invoice_pk = FieldSpecDb(
            title='InvoiceNumber',
            machine_name='fld_spec_invc_pk',
            description='Invoice table primary key',
            field_type='pk',
        )
        self.invoice_pk.save()
        # Record that invoice pk is in the invoice table.
        self.invoice_pk_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_pk,
            notional_table=self.tbl_invoice,
            machine_name='tbl_invc_fld_spec_invc_pk',
            field_order=1
        )
        self.invoice_pk_table_membership.save()

        # Make a FieldSpec for the invoice's customer FK.
        self.invoice_customer_id = FieldSpecDb(
            title='CustomerId',
            machine_name='fld_spec_cust_fk',
            description='Foreign key into Customer table',
            field_type='fk',
        )
        self.invoice_customer_id.save()
        # Record that invoice customer id is in the invoice table.
        self.invoice_customer_id_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_customer_id,
            notional_table=self.tbl_invoice,
            machine_name='tbl_invc_fld_spec_cust_fk',
            field_order=2
        )
        self.invoice_customer_id_table_membership.save()

        # Make a FieldSpec for the invoice date.
        self.invoice_date = FieldSpecDb(
            title='InvoiceDate',
            description='Invoice date',
            machine_name='fld_spec_invc_date',
            field_type='date',
        )
        self.invoice_date.save()
        # Record that invoice date is in the invoice table.
        self.invoice_date_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_date,
            notional_table=self.tbl_invoice,
            machine_name='tbl_invc_fld_spec_invc_date',
            field_order=3
        )
        self.invoice_date_table_membership.save()

        # Make a FieldSpec for the invoice's payment type.
        self.invoice_payment_type = FieldSpecDb(
            title='PaymentType',
            machine_name='fld_spec_paymnt_type',
            description='Payment type',
            field_type=FEDS_CHOICE_NOTIONAL_FIELD,
            field_params={
                FEDS_CHOICES_PARAM: FEDS_PAYMENT_TYPES
            }
        )
        self.invoice_payment_type.save()
        # Record that invoice payment_type is in the invoice table.
        self.invoice_payment_type_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_payment_type,
            notional_table=self.tbl_invoice,
            machine_name='tbl_invc_fld_spec_paymnt_type',
            field_order=4
        )
        self.invoice_payment_type_table_membership.save()

        # Make a FieldSpec for the invoice's credit terms.
        self.invoice_credit_terms = FieldSpecDb(
            title='CreditTerms',
            machine_name='fld_spec_cred_terms',
            description='Credit terms',
            field_type='text',
        )
        self.invoice_credit_terms.save()
        # Record that invoice credit terms is in the invoice table.
        self.invoice_credit_terms_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_credit_terms,
            notional_table=self.tbl_invoice,
            machine_name='tbl_invc_fld_spec_cred_terms',
            field_order=5
        )
        self.invoice_credit_terms_table_membership.save()

        # Make a FieldSpec for the invoice's due date
        self.invoice_due_date = FieldSpecDb(
            title='DueDate',
            machine_name='fld_spec_due_date',
            description='When payment is due',
            field_type='date',
        )
        self.invoice_due_date.save()
        # Record that invoice due_date is in the invoice table.
        self.invoice_due_date_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_due_date,
            machine_name='tbl_invc_fld_spec_due_date',
            notional_table=self.tbl_invoice,
            field_order=6
        )
        self.invoice_due_date_table_membership.save()

        # Make a FieldSpec for the invoice's shipping method.
        self.invoice_shipping_method = FieldSpecDb(
            title='ShippingMethod',
            machine_name='fld_spec_ship_meth',
            description='How the order is shipped',
            field_type='text',
        )
        self.invoice_shipping_method.save()
        # Record that invoice shipping method is in the invoice table.
        self.invoice_shipping_method_table_membership \
            = NotionalTableMembershipDb(
              field_spec=self.invoice_shipping_method,
              notional_table=self.tbl_invoice,
              machine_name='tbl_invc_fld_spec_ship_meth',
              field_order=7
            )
        self.invoice_shipping_method_table_membership.save()

        # Make a FieldSpec for the invoice's shipping terms.
        self.invoice_shipping_terms = FieldSpecDb(
            title='ShippingTerms',
            machine_name='fld_spec_ship_terms',
            description='Shipping terms',
            field_type='text',
        )
        self.invoice_shipping_terms.save()
        # Record that invoice shipping terms is in the invoice table.
        self.invoice_shipping_terms_table_membership \
            = NotionalTableMembershipDb(
              field_spec=self.invoice_shipping_terms,
              notional_table=self.tbl_invoice,
              machine_name='tbl_invc_fld_spec_ship_terms',
              field_order=8
            )
        self.invoice_shipping_terms_table_membership.save()

        # Make a FieldSpec for the invoice total before tax.
        self.invoice_total_before_tax = FieldSpecDb(
            title='TotalBTax',
            description='Invoice total before tax',
            machine_name='fld_spec_total_bt',
            field_type='currency',
        )
        self.invoice_total_before_tax.save()
        # Record that invoice total before tax is in the invoice table.
        self.invoice_total_before_tax_table_membership \
            = NotionalTableMembershipDb(
              field_spec=self.invoice_total_before_tax,
              notional_table=self.tbl_invoice,
              machine_name='tbl_invc_fld_spec_total_bt',
              field_order=9
            )
        self.invoice_total_before_tax_table_membership.save()

        # Make a FieldSpec for the invoice sales tax.
        self.invoice_sales_tax \
            = FieldSpecDb(
              title='SalesTax',
              machine_name='fld_spec_sales_tax',
              description='Invoice sales tax',
              field_type='currency',
            )
        self.invoice_sales_tax.save()
        # Record that invoice sales tax is in the invoice table.
        self.invoice_sales_tax_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_sales_tax,
            notional_table=self.tbl_invoice,
            machine_name='tbl_invc_fld_spec_sales_tax',
            field_order=10
        )
        self.invoice_sales_tax_table_membership.save()

        # Make a FieldSpec for the invoice total.
        self.invoice_total = FieldSpecDb(
            title='Total',
            description='Invoice total',
            machine_name='fld_spec_invc_tot',
            field_type='currency',
        )
        self.invoice_total.save()
        # Record that invoice total is in the invoice table.
        self.invoice_total_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_total,
            notional_table=self.tbl_invoice,
            machine_name='tbl_invc_fld_spec_invc_tot',
            field_order=11
        )
        self.invoice_total_table_membership.save()

    def make_invoice_detail_fields(self):
        # Clear existing FieldSpecs for the invoice detail table, and their
        # table membership records.
        FieldSpecDb.objects.filter(notional_tables=self.tbl_invoice_detail) \
            .delete()
        NotionalTableMembershipDb.objects \
            .filter(notional_table=self.tbl_invoice_detail).delete()

        # Make a FieldSpec for the invoice detail pk.
        self.invoice_detail_pk = FieldSpecDb(
            title='InvDetailNumber',
            machine_name='fld_spec_invc_detl_pk',
            description='InvoiceDetail table primary key',
            field_type='pk',
        )
        self.invoice_detail_pk.save()
        # Record that invoice details PK is in the invoice details table.
        self.invoice_detail_pk_table_membership = NotionalTableMembershipDb(
            field_spec=self.invoice_detail_pk,
            notional_table=self.tbl_invoice_detail,
            machine_name='tbl_inv_detl_fld_spec_invc_detl_pk',
            field_order=1
        )
        self.invoice_detail_pk_table_membership.save()

        # Make a FieldSpec for the invoice detail invoice number.
        self.invoice_detail_invoice_number = FieldSpecDb(
            title='InvoiceNumber',
            machine_name='fld_spec_invoice_fk',
            description='Foreign key into Invoice table',
            field_type='fk',
        )
        self.invoice_detail_invoice_number.save()
        # Record that invoice details invoice number is in the invoice
        # details table.
        self.invoice_detail_invoice_number_table_membership \
            = NotionalTableMembershipDb(
              field_spec=self.invoice_detail_invoice_number,
              notional_table=self.tbl_invoice_detail,
              machine_name='tbl_inv_detl_fld_spec_invoice_fk',
              field_order=2
            )
        self.invoice_detail_invoice_number_table_membership.save()

        # Make a FieldSpec for the invoice detail product id.
        self.invoice_detail_product_id = FieldSpecDb(
            title='ProductId',
            machine_name='fld_spec_prod_fk',
            description='Foreign key into Product table',
            field_type='fk',
        )
        self.invoice_detail_product_id.save()
        # Record that invoice details product id is in the invoice details
        # table.
        self.invoice_detail_product_id_table_membership \
            = NotionalTableMembershipDb(
              field_spec=self.invoice_detail_product_id,
              notional_table=self.tbl_invoice_detail,
              machine_name='tbl_inv_detl_fld_spec_prod_fk',
              field_order=3
            )
        self.invoice_detail_product_id_table_membership.save()

        # Make a FieldSpec for the invoice detail quantity.
        self.invoice_detail_quantity = FieldSpecDb(
            title='Quantity',
            description='Invoiced quantity',
            machine_name='fld_spec_quantity',
            field_type='int',
        )
        self.invoice_detail_quantity.save()
        # Record that invoice details quantity is in the invoice details table.
        self.invoice_detail_quantity_table_membership \
            = NotionalTableMembershipDb(
              field_spec=self.invoice_detail_quantity,
              notional_table=self.tbl_invoice_detail,
              machine_name='tbl_inv_detl_fld_spec_quantity',
              field_order=4
            )
        self.invoice_detail_quantity_table_membership.save()

        # Make a FieldSpec for the invoice detail product subtotal.
        self.invoice_detail_subtotal_product = FieldSpecDb(
            title='SubtotalProduct',
            machine_name='fld_spec_prod_subtot',
            description='Subtotal for detail line',
            field_type='currency',
        )
        self.invoice_detail_subtotal_product.save()
        # Record that invoice details subtotal product is in the invoice
        # details table.
        self.invoice_detail_subtotal_product_table_membership \
            = NotionalTableMembershipDb(
              field_spec=self.invoice_detail_subtotal_product,
              notional_table=self.tbl_invoice_detail,
              machine_name='tbl_inv_detl_fld_spec_prod_subtot',
              field_order=5
            )
        self.invoice_detail_subtotal_product_table_membership.save()

    def make_product_fields(self):
        # Clear existing FieldSpecs for the product table, and their table
        # membership records.
        FieldSpecDb.objects.filter(notional_tables=self.tbl_product).delete()
        NotionalTableMembershipDb.objects.filter(
            notional_table=self.tbl_product).delete()

        # Make a FieldSpec for the product PK.
        self.product_pk = FieldSpecDb(
            title='ProductId',
            machine_name='fld_spec_prod_pk',
            description='Product table primary key',
            field_type='pk',
        )
        self.product_pk.save()
        # Record that product pk is in the product table.
        self.product_pk_table_membership = NotionalTableMembershipDb(
            field_spec=self.product_pk,
            notional_table=self.tbl_product,
            machine_name='tbl_prod_fld_spec_prod_pk',
            field_order=1
        )
        self.product_pk_table_membership.save()

        # Make a FieldSpec for the product description.
        self.product_description = FieldSpecDb(
            title='Description',
            machine_name='fld_spec_prod_desc',
            description='Product description',
            field_type='text',
        )
        self.product_description.save()
        # Record that product description is in the product table.
        self.product_description_table_membership = NotionalTableMembershipDb(
            field_spec=self.product_description,
            notional_table=self.tbl_product,
            machine_name='tbl_prod_fld_spec_prod_desc',
            field_order=2
        )
        self.product_description_table_membership.save()

        # Make a FieldSpec for the product price.
        self.product_price = FieldSpecDb(
            title='ProdPrice',
            machine_name='fld_spec_prod_price',
            description='Product price',
            field_type='currency',
        )
        self.product_price.save()
        # Record that product price is in the product table.
        self.product_price_table_membership = NotionalTableMembershipDb(
            field_spec=self.product_price,
            notional_table=self.tbl_product,
            machine_name='tbl_prod_fld_spec_prod_price',
            field_order=3
        )
        self.product_price_table_membership.save()

    def erase_field_settings(self):
        FieldSettingDb.objects.all().delete()
        AvailableFieldSpecSettingDb.objects.all().delete()

    def make_field_settings_customer(self):
        # Link duplicate values to customer PK.
        self.fld_spec_customer_pk_anomaly_duplicate_values \
            = AvailableFieldSpecSettingDb(
              field_spec=self.customer_pk,
              field_setting=self.anomaly_duplicate_values,
              machine_name='fld_spec_customer_pk_anomaly_duplicate_values',
              field_setting_order=1,
              field_setting_params={}
            )
        self.fld_spec_customer_pk_anomaly_duplicate_values.save()


    def make_table_settings_customer(self):
        # Number of customers options.
        self.setting_num_cust_options = FieldSettingDb(
            title='Number of customers options',
            machine_name='setting_num_cust_options',
            description='How the number of customers is determined.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            setting_params={
                           FEDS_CHOICES_PARAM: FEDS_NUM_CUSTOMERS_OPTIONS,
                           FEDS_VALUE_PARAM: FEDS_NUM_CUSTOMERS_STANDARD,
                           }
        )
        self.setting_num_cust_options.save()
        # Link setting to customer table.
        self.tbl_customer_setting_num_cust_options \
            = AvailableNotionalTableSettingDb(
              table=self.tbl_customer,
              table_setting=self.setting_num_cust_options,
              machine_name='tbl_customer_setting_num_cust_options',
              table_setting_order=1,
            )
        self.tbl_customer_setting_num_cust_options.save()

        # Custom number of customers.
        self.setting_cust_num_custs = FieldSettingDb(
            title='Number of customers',
            machine_name='setting_cust_num_custs',
            description='Number of customer records that will be generated.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_INTEGER_SETTING,
            # Set default.
            setting_params={
                           FEDS_VALUE_PARAM: FEDS_NUM_CUSTOMERS_CUSTOM_DEFAULT,
                           # Setting visible when machine name given
                           # equals value given.
                           FEDS_VISIBILITY_TEST_PARAM: {
                               FEDS_MACHINE_NAME_PARAM:
                                   'tbl_customer_setting_num_cust_options',
                               FEDS_DETERMINING_VALUE_PARAM:
                                   FEDS_NUM_CUSTOMERS_CUSTOM,
                           },
                           FEDS_MIN_PARAM: FEDS_MIN_NUMBER_CUSTOMERS,
                           FEDS_MAX_PARAM: FEDS_MAX_NUMBER_CUSTOMERS,
                           }
        )
        self.setting_cust_num_custs.save()
        # Link setting to customer table.
        self.tbl_customer_setting_cust_num_custs \
            = AvailableNotionalTableSettingDb(
              table=self.tbl_customer,
              table_setting=self.setting_cust_num_custs,
              machine_name='tbl_customer_setting_cust_num_custs',
              table_setting_order=2,
            )
        self.tbl_customer_setting_cust_num_custs.save()

    def make_field_settings_invoice(self):

        # Make anomaly - skip some invoice numbers.
        self.anomaly_skip_invoice_numbers = FieldSettingDb(
            title='Skip some invoice numbers',
            description='If on, there will be gaps in the invoice number '
                        'sequence.',
            machine_name='anomaly_skip_invoice_numbers',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_skip_invoice_numbers.save()
        # Link anomaly to invoice number field spec.
        self.fld_spec_invc_num_anom_skip_invc_num \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_pk,
              field_setting=self.anomaly_skip_invoice_numbers,
              machine_name='fld_spec_invc_num_anom_skip_invc_num',
              field_setting_order=1,
            )
        self.fld_spec_invc_num_anom_skip_invc_num.save()

        # Link missing data anomaly to invoice number field spec.
        self.fld_spec_invc_num_anomaly_missing \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_pk,
              field_setting=self.anomaly_missing,
              machine_name='fld_spec_invc_num_anomaly_missing',
              field_setting_order=2,
            )
        self.fld_spec_invc_num_anomaly_missing.save()

        # Link duplicate values anomaly to invoice number field spec.
        self.fld_spec_invc_num_anomaly_duplicate_values \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_pk,
              field_setting=self.anomaly_duplicate_values,
              machine_name='fld_spec_invc_num_anomaly_duplicate_values',
              field_setting_order=3,
            )
        self.fld_spec_invc_num_anomaly_duplicate_values.save()

        # Link Benford's law anomaly to invoice number field spec.
        self.fld_spec_invc_num_anomaly_violates_benfords_law \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_pk,
              field_setting=self.anomaly_violates_benfords_law,
              machine_name='fld_spec_invc_num_anomaly_violates_benfords_law',
              field_setting_order=4,
            )
        self.fld_spec_invc_num_anomaly_violates_benfords_law.save()

        # Link out of range anomaly to invoice date field.
        self.fld_spec_invoice_date_anomaly_out_of_range \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_date,
              field_setting=self.anomaly_out_of_range,
              machine_name='fld_spec_invoice_date_anomaly_out_of_range',
              field_setting_order=1,
              field_setting_params={
              }
            )
        self.fld_spec_invoice_date_anomaly_out_of_range.save()

        # # Setting - invoices/due dates on nonwork days.
        # self.setting_nonwork_days = FieldSettingDb(
        #     title='Overridden.',
        #     machine_name='setting_nonwork_days',
        #     description='Overridden',
        #     setting_group=FEDS_BASIC_SETTING_GROUP,
        #     setting_type=FEDS_BOOLEAN_SETTING,
        #     # Default for new project is false.
        #     setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        # )
        # self.setting_nonwork_days.save()
        # # Link to invoice date field.
        # self.fld_spec_invoice_date_setting_nonwork_days \
        #     = AvailableFieldSpecSettingDb(
        #       field_spec=self.invoice_date,
        #       field_setting=self.setting_nonwork_days,
        #       machine_name='fld_spec_invoice_date_setting_nonwork_days',
        #       field_setting_order=2,
        #       field_setting_params={
        #         'title': 'Invoices with non-workday dates.',
        #         'description': 'Some invoices will have dates on the weekend.',
        #       }
        #     )
        # self.fld_spec_invoice_date_setting_nonwork_days.save()
        # # Link to due date field.
        # self.fld_spec_invoice_due_date_setting_nonwork_days \
        #     = AvailableFieldSpecSettingDb(
        #       field_spec=self.invoice_due_date,
        #       field_setting=self.setting_nonwork_days,
        #       machine_name='fld_spec_invoice_due_date_setting_nonwork_days',
        #       field_setting_order=1,
        #       field_setting_params={
        #         'title': 'Invoice due dates with non-workday dates.',
        #         'description': 'Some invoice due dates will have due dates '
        #                        'on the weekend.',
        #       }
        #     )
        # self.fld_spec_invoice_due_date_setting_nonwork_days.save()

        # Make anomalies - invoices/due dates on nonwork days.
        self.anomaly_nonwork_days = FieldSettingDb(
            title='Overridden.',
            machine_name='anomaly_nonwork_days',
            description='Overridden',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_nonwork_days.save()
        # Link to invoice date field.
        self.fld_spec_invoice_date_anomaly_nonwork_days \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_date,
              field_setting=self.anomaly_nonwork_days,
              machine_name='fld_spec_invoice_date_anomaly_nonwork_days',
              field_setting_order=2,
              field_setting_params={
                'title': 'Invoices with non-workday dates.',
                'description': '''Some invoices will have dates on the weekend.
                     This is only an anomaly when normal invoice dates are 
                     restricted to workdays.''',
              }
            )
        self.fld_spec_invoice_date_anomaly_nonwork_days.save()
        # Link to due date field.
        self.fld_spec_invoice_due_date_anomaly_nonwork_days \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_due_date,
              field_setting=self.anomaly_nonwork_days,
              machine_name='fld_spec_invoice_due_date_anomaly_nonwork_days',
              field_setting_order=2,
              field_setting_params={
                'title': 'Invoice due dates with non-workday dates.',
                'description': '''Some invoices due dates will have dates 
                        on the weekend. This is only an anomaly when 
                        normal invoice due dates are restricted to workdays.''',
              }
            )
        self.fld_spec_invoice_due_date_anomaly_nonwork_days.save()

        # Statistical distribution type.
        self.setting_stat_distribution = FieldSettingDb(
            title='Statistical distribution',
            machine_name='setting_stat_distribution',
            description='Statistical distribution of data.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            # Set default.
            setting_params={
                FEDS_CHOICES_PARAM: FEDS_STAT_DISTRIBUTION_CHOCIES,
                FEDS_VALUE_PARAM: FEDS_NORMAL_DISTRIBUTION,
            }
        )
        self.setting_stat_distribution.save()
        # Link to total cost before tax field.
        self.fld_spec_invc_tot_bt_setting_stat_distrib \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_total_before_tax,
              field_setting=self.setting_stat_distribution,
              machine_name='fld_spec_invc_tot_bt_setting_stat_distrib',
              field_setting_order=1,
              field_setting_params={
                'title': 'Statistical distribution.',
                'description': 'Statistical distribution of invoice '
                               'total before tax.',
              }
            )
        self.fld_spec_invc_tot_bt_setting_stat_distrib.save()

        # Normal distribution mean.
        self.setting_normal_distribution_mean = FieldSettingDb(
            title='Normal distribution mean',
            machine_name='setting_normal_distribution_mean',
            description='Mean for normal distribution.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CURRENCY_SETTING,
            # Set default.
            setting_params={
                FEDS_VALUE_PARAM:
                    FEDS_NORMAL_DISTRIBUTION_MEAN_TOTAL_BEFORE_TAX_DEFAULT,
                # Setting visible when machine name when equals value given.
                FEDS_VISIBILITY_TEST_PARAM: {
                    FEDS_MACHINE_NAME_PARAM: 'fld_spec_invc_tot_bt_setting_stat_distrib',
                    FEDS_DETERMINING_VALUE_PARAM: FEDS_NORMAL_DISTRIBUTION,
                },
            }
        )
        self.setting_normal_distribution_mean.save()
        # Link to total invoice cost before tax.
        self.fld_spec_invc_tot_bt_setting_norm_distrib_mean \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_total_before_tax,
              field_setting=self.setting_normal_distribution_mean,
              machine_name='fld_spec_invc_tot_bt_setting_norm_distrib_mean',
              field_setting_order=2,
              field_setting_params={
                                   'title': 'Mean',
                                   'description': 'Mean of normal distribution '
                                                  'for total before tax.',
                                   }
              )
        self.fld_spec_invc_tot_bt_setting_norm_distrib_mean.save()

        # Link arithmetic error to total invoice cost before tax.
        self.fld_spec_invc_tot_bt_anomaly_arithmetic_errors \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_total_before_tax,
              field_setting=self.anomaly_arithmetic_errors,
              machine_name='fld_spec_invc_tot_bt_anomaly_arithmetic_errors',
              field_setting_order=3,
              field_setting_params={}
            )
        self.fld_spec_invc_tot_bt_setting_norm_distrib_mean.save()

        # Link negative numbers to total invoice cost before tax.
        self.fld_spec_invc_tot_bt_anomaly_negative_numbers \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_total_before_tax,
              field_setting=self.anomaly_negative_numbers,
              machine_name='fld_spec_invc_tot_bt_anomaly_negative_numbers',
              field_setting_order=4,
              field_setting_params={}
            )
        self.fld_spec_invc_tot_bt_anomaly_negative_numbers.save()

        # Link arithmetic error to sales tax.
        self.fld_spec_invc_sales_tax_anomaly_arithmetic_errors \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_sales_tax,
              field_setting=self.anomaly_arithmetic_errors,
              machine_name='fld_spec_invc_sales_tax_anomaly_arithmetic_errors',
              field_setting_order=1,
              field_setting_params={}
            )
        self.fld_spec_invc_sales_tax_anomaly_arithmetic_errors.save()

        # Link negative numbers to sales tax.
        self.fld_spec_invc_sales_tax_anomaly_negative_numbers \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_sales_tax,
              field_setting=self.anomaly_negative_numbers,
              machine_name='fld_spec_invc_sales_tax_anomaly_negative_numbers',
              field_setting_order=2,
              field_setting_params={}
            )
        self.fld_spec_invc_sales_tax_anomaly_negative_numbers.save()

        # Link arithmetic error to invoice total.
        self.fld_spec_invc_total_anomaly_arithmetic_errors \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_total,
              field_setting=self.anomaly_arithmetic_errors,
              machine_name='fld_spec_invc_total_anomaly_arithmetic_errors',
              field_setting_order=1,
              field_setting_params={}
            )
        self.fld_spec_invc_total_anomaly_arithmetic_errors.save()

        # Link negative numbers to invoice total.
        self.fld_spec_invc_total_anomaly_negative_numbers \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_total,
              field_setting=self.anomaly_negative_numbers,
              machine_name='fld_spec_invc_total_anomaly_negative_numbers',
              field_setting_order=1,
              field_setting_params={}
            )
        self.fld_spec_invc_total_anomaly_negative_numbers.save()

    def make_table_settings_invoice(self):

        # Number of invoices per customer options.
        self.setting_num_invc_per_cust_options = FieldSettingDb(
            title='Number of invoices per customer options',
            machine_name='setting_num_invc_per_cust_options',
            description='How the number of invoices per customer '
                        'is determined.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            # Set default.
            setting_params={
                FEDS_CHOICES_PARAM: FEDS_NUM_INVOICES_PER_CUST_OPTIONS,
                FEDS_VALUE_PARAM: FEDS_NUM_INVOICES_PER_CUST_STANDARD,
            }
        )
        self.setting_num_invc_per_cust_options.save()
        # Link setting to invoices table.
        self.tbl_customer_setting_num_invc_per_cust_options \
            = AvailableNotionalTableSettingDb(
              table=self.tbl_invoice,
              table_setting=self.setting_num_invc_per_cust_options,
              machine_name='tbl_customer_setting_num_invc_per_cust_options',
              table_setting_order=1,
            )
        self.tbl_customer_setting_num_invc_per_cust_options.save()

        # Custom number of invoices per customer.
        self.setting_cust_num_invc_per_cust = FieldSettingDb(
            title='Average number of invoices per customer',
            machine_name='setting_cust_num_invc_per_cust',
            description='Average number of invoices '
                        'that will be generated per customer.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_INTEGER_SETTING,
            setting_params={
                           FEDS_VALUE_PARAM:
                               FEDS_CUST_INVOICES_PER_CUST_DEFAULT,
                           FEDS_MIN_PARAM: FEDS_MIN_CUST_INVOICES_PER_CUST,
                           FEDS_MAX_PARAM: FEDS_MAX_CUST_INVOICES_PER_CUST,
                           # Setting visible when machine name given
                           # equals value given.
                           FEDS_VISIBILITY_TEST_PARAM: {
                               FEDS_MACHINE_NAME_PARAM:
                                   'tbl_customer_setting_num_invc_per_cust_options',
                               FEDS_DETERMINING_VALUE_PARAM:
                                   FEDS_NUM_INVOICES_PER_CUST_CUSTOM,
                           },
                           }
        )
        self.setting_cust_num_invc_per_cust.save()
        # Link setting to invoice table.
        self.tbl_customer_setting_cust_num_invc_per_cust \
            = AvailableNotionalTableSettingDb(
              table=self.tbl_invoice,
              table_setting=self.setting_cust_num_invc_per_cust,
              machine_name='tbl_customer_setting_cust_num_invc_per_cust',
              table_setting_order=2,
            )
        self.tbl_customer_setting_cust_num_invc_per_cust.save()

    def make_table_settings_product(self):
        # Number of products options.
        self.setting_num_product_options = FieldSettingDb(
            title='Number of products options',
            machine_name='setting_num_product_options',
            description='How the number of products is determined.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_CHOICE_SETTING,
            # Set default.
            setting_params={
                           FEDS_CHOICES_PARAM: FEDS_NUM_PRODUCTS_STANDARD,
                           FEDS_VALUE_PARAM: FEDS_NUM_PRODUCTS_STANDARD,
                           }
        )
        self.setting_num_product_options.save()
        # Link setting to product table.
        self.tbl_products_setting_num_product_options \
            = AvailableNotionalTableSettingDb(
              table=self.tbl_product,
              table_setting=self.setting_num_product_options,
              machine_name='tbl_products_setting_num_product_options',
              table_setting_order=1,
            )
        self.tbl_products_setting_num_product_options.save()

        # Custom number of products.
        self.setting_cust_num_products = FieldSettingDb(
            title='Number of products',
            machine_name='setting_cust_num_products',
            description='Number of products that will be generated.',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_INTEGER_SETTING,
            # Set default.
            setting_params={
                           FEDS_VALUE_PARAM: FEDS_NUM_PRODUCTS_CUSTOM_DEFAULT,
                           FEDS_MIN_PARAM: FEDS_MIN_PRODUCTS,
                           FEDS_MAX_PARAM: FEDS_MAX_PRODUCTS,
                           # Setting visible when machine name when
                           # equals value given.
                           FEDS_VISIBILITY_TEST_PARAM: {
                               FEDS_MACHINE_NAME_PARAM: 'tbl_products_setting_num_product_options',
                               FEDS_DETERMINING_VALUE_PARAM: FEDS_NUM_PRODUCTS_CUSTOM,
                           },

            }
        )
        self.setting_cust_num_products.save()
        # Link setting to product table.
        self.tbl_product_setting_cust_num_custs \
            = AvailableNotionalTableSettingDb(
              table=self.tbl_product,
              table_setting=self.setting_cust_num_products,
              machine_name='tbl_product_setting_cust_num_custs',
              table_setting_order=2,
            )
        self.tbl_product_setting_cust_num_custs.save()

    def make_field_settings_invoice_deets(self):
        # Settings for the fields in the invoice details table.

        # Link arithmetic error to subtotal.
        self.fld_spec_invc_deets_subtotal_anomaly_arithmetic_errors \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_detail_subtotal_product,
              field_setting=self.anomaly_arithmetic_errors,
              machine_name='fld_spec_invc_deets_subtotal_anomaly_arithmetic_errors',
              field_setting_order=1,
              field_setting_params={}
            )
        self.fld_spec_invc_deets_subtotal_anomaly_arithmetic_errors.save()

        # Link negative numbers to subtotal.
        self.fld_spec_invc_deets_subtotal_anomaly_negative_numbers \
            = AvailableFieldSpecSettingDb(
              field_spec=self.invoice_detail_subtotal_product,
              field_setting=self.anomaly_negative_numbers,
              machine_name='fld_spec_invc_deets_subtotal_anomaly_negative_numbers',
              field_setting_order=2,
              field_setting_params={}
            )
        self.fld_spec_invc_deets_subtotal_anomaly_negative_numbers.save()
