from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from django.contrib import admin
from .models import GlacierBackup

class GlacierBackupAdmin (admin.ModelAdmin):
	list_display = ('date', 'glacier_id')
	readonly_fields = ('glacier_id', 'date')
	
	def has_add_permission(self, request):
		return False
		
	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(GlacierBackup, GlacierBackupAdmin)