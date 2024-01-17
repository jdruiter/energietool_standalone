from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import EnergyPrice, GasPrice


@admin.register(EnergyPrice)
class EnergieprijzenAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    model = EnergyPrice
    list_display = ['country_id', 'date', 'time', 'purchase_price', 'all_in_price' ]
    list_display_links = ['country_id', 'date']
    list_filter = ['date', 'country_id']
    ordering = ['country_id', 'date', 'time']
    date_hierarchy = 'date'


@admin.register(GasPrice)
class GasprijzenAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    model = EnergyPrice
    list_display = ['country_id', 'date', 'time', 'purchase_price', 'all_in_price']
    list_display_links = ['country_id', 'date']
    list_filter = ['date', 'country_id']
    ordering = ['country_id', 'date', 'time']
    date_hierarchy = 'date'


# class CountryAdmin(admin.ModelAdmin):
#
#     model = Country
#     list_display = ['country_id', 'country_iso', 'country_name']
#     ordering = ['country_id']

# class BelastingRegelsAdmin(admin.ModelAdmin):  #ImportExportModelAdmin
#
#     model = BelastingRegels
#     list_display = ['start_date', 'end_date', 'btw', 'opslag', 'ode', 'eb']
#     list_display_links = ['start_date', 'end_date']
#     list_filter = ['kind']
#     # search_fields = ''
#     ordering = ['kind', '-start_date']
#     readonly_fields = ['btw_display', 'opslag_display', 'ode_display', 'eb_display']
#
#
# class BelastingPerDagAdmin(admin.ModelAdmin):
#
#     model = BelastingPerDag
#     list_display = ['datum', 'kind',  'btw', 'opslag', 'ode', 'eb']
#     list_display_links = ['datum']
#     list_filter = ['kind']
#     ordering = ['kind', '-datum']
#     date_hierarchy = 'datum'
#