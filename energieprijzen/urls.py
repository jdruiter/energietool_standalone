from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.contrib import admin
from django.urls import path
from eprijzen import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('rosetta/', include('rosetta.urls')),

    path('', views.show_energyprices, name='show_energyprices'),

    # Update prijzen in db
    # path('update_price/secretstring/<fromdate>/<todate>/', views.api_update_prices), #2023-12-01
    # path('update_price/secretstring/<period>/', views.api_update_period),            #vandaag|gisteren|vorige_week

]