# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-05 06:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20171105_1401'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asin',
            name='tag',
        ),
        migrations.AddField(
            model_name='asin',
            name='tags',
            field=models.ManyToManyField(to='myapp.Tag'),
        ),
    ]
