# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bystander',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('price', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('bystanders', models.ManyToManyField(to='meals.Bystander', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('wbw_id', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('participant', models.ForeignKey(to='meals.Participant')),
            ],
        ),
        migrations.CreateModel(
            name='Wbw_list',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('list_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=200, blank=True)),
            ],
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
        migrations.AddField(
            model_name='meal',
            name='participants',
            field=models.ManyToManyField(to='meals.Participant', blank=True),
        ),
        migrations.AddField(
            model_name='meal',
            name='payer',
            field=models.ForeignKey(related_name='paymeal', blank=True, to='meals.Participant', null=True),
        ),
        migrations.AddField(
            model_name='meal',
            name='wbw_list',
            field=models.ForeignKey(null=True, to='meals.Wbw_list'),
        ),
        migrations.AddField(
            model_name='bystander',
            name='participant',
            field=models.ForeignKey(to='meals.Participant'),
        ),
    ]
