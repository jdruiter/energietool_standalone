from django.urls import path
from eprijzen import views

urlpatterns = [
    path('', views.homepage),
    path('linechart/', views.linechart, name='linechart'),
    path('weekchart/', views.week_barchart, name='weekchart'),
    path('monthchart/', views.month_barchart, name='monthchart'),
    path('yearchart/', views.year_barchart, name='yearchart'),
]