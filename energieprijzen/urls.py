from django.urls import path, include, re_path
from django.views.generic import RedirectView, TemplateView
from django.contrib import admin
from django.urls import path
from eprijzen import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path('', views.show_energyprices, name='show_energyprices'),
]