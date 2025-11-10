import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from planner.models import Order, Operation, Resource, OrderOperation
from django.utils.dateparse import parse_date


class Command(BaseCommand):
help = 'Import orders from CSV file (idempotent)'


def add_arguments(self, parser):
parser.add_argument('csvfile', type=str)


def handle(self, *args, **options):
path = options['csvfile']
created = updated = skipped = 0
try:
with open(path, newline='') as csvfile:
reader = csv.DictReader(csvfile)
with transaction.atomic():
for row in reader:
ext_id = row['external_id'].strip()
item = row['item'].strip()
qty = int(row['quantity'])
due = parse_date(row['due_date'])
priority = int(row.get('priority', 5))
op_code = row['operation_code'].strip()
res_code = row['resource_code'].strip()
duration = int(row.get('duration_minutes') or 0)


resource, _ = Resource.objects.get_or_create(code=res_code, defaults={'name': res_code})
operation, _ = Operation.objects.get_or_create(code=op_code, defaults={'name': op_code, 'resource': resource, 'duration_minutes': duration})


order, created_flag = Order.objects.update_or_create(
external_id=ext_id,
defaults={'item': item, 'quantity': qty, 'due_date': due, 'priority': priority}
)
if created_flag:
created += 1
else:
updated += 1


# create or update OrderOperation (sequence default 0)
oo, _ = OrderOperation.objects.update_or_create(
order=order,
operation=operation,
sequence=0,
defaults={'qty': qty}
)
self.stdout.write(self.style.SUCCESS(f'Import finished. created={created} updated={updated}'))
except FileNotFoundError:
raise CommandError(f'File not found: {path}')
except Exception as e:
raise CommandError(str(e))