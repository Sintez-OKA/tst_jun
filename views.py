from django.http import JsonResponse
from django.views.decorators.http import require_POST
from planner.models import PlanRun, OrderOperation, ScheduledOperation
from django.utils import timezone
from django.db import transaction


@require_POST
def run_plan(request):
plan = PlanRun.objects.create(status='running')
try:
now = timezone.now()
# простая FIFO-симуляция — группируем по ресурс и ставим в очередь
ops = OrderOperation.objects.select_related('order', 'operation', 'operation__resource')
resource_events = {}
to_create = []
for oo in ops:
res = oo.operation.resource
last_end = resource_events.get(res.code, now)
start = last_end
end = start + timezone.timedelta(minutes=oo.operation.duration_minutes)
to_create.append(ScheduledOperation(plan_run=plan, order=oo.order, operation=oo.operation, resource=res, start_time=start, end_time=end))
resource_events[res.code] = end
with transaction.atomic():
ScheduledOperation.objects.bulk_create(to_create)
plan.status = 'ok'
plan.finished_at = timezone.now()
plan.save()
return JsonResponse({'status': 'ok', 'plan_run_id': plan.id})
except Exception as e:
plan.status = 'failed'
plan.logs = str(e)
plan.finished_at = timezone.now()
plan.save()
return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)