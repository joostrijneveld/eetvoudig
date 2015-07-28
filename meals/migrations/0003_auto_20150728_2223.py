# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_meal_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='payer',
            field=models.ForeignKey(to='meals.WBW_list', null=True),
        ),
    ]
