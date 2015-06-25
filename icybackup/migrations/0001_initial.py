# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GlacierBackup'
        db.create_table('icybackup_glacierbackup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('glacier_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=138)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('icybackup', ['GlacierBackup'])


    def backwards(self, orm):
        # Deleting model 'GlacierBackup'
        db.delete_table('icybackup_glacierbackup')


    models = {
        'icybackup.glacierbackup': {
            'Meta': {'object_name': 'GlacierBackup'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'glacier_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '138'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['icybackup']