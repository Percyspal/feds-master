import os
import csv
import time
import random
from feds.settings import FEDS_NUM_CUSTOMERS_STANDARD, \
    FEDS_NUM_CUSTOMERS_STANDARD_LOW, FEDS_NUM_CUSTOMERS_STANDARD_HIGH, \
    FEDS_VALUE_PARAM, FEDS_NUM_CUSTOMERS_CUSTOM
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

    def create_customer_table(self):
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

    def add_customers(self):
        pass

    def erase_table(self, table_name):
        sql = 'DROP TABLE {table};'.format(table=table_name)
        self.run_sql(sql)

    def run_sql(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql, [])

    def get_num_customers_to_make(self):
        option_setting_name = 'tbl_customer_setting_num_cust_options'
        custom_option_name = 'tbl_customer_setting_cust_num_custs'
        if option_setting_name not in FedsSetting.setting_machine_names:
            message = '"{setting}" not in FedsSetting.setting_machine_names'
            raise LookupError(message.format(setting=option_setting_name))
        chosen_option = FedsSetting.setting_machine_names[
            option_setting_name].params[FEDS_VALUE_PARAM]
        if chosen_option == FEDS_NUM_CUSTOMERS_STANDARD:
            num_custs = random.randint(
                FEDS_NUM_CUSTOMERS_STANDARD_LOW,
                FEDS_NUM_CUSTOMERS_STANDARD_HIGH
            )
        elif chosen_option == FEDS_NUM_CUSTOMERS_CUSTOM:
            num_custs = \
                FedsSetting.setting_machine_names[custom_option_name].params[
                    FEDS_VALUE_PARAM]
        else:
            message = 'Bad value "{v}" for setting {s}'
            raise ValueError(
                message.format(v=chosen_option, s=option_setting_name)
            )
        return num_custs

    def create_customers(self):
        self.num_custs = self.get_num_customers_to_make()
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
        for cust_id in range(1, self.num_custs + 1):
            if cust_id == 1:
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
            record += str(cust_id) + ",'" + cust_name + "','" \
                      + cust_address + "','" + cust_zip + "','" \
                      + cust_phone + "','" + cust_email + "')"
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

    def save_customer_data(self, export_dir_path, file_name):
        sql = 'select * from customer{id} order by CustomerId'.format(
            id=self.project_id)
        with connection.cursor() as cursor:
            cursor.execute(sql, [])
            rows = cursor.fetchall()
        file_path = os.path.join(export_dir_path, file_name)
        with open(file_path, 'w') as csvfile:
            customer_writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                                         quoting=csv.QUOTE_NONNUMERIC)
            for customer in rows:
                customer_writer.writerow(customer)

    def save_proj_spec_file(self, visible_settings,
                            export_dir_path, file_name):
        # Compute user label to show.
        owner = self.project.owner
        user_label = owner.username
        full_name = owner.first_name + ' ' + owner.last_name
        if full_name.strip() != '':
            user_label += ' (' + full_name + ')'
        project_settings = list()
        for setting in self.project.settings:
            if setting.machine_name in visible_settings:
                project_settings.append({
                    'title': setting.title,
                    'setting': visible_settings[setting.machine_name]
                })
        context = {
            'project': self.project,
            'user_label': user_label,
            'project_settings': project_settings,
        }

        content = render_to_string('generate/project_spec.html', context)
        file_path = os.path.join(export_dir_path, file_name)
        with open(file_path, 'w+') as proj_spec_file:
            proj_spec_file.write(content)
