from django.shortcuts import render
from eprijzen.models import Energyprice
from datetime import datetime, date

from pprint import pprint
import numpy as np
from django.db.models import Q, IntegerField
from django.db.models.functions import ExtractMonth

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def plot_graph(request):
    if request.method == 'GET':
        month = request.GET.get('month')
        year = request.GET.get('year')

    # if the user opens the page for the first time: month = 7, year = 2020
    if not month or not year:
        month = 7
        year = 2020

    month = int(month)
    year = int(year)
    month_name = months[month - 1]

    energy_prices = Energyprice.objects.filter(
        date__month = month, date__year = year, country_id = "NL"
    )

    energy_prices_data = []
    for entry in energy_prices:
        energy_prices_data.append([datetime.combine(entry.date, entry.time).timestamp()*1000, entry.purchase_price])

    context = {
        "energy_prices_data":energy_prices_data,
        "month": month,
        "year": year,
        "month_name": month_name,
    }


    return render(request, 'charts/linechart.html', context)
