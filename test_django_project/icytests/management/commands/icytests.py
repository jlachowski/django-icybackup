"""
This runs the tests for icybackup.

We're not using Django's unit test framework because this is really only one big test,
and Django likes to use an in-memory sqlite database, which can't be backed up.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import hashlib
from optparse import make_option
from django.conf import settings
import os
from ...models import Blah
from django.core.management import call_command, BaseCommand

IMAGE_SHA1 = "65c31668e9a889849e7ee8797f50e41d01a4bdcc"

TEST_POSTGRES = "This is the test content for the Postgres database"
TEST_MYSQL = "This is the test content for the MySQL database"
TEST_SQLITE = "This is the test content for the SQLite database"

class Command(BaseCommand):
	option_list = BaseCommand.option_list + (
	        make_option('--without-mysql', action='store_false', dest='mysql'),
	        make_option('--without-postgres', action='store_false', dest='postgres'),
	        make_option('--without-sqlite', action='store_false', dest='sqlite'),
	    )
	def handle(self, *args, **options):
		try:
			self._handle(*args, **options)
		except:
			if os.path.exists('backup.tgz'):
				os.unlink('backup.tgz')
			raise
	def _handle(self, *args, **options):
		postgres = true_if_none(options.get('postgres'))
		mysql = true_if_none(options.get('mysql'))
		sqlite = true_if_none(options.get('sqlite'))

		print(postgres, mysql, sqlite)

		# Create DB objects
		if postgres:
			call_command('migrate', '--noinput', input=False, database='postgres')
			Blah.objects.using('postgres').all().delete()
			pg_test = Blah.objects.create(text=TEST_POSTGRES)
			pg_test.save(using='postgres')
		if mysql:
			call_command('migrate', '--noinput', input=False, database='mysql')
			Blah.objects.using('mysql').all().delete()
			mysql_test = Blah.objects.create(text=TEST_MYSQL)
			mysql_test.save(using='mysql')
		if sqlite:
			call_command('migrate', --noinput', input=False)
			Blah.objects.using('default').all().delete()
			sqlite_test = Blah.objects.create(text=TEST_SQLITE)
			sqlite_test.save()

		# remove databases from the DB dict if we're not testing them
		if not postgres: del settings.DATABASES['postgres']
		if not mysql: del settings.DATABASES['mysql']
		if not sqlite: del settings.DATABASES['default']

		# perform backup
		call_command('backup', output='backup.tgz')

		# delete everything
		if postgres: pg_test.delete()
		if mysql: mysql_test.delete()
		if sqlite: os.unlink(settings.DATABASES['default']['NAME'])
		os.unlink(os.path.join(settings.MEDIA_ROOT, 'test_image.jpg'))

		# perform restore
		call_command('restore', input='backup.tgz')

		# check that the file is present
		img_path = os.path.join(settings.MEDIA_ROOT, 'test_image.jpg')
		assert os.path.exists(img_path)
		assert hashfile(img_path) == IMAGE_SHA1

		# check that the postgres db entry is there
		if postgres:
			qs = Blah.objects.using('postgres').all()
			assert len(qs) == 1
			assert qs[0].text == TEST_POSTGRES

		# check that the mysql db entry is there
		if mysql:
			qs = Blah.objects.using('mysql').all()
			assert len(qs) == 1
			assert qs[0].text == TEST_MYSQL

		# check that the sqlite db entry is there
		if sqlite:
			qs = Blah.objects.using('default').all()
			assert len(qs) == 1
			assert qs[0].text == TEST_SQLITE

def true_if_none(a):
	if a is None:
		return True
	else:
		return a

def hashfile(filepath):
	sha1 = hashlib.sha1()
	f = open(filepath, 'rb')
	try:
		sha1.update(f.read())
	finally:
		f.close()
	return sha1.hexdigest()
