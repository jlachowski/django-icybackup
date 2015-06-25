from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from .. import models
from datetime import timedelta, datetime
from boto.glacier.layer2 import Layer2 as Glacier
from dateutil.parser import parse
from django.core.management import CommandError

# upload to amazon glacier

def _get_vault_from_arn(arn, settings):
	g = Glacier(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
	for i in g.list_vaults():
		if arn == i.arn:
			return i
	else:
		raise CommandError('The specified vault could not be accessed.')

def upload(arn, output_file, settings):
	vault = _get_vault_from_arn(arn, settings)
	id = vault.upload_archive(output_file)
	
	# record backup internally
	# we don't need this record in order to restore from backup (obviously!)
	# but it makes pruning the backup set easier, and amazon reccomends it
	record = models.GlacierBackup.objects.create(glacier_id=id, date=datetime.now())
	record.save()

def reconcile(arn, settings):
	vault = _get_vault_from_arn(arn, settings)

	# check any inventory requests that have not been collected,
	# and if they are finished, collect them
	to_be_collected = models.GlacierInventory.objects.filter(collected_date=None)
	if len(to_be_collected) > 0:
		for record in to_be_collected:
			job = vault.get_job(record.inventory_id)
			if job.completed:
				print("Reconciling inventory", record.inventory_id)
				_do_reconcile(job.get_output())
				record.collected_date = datetime.now()
				record.save()

	# if there are no collected inventories in the last 14 days,
	# and no requested inventories in the last 3,
	# request another inventory
	max_requested_date = datetime.now() - timedelta(days=3)
	max_collected_date = datetime.now() - timedelta(days=14)
	if models.GlacierInventory.objects.exclude(collected_date__lte=max_collected_date).exclude(requested_date__lte=max_requested_date).count() == 0:
		job_id = vault.retrieve_inventory()
		record = models.GlacierInventory.objects.create(inventory_id=job_id)
		record.save()

def _do_reconcile(inventory):
	for archive in inventory['ArchiveList']:
		id = archive['ArchiveId']
		creation_date = parse(archive['CreationDate'])
		if not models.GlacierBackup.objects.filter(glacier_id=id).exists():
			models.GlacierBackup.objects.create(glacier_id=id, date=creation_date).save()

def prune(arn, settings):
	vault = _get_vault_from_arn(arn, settings)
	keep_all_before = datetime.now() - timedelta(days=31)
	keep_daily_before = datetime.now() - timedelta(days=90)
	keep_weekly_before = datetime.now() - timedelta(days=365)
	oldest_date = models.GlacierBackup.objects.all().order_by('date')[0].date
	_do_delete(vault, 1, keep_all_before, keep_daily_before)
	_do_delete(vault, 30, keep_daily_before, keep_weekly_before)
	_do_delete(vault, 30, keep_weekly_before, oldest_date)

def _do_delete(vault, day_count, from_date, to_date):
	begin_date = from_date
	while begin_date >= to_date:
		end_date = begin_date - timedelta(days=day_count)
		if end_date < to_date:
			end_date = to_date
		qs = models.GlacierBackup.objects.filter(date__lt=end_date, date__gte=begin_date)
		# delete all but the most recent
		for record in qs[1:]:
			print("Deleting", record.glacier_id)
			vault.delete(record.glacier_id)
			record.delete()
