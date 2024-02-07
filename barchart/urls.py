from django.urls import path
from barchart import views

urlpatterns = [
    path('', views.plot_chart, name='barchart')
]