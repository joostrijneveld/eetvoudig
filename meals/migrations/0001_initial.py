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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('price', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('bystanders', models.ManyToManyField(blank=True, to='meals.Bystander')),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('wbw_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Wbw_list',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('list_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=200, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='participant',
            name='wbw_list',
            field=models.ForeignKey(to='meals.Wbw_list', null=True),
        ),
        migrations.AddField(
            model_name='meal',
            name='participants',
            field=models.ManyToManyField(blank=True, to='meals.Participant'),
        ),
        migrations.AddField(
            model_name='meal',
            name='payer',
            field=models.ForeignKey(to='meals.Participant', related_name='paymeal', null=True),
        ),
        migrations.AddField(
            model_name='meal',
            name='wbw_list',
            field=models.ForeignKey(to='meals.Wbw_list', null=True),
        ),
    ]
