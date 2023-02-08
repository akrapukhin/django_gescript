from django.urls import path
from . import views

urlpatterns = [
    path('', views.query, name='query'),
    path('counters/', views.counters, name='counters'),
    path('trud/', views.trud, name='trud')
]
