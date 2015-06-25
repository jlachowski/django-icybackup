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

        # Changing field 'GlacierBackup.date'
        db.alter_column('icybackup_glacierbackup', 'date', self.gf('django.db.models.fields.DateTimeField')())

    def backwards(self, orm):

        # Changing field 'GlacierBackup.date'
        db.alter_column('icybackup_glacierbackup', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    models = {
        'icybackup.glacierbackup': {
            'Meta': {'object_name': 'GlacierBackup'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'glacier_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '138'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'icybackup.glacierinventory': {
            'Meta': {'object_name': 'GlacierInventory'},
            'collected_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventory_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '92'}),
            'requested_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['icybackup']