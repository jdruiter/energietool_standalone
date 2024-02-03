from django.urls import path
from linechart import views

urlpatterns = [
    path('', views.plot_graph, name='linechart'),
]