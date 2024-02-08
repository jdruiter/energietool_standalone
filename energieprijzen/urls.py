from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.contrib import admin
from django.urls import path
from eprijzen import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.show_energyprices_joris),
    path('linechart/', include("linechart.urls")),
    path('barchart/', include("barchart.urls")),
    path('monthchart/', include("month_bar_chart.urls")),
]