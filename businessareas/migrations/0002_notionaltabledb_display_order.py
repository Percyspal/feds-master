# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-22 18:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businessareas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notionaltabledb',
            name='display_order',
            field=models.IntegerField(default=1, help_text='Order table is displayed, from left to right.'),
        ),
    ]
