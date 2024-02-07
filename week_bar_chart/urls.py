from django.urls import path
from week_bar_chart import views

urlpatterns = [
    path('', views.plot_graph, name='week_bar_chart'),
]