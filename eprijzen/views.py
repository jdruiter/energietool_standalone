from datetime import datetime, timedelta
from django.shortcuts import render, HttpResponse, render
from django.db.models import Avg, ExpressionWrapper, F, DateTimeField
from django.db.models.functions import TruncDate, Concat
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
import requests
import json

from eprijzen.models import EnergyPrice, GasPrice

import logging
logger = logging.getLogger('eprijzen')
apilogger = logging.getLogger('api-results')


def days_processing(energyprices, date):
    date_object = datetime.strptime(date, "%Y-%m-%d").date()
    purchase_prices = []
    times = []
    for e in energyprices:
        purchase_prices.append(e.purchase_price)
        combined_datetime = datetime.combine(date_object, e.time)
        times.append(combined_datetime.timestamp())

    return [[time, price] for time, price in zip(times, purchase_prices)]

def get_min_max_mean(data):
    if not data:
        return []

    max_entry = data.order_by('-purchase_price').first()
    min_entry = data.order_by('purchase_price').first()
    mean = data.aggregate(Avg('purchase_price'))
    mean = mean["purchase_price__avg"]

    statistics = {
        "mean": round(mean, 4),
        "max": {
            "value": max_entry.purchase_price,
            "date": max_entry.date,
            "time": max_entry.time
        },
        "min": {
            "value": min_entry.purchase_price,
            "date": min_entry.date,
            "time": min_entry.time
        }
    }

    return statistics


def weeks_processing(data):
    times = []
    purchase_prices = []

    for d in data:
        purchase_prices.append(d['average_value'])
        datetime_object = datetime.combine(d["date"], datetime.min.time())
        times.append(datetime_object.timestamp())

    return [[time, price] for time, price in zip(times, purchase_prices)]

def months_processing(data):
    times = []
    purchase_prices = []

    for d in data:
        purchase_prices.append(d['average_value'])
        datetime_object = datetime.combine(d["date"], datetime.min.time())
        times.append(datetime_object.timestamp())

    return [[time, price] for time, price in zip(times, purchase_prices)]

def show_energyprices(request):
    """ Show energy and gas prices for NL
    Todo Improvements:
    1. User can select days, weeks, months. The mean of (day|week}month) is graphed in the graph. The min, max and mean are shown in a table.
    2. User can navigate forward and backwards in time (prev, next day|week|month)
    """

    context = {}
    period = request.GET.get('period', '')
    date = request.GET.get('date', False)
    if not date:
        return render(request, 'eprijzen/eprijzen.html', context)

    energyprices_nl = EnergyPrice.objects.filter(country_id='NL')
    gasprices_nl = GasPrice.objects.filter(country_id='NL')


    if period == 'today':
        energyprices = energyprices_nl.filter(date=date.today())
        gasprices = gasprices_nl.filter(date=date.today())
    elif period == 'tomorrow':
        energyprices = energyprices_nl.filter(date=date.today()+timedelta(days=1))
        gasprices = gasprices_nl.filter(date=date.today()+timedelta(days=1))
    elif period == 'yesterday':
        energyprices = energyprices_nl.filter(date=date.today()-timedelta(days=1))
        gasprices = gasprices_nl.filter(date=date.today()-timedelta(days=1))
    elif period == 'days':
        energyprices = energyprices_nl.filter(date=date)
        gasprices = gasprices_nl.filter(date=date)

        # data for graphs
        energy_prices_data = days_processing(energyprices, date)
        gas_prices_data = days_processing(gasprices, date)
        context["energy_prices_data"] = energy_prices_data
        context["gas_prices_data"] = gas_prices_data

        # data for data tables
        context["energyprices"] = energyprices
        context["gasprices"] = gasprices

        # data for min_max_mean tables
        context["statistics_energy"] = get_min_max_mean(energyprices)
        context["statistics_gas"] = get_min_max_mean(gasprices)

    elif period == 'weeks':
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=6)

        energy_prices_data = energyprices_nl.filter(date__range=(start_date, end_date))
        energy_prices_data = energy_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        gas_prices_data = gasprices_nl.filter(date__range=(start_date, end_date))
        gas_prices_data = gas_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        # data for data tables
        context["energyprices"] = energy_prices_data
        context["gasprices"] =    gas_prices_data

        # data for graphs
        energy_prices_data = weeks_processing(energy_prices_data)
        gas_prices_data = weeks_processing(gas_prices_data)
        context["energy_prices_data"] = energy_prices_data
        context["gas_prices_data"] = gas_prices_data

        # data for min_max_mean tables
        context["statistics_energy"] = get_min_max_mean(energyprices_nl.filter(date__range=(start_date, end_date)))
        context["statistics_gas"] = get_min_max_mean(gasprices_nl.filter(date__range=(start_date, end_date)))


    elif period == 'months':
        year, month = date.split("-")
        year, month = int(year), int(month)

        energy_prices_data = energyprices_nl.filter(date__month=month, date__year=year)
        energy_prices_data = energy_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        gas_prices_data = gasprices_nl.filter(date__month=month, date__year=year)
        gas_prices_data = gas_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        # data for data tables
        context["energyprices"] = energy_prices_data
        context["gasprices"] = gas_prices_data

        # data for graphs
        energy_prices_data = months_processing(energy_prices_data)
        gas_prices_data = months_processing(gas_prices_data)
        context["energy_prices_data"] = energy_prices_data
        context["gas_prices_data"] = gas_prices_data

        # data for min_max_mean tables
        context["statistics_energy"] = get_min_max_mean(energyprices_nl.filter(date__month=month, date__year=year))
        context["statistics_gas"] = get_min_max_mean(gasprices_nl.filter(date__month=month, date__year=year))


    context['period'] = period
    context['date'] = date

    # context['energieprijzen'] = energyprices.order_by('-date', 'time')[:100]
    # context['gasprijzen'] = gasprices.order_by('-date', 'time')[:100]
    # context['energieprijzen_list'] = energyprices.order_by('-date', 'time').values_list('purchase_price', flat=True)[:100]
    # context['gasprijzen_list'] = gasprices.order_by('-date', 'time').values_list('purchase_price', flat=True)[:100]

    return render(request, 'eprijzen/eprijzen.html', context)