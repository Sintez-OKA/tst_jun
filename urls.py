from django.urls import path
from . import views


urlpatterns = [
path('api/run_plan/', views.run_plan, name='run_plan'),
]