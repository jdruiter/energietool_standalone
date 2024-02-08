from django.urls import path
from month_bar_chart import views

urlpatterns = [
    path('', views.plot_graph, name='month_bar_chart'),
]