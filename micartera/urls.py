from django.urls import path
from . import views
from micartera.views import *

urlpatterns = [
    path('', views.index, name='index'),
    path('charts', views.charts, name='charts'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]