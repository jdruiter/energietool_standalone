from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('eprijzen.urls')),

]