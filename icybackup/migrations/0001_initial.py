# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlacierBackup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('glacier_id', models.CharField(unique=True, max_length=138, verbose_name='Glacier backup ID')),
                ('date', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Glacier backup',
                'verbose_name_plural': 'Glacier backups',
            },
        ),
        migrations.CreateModel(
            name='GlacierInventory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inventory_id', models.CharField(unique=True, max_length=92, verbose_name='Glacier inventory ID')),
                ('collected_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('requested_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
