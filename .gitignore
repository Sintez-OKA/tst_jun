from django.test import TestCase, Client
from django.core.management import call_command
from io import StringIO
from planner.models import Order, PlanRun, ScheduledOperation
import os


class ImportTestCase(TestCase):
def test_import_idempotent(self):
path = os.path.join(os.path.dirname(__file__), 'orders.csv')
out = StringIO()
call_command('import_orders', path, stdout=out)
count1 = Order.objects.count()
call_command('import_orders', path, stdout=out)
count2 = Order.objects.count()
self.assertEqual(count1, count2)


class RunPlanTestCase(TestCase):
def setUp(self):
path = os.path.join(os.path.dirname(__file__), 'orders.csv')
call_command('import_orders', path)


def test_run_plan_creates_schedule(self):
client = Client()
resp = client.post('/planner/api/run_plan/')
self.assertEqual(resp.status_code, 200)
self.assertTrue(PlanRun.objects.filter(status='ok').exists())
self.assertTrue(ScheduledOperation.objects.exists())