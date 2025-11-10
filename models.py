from django.db import models


class Resource(models.Model):
code = models.CharField(max_length=50, unique=True)
name = models.CharField(max_length=200)


def __str__(self):
return f"{self.code} — {self.name}"


class Operation(models.Model):
code = models.CharField(max_length=50, unique=True)
name = models.CharField(max_length=200)
resource = models.ForeignKey(Resource, on_delete=models.PROTECT)
duration_minutes = models.IntegerField()


def __str__(self):
return f"{self.code} ({self.resource.code})"


class Order(models.Model):
external_id = models.CharField(max_length=100, unique=True)
item = models.CharField(max_length=200)
quantity = models.IntegerField()
due_date = models.DateField()
priority = models.IntegerField(default=5)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)


def __str__(self):
return f"{self.external_id} — {self.item} x{self.quantity}"


class OrderOperation(models.Model):
order = models.ForeignKey(Order, related_name='operations', on_delete=models.CASCADE)
operation = models.ForeignKey(Operation, on_delete=models.PROTECT)
sequence = models.IntegerField(default=0)
qty = models.IntegerField()


class Meta:
unique_together = ('order', 'operation', 'sequence')


class PlanRun(models.Model):
started_at = models.DateTimeField(auto_now_add=True)
finished_at = models.DateTimeField(null=True, blank=True)
status = models.CharField(max_length=20, choices=(('pending','pending'),('running','running'),('ok','ok'),('failed','failed')),
default='pending')
logs = models.TextField(blank=True)


class ScheduledOperation(models.Model):
plan_run = models.ForeignKey(PlanRun, related_name='scheduled_ops', on_delete=models.CASCADE)
order = models.ForeignKey(Order, on_delete=models.CASCADE)
operation = models.ForeignKey(Operation, on_delete=models.PROTECT)
resource = models.ForeignKey(Resource, on_delete=models.PROTECT)
start_time = models.DateTimeField()
end_time = models.DateTimeField()