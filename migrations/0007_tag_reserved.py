# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-12 15:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_auto_20171112_2240'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='reserved',
            field=models.BooleanField(default=False),
        ),
    ]
