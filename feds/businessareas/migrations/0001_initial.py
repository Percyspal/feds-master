# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-22 14:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fieldsettings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableBusinessAreaSettingDb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.TextField(default='', help_text='Machine name of this setting, e.g., ba_revenue_sales_tax.', max_length=50)),
                ('business_area_setting_order', models.IntegerField(help_text='Order of the setting in the list for the business area.')),
                ('business_area_setting_params', models.TextField(blank=True, default='{}', help_text='JSON parameters to initialize the setting.')),
            ],
        ),
        migrations.CreateModel(
            name='AvailableNotionalTableSettingDb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.TextField(default='', help_text='Machine name of this setting, e.g., tbl_invoices_total_bt.', max_length=50)),
                ('table_setting_order', models.IntegerField(default=1, help_text='Order of the setting in the settings list for the field.')),
                ('table_setting_params', models.TextField(blank=True, default='{}', help_text='JSON parameters to initialize the table setting.')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessAreaDb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='E.g., Invoicing.', max_length=200)),
                ('description', models.TextField(blank=True)),
                ('machine_name', models.TextField(default='', help_text='Machine name of this business area, e.g., ba_revenue.', max_length=50)),
                ('available_business_area_settings', models.ManyToManyField(help_text='Settings projects for this business area can have.', related_name='available_business_area_settings', through='businessareas.AvailableBusinessAreaSettingDb', to='fieldsettings.FieldSettingDb')),
            ],
        ),
        migrations.CreateModel(
            name='NotionalTableDb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='E.g., Customers.', max_length=200)),
                ('machine_name', models.TextField(default='', help_text='Machine name of this table, e.g., tbl_invoices.', max_length=50)),
                ('description', models.TextField(blank=True)),
                ('available_notional_table_settings', models.ManyToManyField(help_text='Settings that this table can have.', related_name='available_notional_table_settings', through='businessareas.AvailableNotionalTableSettingDb', to='fieldsettings.FieldSettingDb')),
                ('business_area', models.ForeignKey(help_text='What business area is this notional table part of?', on_delete=django.db.models.deletion.CASCADE, related_name='notional_table_business_area', to='businessareas.BusinessAreaDb')),
            ],
        ),
        migrations.AddField(
            model_name='availablenotionaltablesettingdb',
            name='table',
            field=models.ForeignKey(help_text='Notional table can have the setting.', on_delete=django.db.models.deletion.CASCADE, to='businessareas.NotionalTableDb'),
        ),
        migrations.AddField(
            model_name='availablenotionaltablesettingdb',
            name='table_setting',
            field=models.ForeignKey(help_text='A setting the notional table can have.', on_delete=django.db.models.deletion.CASCADE, to='fieldsettings.FieldSettingDb'),
        ),
        migrations.AddField(
            model_name='availablebusinessareasettingdb',
            name='business_area',
            field=models.ForeignKey(help_text='What business area is this setting available for?', on_delete=django.db.models.deletion.CASCADE, to='businessareas.BusinessAreaDb'),
        ),
        migrations.AddField(
            model_name='availablebusinessareasettingdb',
            name='business_area_setting',
            field=models.ForeignKey(help_text='The setting that is available.', on_delete=django.db.models.deletion.CASCADE, to='fieldsettings.FieldSettingDb'),
        ),
    ]
