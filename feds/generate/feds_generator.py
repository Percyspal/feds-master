import os
import csv
import time
import random
from feds.settings import FEDS_NUM_CUSTOMERS_STANDARD, \
    FEDS_NUM_CUSTOMERS_STANDARD_LOW, FEDS_NUM_CUSTOMERS_STANDARD_HIGH, \
    FEDS_VALUE_PARAM, FEDS_NUM_CUSTOMERS_CUSTOM, FEDS_NUM_PRODUCTS_STANDARD, \
    FEDS_NUM_PRODUCTS_STANDARD_LOW, FEDS_NUM_PRODUCTS_STANDARD_HIGH, \
    FEDS_MAX_PRICE, FEDS_MIN_PRICE, FEDS_NUM_PRODUCTS_CUSTOM, \
    FEDS_NUM_INVOICES_PER_CUST_STANDARD, FEDS_NUM_INVOICES_PER_CUST_CUSTOM, \
    FEDS_MIN_STANDARD_INVOICES_PER_CUST, FEDS_MAX_STANDARD_INVOICES_PER_CUST
from projects.internal_representation_classes import FedsSetting
from projects.models import ProjectDb
from projects.read_write_project import read_project
from django.db import connection
from django.shortcuts import render
from django.template.loader import render_to_string


class FedsGenerator:
    def __init__(self, project_id):
        self.project_id = project_id
        self.project_db = ProjectDb.objects.get(pk=project_id)
        self.project = read_project(project_id)
        # Number of customers to make.
        self.number_customers = 0
        # Number of products to make.
        self.number_products = 0
        # How many invoices per customer.
        self.invoices_per_customer = dict()

    def create_customer_table(self):
        # Compute the name of the customer table, unique for this project.
        self.customer_table_name \
            = 'customer{project_id}'.format(project_id=self.project_id)
        self.erase_table(self.customer_table_name)
        sql = '''
        CREATE TABLE {cust_table_name}(
          CustomerId        INT,
          CName             VARCHAR (50),
          CStreetAndNumber  VARCHAR(255),
          CZipCode          VARCHAR(7),
          CPhone            VARCHAR(10),
          CEmail            VARCHAR(50)
          );'''.format(cust_table_name=self.customer_table_name)
        self.run_sql(sql)

    def create_invoice_table(self):
        # Compute the name of the invoice table, unique for this project.
        self.invoice_table_name \
            = 'invoice{project_id}'.format(project_id=self.project_id)
        self.erase_table(self.invoice_table_name)
        sql = '''
        CREATE TABLE {invc_table_name}(
          InvoiceNumber    INT,
          CustomerId       INT,
          InvoiceDate      DATE,
          PaymentType      VARCHAR(10),
          CreditTerms      VARCHAR(20),
          DueDate          DATE,
          ShippingMethod   VARCHAR(20),
          ShippingTerms    VARCHAR(20),
          TotalBTax        NUMERIC(12,2),
          SalesTax         NUMERIC(12,2),
          Total            NUMERIC(12,2)
          );'''.format(invc_table_name=self.invoice_table_name)
        self.run_sql(sql)

    def create_invoice_deets_table(self):
        # Compute the name of the invoice deets table, unique for this project.
        self.invoice_deets_table_name \
            = 'invoicedetail{project_id}'.format(project_id=self.project_id)
        self.erase_table(self.invoice_deets_table_name)
        sql = '''
        CREATE TABLE {invc_deets_table_name}(
          InvDetailNumber   INT,
          InvoiceNumber     INT,
          ProductId         INT,
          Quantity          INT,
          SubtotalProduct   NUMERIC(12,2)
          );'''.format(invc_deets_table_name=self.invoice_deets_table_name)
        self.run_sql(sql)

    def create_product_table(self):
        # Compute the name of the product table, unique for this project.
        self.product_table_name \
            = 'product{project_id}'.format(project_id=self.project_id)
        self.erase_table(self.product_table_name)
        sql = '''
        CREATE TABLE {prod_table_name}(
          ProductId        INT,
          ProductName      VARCHAR(50),
          Description      VARCHAR(100),
          ProdPrice        NUMERIC(7,2)
          );'''.format(prod_table_name=self.product_table_name)
        self.run_sql(sql)

    def erase_table(self, table_name):
        """
        Erase a table if it exists.
        """
        sql = 'DROP TABLE IF EXISTS {table};'.format(table=table_name)
        self.run_sql(sql)

    def run_sql(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql, [])

    def get_num_customers_to_make(self):
        # Work out how many customers need need to make.
        option_setting_name = 'tbl_customer_setting_num_cust_options'
        custom_option_name = 'tbl_customer_setting_cust_num_custs'
        # Did the user choose the default: number chosen by FEDS?
        if option_setting_name not in FedsSetting.setting_machine_names:
            message = '"{setting}" not in FedsSetting.setting_machine_names'
            raise LookupError(message.format(setting=option_setting_name))
        chosen_option = FedsSetting.setting_machine_names[
            option_setting_name].params[FEDS_VALUE_PARAM]
        if chosen_option == FEDS_NUM_CUSTOMERS_STANDARD:
            # Let FEDS choose number of customers.
            num_custs = random.randint(
                FEDS_NUM_CUSTOMERS_STANDARD_LOW,
                FEDS_NUM_CUSTOMERS_STANDARD_HIGH
            )
        elif chosen_option == FEDS_NUM_CUSTOMERS_CUSTOM:
            # Get the user's value for number of customers.
            num_custs = \
                FedsSetting.setting_machine_names[custom_option_name].params[
                    FEDS_VALUE_PARAM]
        else:
            message = 'Bad value "{v}" for setting {s}'
            raise ValueError(
                message.format(v=chosen_option, s=option_setting_name)
            )
        # Int because JSON option is string.
        self.number_customers = int(num_custs)

    def get_num_products_to_make(self):
        # Work out how many products need need to make.
        option_setting_name = 'tbl_products_setting_num_product_options'
        custom_option_name = 'tbl_product_setting_cust_num_products'
        # Did the user choose the default: number chosen by FEDS?
        if option_setting_name not in FedsSetting.setting_machine_names:
            message = '"{setting}" not in FedsSetting.setting_machine_names'
            raise LookupError(message.format(setting=option_setting_name))
        chosen_option = FedsSetting.setting_machine_names[
            option_setting_name].params[FEDS_VALUE_PARAM]
        if chosen_option == FEDS_NUM_PRODUCTS_STANDARD:
            # Let FEDS choose number of customers.
            num_products = random.randint(
                FEDS_NUM_PRODUCTS_STANDARD_LOW,
                FEDS_NUM_PRODUCTS_STANDARD_HIGH
            )
        elif chosen_option == FEDS_NUM_PRODUCTS_CUSTOM:
            # Get the user's value for number of customers.
            num_products = \
                FedsSetting.setting_machine_names[custom_option_name].params[
                    FEDS_VALUE_PARAM]
        else:
            message = 'Bad value "{v}" for setting {s}'
            raise ValueError(
                message.format(v=chosen_option, s=option_setting_name)
            )
        # Int because JSON option is string.
        self.number_products = int(num_products)

    def create_customers(self):
            self.get_num_customers_to_make()
            # Load name options.
            first_names = self.read_names_list('first_names.txt')
            last_names = self.read_names_list('last_names.txt')
            street_names = self.read_names_list('street_names.txt')
            street_types = self.read_names_list('street_types.txt')
            town_names = self.read_names_list('town_names.txt')
            zip_codes = self.read_names_list('zip_codes.txt')
            tlds = self.read_names_list('tlds.txt')
            sql = '''
    insert into customer{project_id} (CustomerId, CName, CStreetAndNumber, 
    CZipCode, CPhone, CEmail) values '''.format(project_id=self.project_id)
            for customer_id in range(1, self.number_customers + 1):
                if customer_id == 1:
                    record = '('
                else:
                    record = ',('
                fn = random.choice(first_names)
                ln = random.choice(last_names)
                cust_name = fn + ' ' + ln
                cust_address = str(random.randint(10, 999)) + ' ' \
                               + random.choice(street_names) + ' ' \
                               + random.choice(street_types) + ', ' \
                               + random.choice(town_names)
                cust_zip = random.choice(zip_codes)
                cust_phone = str(random.randint(211, 799)) \
                             + str(random.randint(211, 799)) \
                             + str(random.randint(2111, 7999))
                cust_email = fn.lower() + '@' + ln.lower() + '.' \
                             + random.choice(tlds)
                record += str(customer_id) + ",'" + cust_name + "','" \
                          + cust_address + "','" + cust_zip + "','" \
                          + cust_phone + "','" + cust_email + "')"
                sql += record
            sql += ';'
            self.run_sql(sql)

    def create_products(self):
        self.get_num_products_to_make()
        # Load name options.
        product_adjectives = self.read_names_list('product_adjectives.txt')
        product_types = self.read_names_list('product_types.txt')
        product_descriptions = self.read_names_list('product_descriptions.txt')
        sql = '''
    insert into product{project_id} (ProductId, ProductName, Description, 
    ProdPrice) values '''.format(project_id=self.project_id)
        price_range = FEDS_MAX_PRICE - FEDS_MIN_PRICE
        for product_id in range(1, self.number_products + 1):
            if product_id == 1:
                record = '('
            else:
                record = ',('
            adj = random.choice(product_adjectives)
            typ = random.choice(product_types)
            product_name = adj.capitalize() + ' ' + typ
            description = random.choice(product_descriptions)
            price = FEDS_MIN_PRICE + random.random() * price_range
            record += str(product_id) + ",'" + product_name + "','" \
                      + description + "'," + '{0:.2f}'.format(price) + ")"
            sql += record
        sql += ';'
        self.run_sql(sql)

    def read_names_list(self, file_name):
        module_dir = os.path.dirname(__file__)  # get current directory
        result = []
        file_path = os.path.join(module_dir, 'names_lists/' + file_name)
        with open(file_path) as file:
            for line in file:
                result.append(line.strip())
        return result

    def get_num_invoices_per_customer(self):
        # Work out how many invoices per customer.
        # Make a dictionary, key is customer id.
        self.invoices_per_customer = dict()
        # What option did the user choose?
        option_setting_name = 'tbl_customer_setting_num_invc_per_cust_options'
        custom_option_name = 'tbl_customer_setting_cust_num_invc_per_cust'
        # Did the user choose the default: number chosen by FEDS?
        if option_setting_name not in FedsSetting.setting_machine_names:
            message = '"{setting}" not in FedsSetting.setting_machine_names'
            raise LookupError(message.format(setting=option_setting_name))
        chosen_option = FedsSetting.setting_machine_names[
            option_setting_name].params[FEDS_VALUE_PARAM]
        for customer_id in range(1, self.number_customers + 1):
            if chosen_option == FEDS_NUM_INVOICES_PER_CUST_STANDARD:
                # Let FEDS choose number of invoices per customer.
                self.invoices_per_customer[customer_id] = random.randint(
                    FEDS_MIN_STANDARD_INVOICES_PER_CUST,
                    FEDS_MAX_STANDARD_INVOICES_PER_CUST
                )
            elif chosen_option == FEDS_NUM_INVOICES_PER_CUST_CUSTOM:
                # Get the user's value for number of invoices per customer.
                self.invoices_per_customer[customer_id] = \
                    FedsSetting.setting_machine_names[
                        custom_option_name].params[
                        FEDS_VALUE_PARAM]
            else:
                message = 'Bad value "{v}" for setting {s}'
                raise ValueError(
                    message.format(v=chosen_option, s=option_setting_name)
                )

    def save_customer_data(self, export_dir_path, file_name):
        sql = 'select * from customer{id} order by CustomerId'.format(
            id=self.project_id)
        with connection.cursor() as cursor:
            cursor.execute(sql, [])
            rows = cursor.fetchall()
        file_path = os.path.join(export_dir_path, file_name)
        with open(file_path, 'w') as csv_file:
            customer_writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                                         quoting=csv.QUOTE_NONNUMERIC)
            for customer in rows:
                customer_writer.writerow(customer)

    def save_product_data(self, export_dir_path, file_name):
        # Combine customer and product into one generic method?
        sql = 'select * from product{id} order by ProductId'.format(
            id=self.project_id)
        with connection.cursor() as cursor:
            cursor.execute(sql, [])
            rows = cursor.fetchall()
        file_path = os.path.join(export_dir_path, file_name)
        with open(file_path, 'w') as csv_file:
            product_writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                                         quoting=csv.QUOTE_NONNUMERIC)
            for product in rows:
                product_writer.writerow(product)

    def save_proj_spec_file(self, visible_settings,
                            export_dir_path, file_name):
        # Compute user label to show.
        owner = self.project.owner
        user_label = owner.username
        full_name = owner.first_name + ' ' + owner.last_name
        if full_name.strip() != '':
            user_label += ' (' + full_name + ')'
        # Show project settings.
        project_settings = list()
        for setting in self.project.settings:
            if setting.machine_name in visible_settings:
                project_settings.append({
                    'title': setting.title,
                    'setting': visible_settings[setting.machine_name]
                })
        tables = list()
        for table in self.project.notional_tables:
            table_data = dict()
            table_data['title'] = table.title
            table_data['description'] = table.description
            # Go through the table's settings.
            if len(table.settings) > 0:
                table_settings = list()
                for setting in table.settings:
                    # Only list visible settings. Some may be hidden, if they
                    # don't apply, since they only apply when other settings
                    # have certain values.
                    if setting.machine_name in visible_settings:
                        table_settings.append({
                            'title': setting.title,
                            'setting': visible_settings[setting.machine_name]
                        })
                table_data['settings'] = table_settings
            # Go through the fields in the table.
            table_field_specs = list()
            for field_spec in table.field_specs:
                field_spec_data = dict()
                field_spec_data['title'] = field_spec.title
                field_spec_data['description'] = field_spec.description
                if len(field_spec.settings) > 0:
                    field_spec_settings = list()
                    for setting in field_spec.settings:
                        # Only list visible settings.
                        if setting.machine_name in visible_settings:
                            field_spec_settings.append({
                                'title': setting.title,
                                'setting': visible_settings[
                                    setting.machine_name]
                            })
                    field_spec_data['settings'] = field_spec_settings
                table_field_specs.append(field_spec_data)
            table_data['field_specs'] = table_field_specs
            tables.append(table_data)
        context = {
            'project': self.project,
            'user_label': user_label,
            'project_settings': project_settings,
            'tables': tables,
        }

        content = render_to_string('generate/project_spec.html', context)
        file_path = os.path.join(export_dir_path, file_name)
        with open(file_path, 'w+') as proj_spec_file:
            proj_spec_file.write(content)
