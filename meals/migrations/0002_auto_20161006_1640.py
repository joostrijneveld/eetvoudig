# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wbw_list',
            name='list_id',
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='wbw_id',
            field=models.CharField(max_length=40, unique=True),
        ),
    ]
