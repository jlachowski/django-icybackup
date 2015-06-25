from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import os
import sys
import shutil
from optparse import make_option
from tempfile import mkdtemp, NamedTemporaryFile
import tarfile
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from distutils.dir_util import copy_tree

from ...components import db

# Based on: http://code.google.com/p/django-backup/
# Based on: http://www.djangosnippets.org/snippets/823/
# Based on: http://www.yashh.com/blog/2008/sep/05/django-database-backup-view/


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-i', '--file', default=None, dest='input',
            help='Read backup from file'),
        make_option(
            '--pg-restore-flags', default=None, dest='postgres_flags',
            help='Flags to pass to pg_restore'),
        make_option(
            '-I', '--stdin', action='store_true', dest='stdin',
            help='Read backup from standard input'),
        make_option(
            '-n', '--native-django-restore', action='store_true', default=None,
            dest='nativerestore', help='use django build in load data method'),
        )
    help = "Restore a Django installation (database and media directory)."

    def handle(self, *args, **options):
        input_file = options.get('input')
        input_from_stdin = options.get('stdin')
        nativerestore = options.get('nativerestore')
        input_file_temporary = False

        if input_file is None and input_from_stdin is None:
            raise CommandError('You must specify an input file')

        media_root = settings.MEDIA_ROOT

        # read from stdin
        if input_from_stdin:
            input_file_temporary = True
            input_file_obj = NamedTemporaryFile(delete=False)
            input_file_obj.write(sys.stdin.read())
            input_file_obj.close()
            input_file = input_file_obj.name

        # Create a temporary directory to extract our backup to
        extract_root = mkdtemp()
        backup_root = os.path.join(extract_root, 'backup')
        database_root = os.path.join(backup_root, 'databases')

        # extract the gzipped tarball
        with tarfile.open(input_file, 'r') as tf:
            tf.extractall(extract_root)

        # Restore databases
        db_options = {}
        if options.get('postgres_flags') is not None:
            db_options['postgres_flags'] = options['postgres_flags']

        if nativerestore:
            db.django_native_restore(settings, database_root)
        else:
            db.restore_from(settings, database_root, **db_options)

        # Restore media directory
        copy_tree(os.path.join(backup_root, 'media'), media_root)

        # clean up
        shutil.rmtree(extract_root, ignore_errors=True)
        if input_file_temporary:
            os.unlink(input_file)
