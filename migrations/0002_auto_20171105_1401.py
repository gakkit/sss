# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-05 06:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='content',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='log',
            name='data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Data'),
        ),
    ]
