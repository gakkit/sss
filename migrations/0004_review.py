# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-08 15:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_auto_20171105_1437'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(default='')),
                ('title', models.CharField(default='', max_length=200)),
                ('content', models.TextField(default='')),
                ('star', models.IntegerField(default=0)),
                ('critical', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Critical')),
            ],
        ),
    ]