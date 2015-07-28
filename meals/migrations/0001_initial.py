# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('price', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('meal', models.ForeignKey(to='meals.Meal')),
            ],
        ),
        migrations.CreateModel(
            name='WBW_list',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('list_id', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='participant',
            name='wbw_list',
            field=models.ForeignKey(to='meals.WBW_list'),
        ),
        migrations.AddField(
            model_name='meal',
            name='payer',
            field=models.ForeignKey(to='meals.WBW_list'),
        ),
    ]
