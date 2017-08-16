from django.contrib.auth.models import User
from .secrets import secret_superuser_deets, secret_users, secret_pages
from accounts.models import Profile
from sitepages.models import SitePage
from businessareas.models import BusinessArea, NotionalTable
from fieldspecs.models import FieldSpec, NotionalTableMembership
from fieldspecs.models import FieldSetting, AvailableFieldSetting
from feds.settings import FEDS_DATE_RANGE_SETTING, FEDS_BOOLEAN_SETTING, \
    FEDS_BASIC_SETTING_GROUP, FEDS_ANOMALY_GROUP, FEDS_BOOLEAN_VALUE_PARAM, \
    FEDS_BOOLEAN_VALUE_TRUE, FEDS_BOOLEAN_VALUE_FALSE


# noinspection PyAttributeOutsideInit,PyMethodMayBeStatic
class DbInitializer:
    """ Initialize the database with starting data. """

    def init_database(self):
        self.make_superuser()
        # Make other users.
        self.make_regular_users()
        # Make some pages.
        self.make_pages()
        self.make_business_area()
        self.make_notional_tables()
        self.make_customer_fields()
        self.make_invoice_fields()
        self.make_invoice_detail_fields()
        self.make_product_fields()
        self.erase_field_settings()
        self.make_field_settings_customer()
        self.make_field_settings_invoice()

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
        BusinessArea.objects.all().delete()
        self.business_area = BusinessArea(
            title='Revenue',
            description='Sell products customers.',
            # default_params={"sales_tax_rate": "0.06"}
        )
        self.business_area.save()

    def make_notional_tables(self):
        NotionalTable.objects.all().delete()
        self.customer_table = NotionalTable(
            business_area=self.business_area,
            title='Customer',
            description='Customers buying products.'
        )
        self.customer_table.save()

        self.invoice_table = NotionalTable(
            business_area=self.business_area,
            title='Invoice',
            description='Invoices sent to customers.'
        )
        self.invoice_table.save()

        self.invoice_detail_table = NotionalTable(
            business_area=self.business_area,
            title='InvoiceDetail',
            description='Lines on invoices.'
        )
        self.invoice_detail_table.save()

        self.product_table = NotionalTable(
            business_area=self.business_area,
            title='Product',
            description='Products purchased by customers'
        )
        self.product_table.save()

    def make_customer_fields(self):
        # Clear existing FieldSpecs for the customer table, and their table
        # membership records.
        FieldSpec.objects.filter(notional_tables=self.customer_table).delete()
        NotionalTableMembership.objects \
            .filter(notional_table=self.customer_table).delete()

        # Make field for customer PK.
        self.customer_pk = FieldSpec(
            title='CustomerId',
            description='Primary key of customer table.',
            field_type='pk',
            # field_spec_params=''
        )
        self.customer_pk.save()
        # Record that customer PK is in the customer table.
        self.customer_pk_table_membership = NotionalTableMembership(
            field_spec=self.customer_pk,
            notional_table=self.customer_table,
            field_order=1
        )
        self.customer_pk_table_membership.save()

        # Make a FieldSpec for the customer name.
        self.customer_name = FieldSpec(
            title='CName',
            description='Name of the customer',
            field_type='text',
            # field_spec_params='{"max_length": "50"}'
        )
        self.customer_name.save()
        # Record that customer name is in the customer table.
        self.customer_name_table_membership = NotionalTableMembership(
            field_spec=self.customer_name,
            notional_table=self.customer_table,
            field_order=2
        )
        self.customer_name_table_membership.save()

        # Make a FieldSpec for the customer address.
        self.customer_address = FieldSpec(
            title='CAddress',
            description='Customer address',
            field_type='text',
            # field_spec_params='{"max_length": "500"}'
        )
        self.customer_address.save()
        # Record that customer address is in the customer table.
        self.customer_address_table_membership = NotionalTableMembership(
            field_spec=self.customer_address,
            notional_table=self.customer_table,
            field_order=3
        )
        self.customer_address_table_membership.save()

        # Make a FieldSpec for the customer zip code.
        self.customer_zip = FieldSpec(
            title='CZipCode',
            description='Zip code',
            field_type='text',
            # field_spec_params='{"length": "5"}'
        )
        self.customer_zip.save()
        # Record that customer zip is in the customer table.
        self.customer_zip_table_membership = NotionalTableMembership(
            field_spec=self.customer_zip,
            notional_table=self.customer_table,
            field_order=4
        )
        self.customer_zip_table_membership.save()

        # Make a FieldSpec for the customer phone number.
        self.customer_phone = FieldSpec(
            title='CPhone',
            description='Customer phone number',
            field_type='text',
            # field_spec_params='{"max-length": "20"}'
        )
        self.customer_phone.save()
        # Record that customer phone is in the customer table.
        self.customer_phone_table_membership = NotionalTableMembership(
            field_spec=self.customer_phone,
            notional_table=self.customer_table,
            field_order=5
        )
        self.customer_phone_table_membership.save()

        # Make a FieldSpec for the customer email.
        self.customer_email = FieldSpec(
            title='CEmail',
            description='Email address',
            field_type='email',
            # field_spec_params=''
        )
        self.customer_email.save()
        # Record that customer email is in the customer table.
        self.customer_email_table_membership = NotionalTableMembership(
            field_spec=self.customer_email,
            notional_table=self.customer_table,
            field_order=6
        )
        self.customer_email_table_membership.save()

    def make_invoice_fields(self):
        # Clear existing FieldSpecs for the customer table, and their table
        # membership records.
        FieldSpec.objects.filter(notional_tables=self.invoice_table).delete()
        NotionalTableMembership.objects \
            .filter(notional_table=self.invoice_table).delete()

        # Make a FieldSpec for the invoice id.
        self.invoice_pk = FieldSpec(
            title='InvoiceNumber',
            description='Invoice number, primary key',
            field_type='pk',
            # field_spec_params=''
        )
        self.invoice_pk.save()
        # Record that invoice pk is in the invoice table.
        self.invoice_pk_table_membership = NotionalTableMembership(
            field_spec=self.invoice_pk,
            notional_table=self.invoice_table,
            field_order=1
        )
        self.invoice_pk_table_membership.save()

        # Make a FieldSpec for the invoice's customer FK.
        self.invoice_customer_id = FieldSpec(
            title='CustomerId',
            description='Foreign key into customer',
            field_type='fk',
            # field_spec_params=''
        )
        self.invoice_customer_id.save()
        # Record that invoice customer id is in the invoice table.
        self.invoice_customer_id_table_membership = NotionalTableMembership(
            field_spec=self.invoice_customer_id,
            notional_table=self.invoice_table,
            field_order=2
        )
        self.invoice_customer_id_table_membership.save()

        # Make a FieldSpec for the invoice date.
        self.invoice_date = FieldSpec(
            title='InvoiceDate',
            description='Invoice date',
            field_type='date',
            # field_spec_params=''
        )
        self.invoice_date.save()
        # Record that invoice date is in the invoice table.
        self.invoice_date_table_membership = NotionalTableMembership(
            field_spec=self.invoice_date,
            notional_table=self.invoice_table,
            field_order=3
        )
        self.invoice_date_table_membership.save()

        # Make a FieldSpec for the invoice's payment type.
        self.invoice_payment_type = FieldSpec(
            title='PaymentType',
            description='Payment type',
            field_type='text',
            # field_spec_params=''
        )
        self.invoice_payment_type.save()
        # Record that invoice payment_type is in the invoice table.
        self.invoice_payment_type_table_membership = NotionalTableMembership(
            field_spec=self.invoice_payment_type,
            notional_table=self.invoice_table,
            field_order=4
        )
        self.invoice_payment_type_table_membership.save()

        # Make a FieldSpec for the invoice's credit terms.
        self.invoice_credit_terms = FieldSpec(
            title='CreditTerms',
            description='Credit terms',
            field_type='text',
            # field_spec_params=''
        )
        self.invoice_credit_terms.save()
        # Record that invoice credit terms is in the invoice table.
        self.invoice_credit_terms_table_membership = NotionalTableMembership(
            field_spec=self.invoice_credit_terms,
            notional_table=self.invoice_table,
            field_order=5
        )
        self.invoice_credit_terms_table_membership.save()

        # Make a FieldSpec for the invoice's due date
        self.invoice_due_date = FieldSpec(
            title='DueDate',
            description='Date payment is due',
            field_type='date',
            # field_spec_params=''
        )
        self.invoice_due_date.save()
        # Record that invoice due_date is in the invoice table.
        self.invoice_due_date_table_membership = NotionalTableMembership(
            field_spec=self.invoice_due_date,
            notional_table=self.invoice_table,
            field_order=6
        )
        self.invoice_due_date_table_membership.save()

        # Make a FieldSpec for the invoice's shipping method.
        self.invoice_shipping_method = FieldSpec(
            title='ShippingMethod',
            description='Shipping method',
            field_type='text',
            # field_spec_params=''
        )
        self.invoice_shipping_method.save()
        # Record that invoice shipping method is in the invoice table.
        self.invoice_shipping_method_table_membership = NotionalTableMembership(
            field_spec=self.invoice_shipping_method,
            notional_table=self.invoice_table,
            field_order=7
        )
        self.invoice_shipping_method_table_membership.save()

        # Make a FieldSpec for the invoice's shipping terms.
        self.invoice_shipping_terms = FieldSpec(
            title='ShippingTerms',
            description='Shipping terms',
            field_type='text',
            # field_spec_params=''
        )
        self.invoice_shipping_terms.save()
        # Record that invoice shipping terms is in the invoice table.
        self.invoice_shipping_terms_table_membership = NotionalTableMembership(
            field_spec=self.invoice_shipping_terms,
            notional_table=self.invoice_table,
            field_order=8
        )
        self.invoice_shipping_terms_table_membership.save()

        # Make a FieldSpec for the invoice total before tax.
        self.invoice_total_before_tax = FieldSpec(
            title='TotalBTax',
            description='Total before tax',
            field_type='currency',
            # field_spec_params=''
        )
        self.invoice_total_before_tax.save()
        # Record that invoice total before tax is in the invoice table.
        self.invoice_total_before_tax_table_membership \
            = NotionalTableMembership(
                field_spec=self.invoice_total_before_tax,
                notional_table=self.invoice_table,
                field_order=9
            )
        self.invoice_total_before_tax_table_membership.save()

        # Make a FieldSpec for the invoice sales tax.
        self.invoice_sales_tax = FieldSpec(
            title='SalesTax',
            description='Sales tax',
            field_type='currency',
            # field_spec_params=''
        )
        self.invoice_sales_tax.save()
        # Record that invoice sales tax is in the invoice table.
        self.invoice_sales_tax_table_membership = NotionalTableMembership(
            field_spec=self.invoice_sales_tax,
            notional_table=self.invoice_table,
            field_order=10
        )
        self.invoice_sales_tax_table_membership.save()

        # Make a FieldSpec for the invoice total.
        self.invoice_total = FieldSpec(
            title='Total',
            description='Invoice total',
            field_type='currency',
            # field_spec_params=''
        )
        self.invoice_total.save()
        # Record that invoice total is in the invoice table.
        self.invoice_total_table_membership = NotionalTableMembership(
            field_spec=self.invoice_total,
            notional_table=self.invoice_table,
            field_order=11
        )
        self.invoice_total_table_membership.save()

    def make_invoice_detail_fields(self):
        # Clear existing FieldSpecs for the invoice detail table, and their
        # table membership records.
        FieldSpec.objects.filter(notional_tables=self.invoice_detail_table) \
            .delete()
        NotionalTableMembership.objects \
            .filter(notional_table=self.invoice_detail_table).delete()

        # Make a FieldSpec for the invoice detail .
        self.invoice_detail_pk = FieldSpec(
            title='InvDetailNumber',
            description='Invoice detail number (primary key)',
            field_type='pk',
            # field_spec_params=''
        )
        self.invoice_detail_pk.save()
        # Record that invoice details PK is in the invoice details table.
        self.invoice_detail_pk_table_membership = NotionalTableMembership(
            field_spec=self.invoice_detail_pk,
            notional_table=self.invoice_detail_table,
            field_order=1
        )
        self.invoice_detail_pk_table_membership.save()

        # Make a FieldSpec for the invoice detail invoice number.
        self.invoice_detail_invoice_number = FieldSpec(
            title='InvoiceNumber',
            description='Invoice number, foreign key',
            field_type='fk',
            # field_spec_params=''
        )
        self.invoice_detail_invoice_number.save()
        # Record that invoice details invoice number is in the invoice
        # details table.
        self.invoice_detail_invoice_number_table_membership \
            = NotionalTableMembership(
                field_spec=self.invoice_detail_invoice_number,
                notional_table=self.invoice_detail_table,
                field_order=2
            )
        self.invoice_detail_invoice_number_table_membership.save()

        # Make a FieldSpec for the invoice detail product id.
        self.invoice_detail_product_id = FieldSpec(
            title='ProductId',
            description='Product id, foreign key',
            field_type='fk',
            # field_spec_params=''
        )
        self.invoice_detail_product_id.save()
        # Record that invoice details product id is in the invoice details
        # table.
        self.invoice_detail_product_id_table_membership \
            = NotionalTableMembership(
                field_spec=self.invoice_detail_product_id,
                notional_table=self.invoice_detail_table,
                field_order=3
            )
        self.invoice_detail_product_id_table_membership.save()

        # Make a FieldSpec for the invoice detail quantity.
        self.invoice_detail_quantity = FieldSpec(
            title='Quantity',
            description='Product quantity',
            field_type='int',
            # field_spec_params=''
        )
        self.invoice_detail_quantity.save()
        # Record that invoice details quantity is in the invoice details table.
        self.invoice_detail_quantity_table_membership \
            = NotionalTableMembership(
                field_spec=self.invoice_detail_quantity,
                notional_table=self.invoice_detail_table,
                field_order=4
            )
        self.invoice_detail_quantity_table_membership.save()

        # Make a FieldSpec for the invoice detail product subtotal.
        self.invoice_detail_subtotal_product = FieldSpec(
            title='SubtotalProduct',
            description='Subtotal for product',
            field_type='currency',
            # field_spec_params=''
        )
        self.invoice_detail_subtotal_product.save()
        # Record that invoice details subtotal product is in the invoice
        # details table.
        self.invoice_detail_subtotal_product_table_membership \
            = NotionalTableMembership(
                field_spec=self.invoice_detail_subtotal_product,
                notional_table=self.invoice_detail_table,
                field_order=5
            )
        self.invoice_detail_subtotal_product_table_membership.save()

    def make_product_fields(self):
        # Clear existing FieldSpecs for the product table, and their table
        # membership records.
        FieldSpec.objects.filter(notional_tables=self.product_table).delete()
        NotionalTableMembership.objects.filter(
            notional_table=self.product_table).delete()

        # Make a FieldSpec for the product PK.
        self.product_pk = FieldSpec(
            title='ProductId',
            description='Product id, primary key',
            field_type='pk',
            # field_spec_params=''
        )
        self.product_pk.save()
        # Record that product pk is in the product table.
        self.product_pk_table_membership = NotionalTableMembership(
            field_spec=self.product_pk,
            notional_table=self.product_table,
            field_order=1
        )
        self.product_pk_table_membership.save()

        # Make a FieldSpec for the product description.
        self.product_description = FieldSpec(
            title='Description',
            description='Product description',
            field_type='text',
            # field_spec_params='{ "max_length": "500" }'
        )
        self.product_description.save()
        # Record that product description is in the product table.
        self.product_description_table_membership = NotionalTableMembership(
            field_spec=self.product_description,
            notional_table=self.product_table,
            field_order=2
        )
        self.product_description_table_membership.save()

        # Make a FieldSpec for the product price.
        self.product_price = FieldSpec(
            title='ProdPrice',
            description='Product price',
            field_type='currency',
            # field_spec_params=''
        )
        self.product_price.save()
        # Record that product price is in the product table.
        self.product_price_table_membership = NotionalTableMembership(
            field_spec=self.product_price,
            notional_table=self.product_table,
            field_order=3
        )
        self.product_price_table_membership.save()

    def erase_field_settings(self):
        FieldSetting.objects.all().delete()
        AvailableFieldSetting.objects.all().delete()

    def make_field_settings_customer(self):
        pass
        # Make a setting for min and max customer name length.
        # self.customer_name_length = FieldSetting(
        #     title='Customer name length',
        #     description="Minimum and maximum number of characters in the "
        #                 "customer's name.",
        #     setting_type=FEDS_BASIC_SETTING,
        #     setting_params={
        #         # Min and max that the name min length can be.
        #         'min_length': {'min': 20, 'max': 100},
        #         # Min and max that the name max length can be.
        #         'max_length': {'min': 20, 'max': 100},
        #     }
        # )
        # self.customer_name_length.save()
        # # Link setting to customer name field.
        # self.customer_name_length_field_specs = AvailableFieldSetting(
        #     field_spec=self.customer_name,
        #     field_setting=self.customer_name_length,
        #     field_setting_order=1,
        #     field_setting_params={}
        # )
        # self.customer_name_length_field_specs.save()

    def make_field_settings_invoice(self):
        # Make anomaly - skip some invoice numbers.
        self.anomaly_skip_invoice_numbers = FieldSetting(
            title='Skip some invoice numbers',
            description='There will be gaps in the invoice number sequence.',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_BOOLEAN_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_skip_invoice_numbers.save()
        # Link anomaly to invoice number field spec.
        self.anomaly_skip_invoice_numbers_to_field_specs\
            = AvailableFieldSetting(
                field_spec=self.invoice_pk,
                field_setting=self.anomaly_skip_invoice_numbers,
                field_setting_order=1,
                field_setting_params={}
            )
        self.anomaly_skip_invoice_numbers_to_field_specs.save()

        # Make setting for invoice and due date ranges
        self.invoice_date_range = FieldSetting(
            title='Overridden',
            description='Overridden',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_DATE_RANGE_SETTING,
            setting_params={
                'start_date_min': '1/1/2000',
                'end_date_min': '2/1/2000',
            }
        )
        self.invoice_date_range.save()
        # Link to invoice date field.
        self.invoice_date_range_field_specs = AvailableFieldSetting(
            field_spec=self.invoice_date,
            field_setting=self.invoice_date_range,
            field_setting_order=1,
            field_setting_params={
                'title': 'Invoice date range',
                'description': 'Range for invoice dates',
            }
        )
        self.invoice_date_range_field_specs.save()
        # Link to due date field.
        self.invoice_due_date_range_field_specs = AvailableFieldSetting(
            field_spec=self.invoice_due_date,
            field_setting=self.invoice_date_range,
            field_setting_order=1,
            field_setting_params={
                'title': 'Due date range',
                'description': 'Range for due dates',
            }
        )
        self.invoice_due_date_range_field_specs.save()

        # Setting - invoices/due dates on nonwork days.
        self.setting_nonwork_days = FieldSetting(
            title='Overridden.',
            description='Overridden',
            setting_group=FEDS_BASIC_SETTING_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_BOOLEAN_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.setting_nonwork_days.save()
        # Link to invoice date field.
        self.setting_invoice_nonwork_days_to_field_specs\
            = AvailableFieldSetting(
                field_spec=self.invoice_date,
                field_setting=self.setting_nonwork_days,
                field_setting_order=2,
                field_setting_params={
                    'title': 'Invoices with non-workday dates.',
                    'description':
                        'Some invoices will have dates on the weekend.',
                }
            )
        self.setting_invoice_nonwork_days_to_field_specs.save()
        # Link to due date field.
        self.setting_invoice_due_date_nonwork_days_to_field_specs \
            = AvailableFieldSetting(
                field_spec=self.invoice_due_date,
                field_setting=self.setting_nonwork_days,
                field_setting_order=2,
                field_setting_params={
                    'title': 'Invoice due dates with non-workday dates.',
                    'description': 'Some invoice due dates will have due dates '
                                   'on the weekend.',
                }
            )
        self.setting_invoice_nonwork_days_to_field_specs.save()

        # Make anomalies - invoices/due dates on nonwork days.
        self.anomaly_nonwork_days = FieldSetting(
            title='Overridden.',
            description='Overridden',
            setting_group=FEDS_ANOMALY_GROUP,
            setting_type=FEDS_BOOLEAN_SETTING,
            # Default for new project is false.
            setting_params={FEDS_BOOLEAN_VALUE_PARAM: FEDS_BOOLEAN_VALUE_FALSE}
        )
        self.anomaly_nonwork_days.save()
        # Link to invoice date field.
        self.anomaly_invoice_nonwork_days_to_field_specs\
            = AvailableFieldSetting(
                field_spec=self.invoice_date,
                field_setting=self.anomaly_nonwork_days,
                field_setting_order=3,
                field_setting_params={
                    'title': 'Invoices with non-workday dates.',
                    'description': '''Some invoices will have dates on the weekend.
                     This is only an anomaly when normal invoice dates are 
                     restricted to workdays.''',
                }
            )
        self.anomaly_invoice_nonwork_days_to_field_specs.save()
        # Link to due date field.
        self.anomaly_invoice_due_date_nonwork_days_to_field_specs \
            = AvailableFieldSetting(
                field_spec=self.invoice_due_date,
                field_setting=self.anomaly_nonwork_days,
                field_setting_order=3,
                field_setting_params={
                    'title': 'Invoice due dates with non-workday dates.',
                    'description': '''Some invoices due dates will have dates 
                        on the weekend. This is only an anomaly when 
                        normal invoice due dates are restricted to workdays.''',
                }
            )
        self.anomaly_invoice_due_date_nonwork_days_to_field_specs.save()
