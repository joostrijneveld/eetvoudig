# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='participant',
            name='name',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='wbw_list',
        ),
        migrations.AddField(
            model_name='participation',
            name='participant',
            field=models.ForeignKey(to='meals.Participant'),
        ),
        migrations.AddField(
            model_name='participation',
            name='wbw_list',
            field=models.ForeignKey(to='meals.Wbw_list'),
        ),
        migrations.AddField(
            model_name='participant',
            name='wbw_list',
            field=models.ManyToManyField(to='meals.Wbw_list', through='meals.Participation'),
        ),
    ]
