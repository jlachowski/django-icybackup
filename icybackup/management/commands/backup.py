from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import os
import sys
import time
import shutil
from optparse import make_option
from tempfile import mkdtemp, NamedTemporaryFile
import tarfile
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...components import db, glacier

# Based on: http://code.google.com/p/django-backup/
# Based on: http://www.djangosnippets.org/snippets/823/
# Based on: http://www.yashh.com/blog/2008/sep/05/django-database-backup-view/


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-o', '--output', default=None, dest='output',
            help='Write backup to file'),
        make_option(
            '-d', '--outdir', default=None, dest='outdir',
            help='Write backup to timestamped file in a directory'),
        make_option(
            '-g', '--glacier', default=None, dest='glacier',
            help='Upload backup to the Amazon Glacier vault with the given ARN'),
        make_option(
            '-O', '--stdout', action='store_true', dest='stdout',
            help='Output backup tarball to standard output'),
        make_option(
            '--extra', '-e', action='append', default=[], dest='extras',
            help='Include extra directories or files in the backup tarball'),
        make_option(
            '-n', '--native-django-dump', action='store_true', default=None,
            dest='nativedump', help='use django build in database dump method'),
    )

    help = "Back up a Django installation (database and media directory)."

    def handle(self, *args, **options):
        extras = options.get('extras')
        nativedump = options.get('nativedump')
        output_file = options.get('output')
        output_dir = options.get('outdir')
        glacier_vault = options.get('glacier')
        output_to_stdout = options.get('stdout')

        output_file_temporary = False

        # glacier backups go to a temporary file
        if glacier_vault is not None or output_to_stdout:
            output_file_temporary = True
            output_file_obj = NamedTemporaryFile(delete=False)
            output_file_obj.close()  # we'll open it later
            output_file = output_file_obj.name

        if output_file is None:
            if output_dir is None:
                raise CommandError('You must specify an output file')
            else:
                output_file = os.path.join(output_dir, '{}.tgz'.format(_time()))

        media_root = settings.MEDIA_ROOT

        # Create a temporary directory to perform our backup in
        backup_root = mkdtemp()
        database_root = os.path.join(backup_root, 'databases')
        os.mkdir(database_root)

        # Back up databases
        if nativedump:
            db.django_native_dump(settings, database_root)
        else:
            db.backup_to(settings, database_root)

        # create backup gzipped tarball
        with tarfile.open(output_file, 'w:gz') as tf:
            tf.add(database_root, arcname='backup/databases')
            tf.add(media_root, arcname='backup/media')
            if len(extras) > 0:
                extras_mf = NamedTemporaryFile(delete=False)
                for count, extra in enumerate(extras):
                    tf.add(extra, arcname='backup/extras/{}'.format(count))
                    extras_mf.write('{},{}\n'.format(
                        count, extra.replace(',', '\\,')))
                extras_mf.close()
                tf.add(extras_mf.name, arcname='backup/extras/manifest')
                os.unlink(extras_mf.name)

        # upload to glacier
        if glacier_vault is not None:
            glacier.upload(glacier_vault, output_file, settings)
            glacier.reconcile(glacier_vault, settings)
            glacier.prune(glacier_vault, settings)

        # output to stdout
        if output_to_stdout:
            with open(output_file, 'r') as f:
                sys.stdout.write(f.read())

        # clean up
        shutil.rmtree(backup_root, ignore_errors=True)
        if output_file_temporary:
            os.unlink(output_file)


def _time():
    return time.strftime('%Y%m%d-%H%M%S')
