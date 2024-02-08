from datetime import date, datetime, timedelta
from django.shortcuts import render, HttpResponse, render
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
import requests
import json
from django.db.models import Avg, F


from eprijzen.models import Energyprice, Gasprice

import logging
logger = logging.getLogger('eprijzen')
apilogger = logging.getLogger('api-results')


def show_energyprices_joris(request):
    """ Show energy and gas prices for NL """

    context = {}
    period = request.GET.get('period')
    if not period:
        return render(request, 'eprijzen/eprijzen.html', context)

    today = datetime.today()
    tomorrow = today+timedelta(days=1)
    yesterday = today-timedelta(days=1)

    energyprices = Energyprice.objects.all()
    gasprices = Gasprice.objects.all()
    if period == 'today':
        energyprices = energyprices.filter(date=date.today())
        gasprices = gasprices.filter(date=date.today())
    elif period == '3days':
        energyprices = energyprices.filter(date__range=[yesterday, tomorrow])
        gasprices = gasprices.filter(date__range=[yesterday, tomorrow])
    elif period == 'days':
        # todo take mean of the day instead of single price at 12:00
        energyprices = energyprices.filter(time='12:00')
        gasprices = gasprices.filter(time='12:00')
    elif period == 'weeks':
        # todo take mean of the week instead of single price at 12:00
        energyprices = energyprices.filter(date__week_day=1, time='12:00')
        gasprices = gasprices.filter(date__week_day=1, time='12:00')
    elif period == 'months':
        # todo take mean of the month instead of single price at 12:00
        energyprices = energyprices.filter(date__week_day=1, time='12:00')
        gasprices = gasprices.filter(date__week_day=1, time='12:00')

    context['period'] = period
    context['energyprices'] = energyprices.order_by('-date', 'time')[:100]
    context['gasprices'] = gasprices.order_by('-date', 'time')[:100]
    context['energyprices_list'] = energyprices.order_by('-date', 'time').values_list('purchase_price', flat=True)[:100]
    context['gasprices_list'] = gasprices.order_by('-date', 'time').values_list('purchase_price', flat=True)[:100]

    return render(request, 'eprijzen/eprijzen.html', context)



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

    today = datetime.today()
    tomorrow = today+timedelta(days=1)
    yesterday = today-timedelta(days=1)

    energyprices_nl = Energyprice.objects.filter(country_id='NL')
    gasprices_nl = Gasprice.objects.filter(country_id='NL')

    if period == 'today':
        energyprices = energyprices_nl.filter(date=date.today())
        gasprices = gasprices_nl.filter(date=date.today())
    elif period == '3days':
        energyprices = energyprices_nl.filter(date__range=[yesterday, tomorrow])
        gasprices = gasprices_nl.filter(date__range=[yesterday, tomorrow])

    elif period == 'days':
        energyprices = energyprices_nl.filter(date=date)
        gasprices = gasprices_nl.filter(date=date)
        context["energy_prices_data"] = days_processing(energyprices, date)
        context["gas_prices_data"] = days_processing(gasprices, date)

    elif period == 'weeks':
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=6)

        energy_prices_data = energyprices_nl.filter(date__range=(start_date, end_date))
        energy_prices_data = energy_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        gas_prices_data = gasprices_nl.filter(date__range=(start_date, end_date))
        gas_prices_data = gas_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        # data for graphs
        energy_prices_data = weeks_processing(energy_prices_data)
        gas_prices_data = weeks_processing(gas_prices_data)
        context["energy_prices_data"] = energy_prices_data
        context["gas_prices_data"] = gas_prices_data

    elif period == 'months':
        year, month = date.split("-")
        year, month = int(year), int(month)

        energy_prices_data = energyprices_nl.filter(date__month=month, date__year=year)
        energy_prices_data = energy_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        gas_prices_data = gasprices_nl.filter(date__month=month, date__year=year)
        gas_prices_data = gas_prices_data.values('date').annotate(average_value=Avg('purchase_price'))

        # data for graphs
        energy_prices_data = months_processing(energy_prices_data)
        gas_prices_data = months_processing(gas_prices_data)
        context["energy_prices_data"] = energy_prices_data
        context["gas_prices_data"] = gas_prices_data


    context['period'] = period
    context['date'] = date

    # context['energieprijzen'] = energyprices.order_by('-date', 'time')[:100]
    # context['gasprijzen'] = gasprices.order_by('-date', 'time')[:100]
    # context['energieprijzen_list'] = energyprices.order_by('-date', 'time').values_list('purchase_price', flat=True)[:100]
    # context['gasprijzen_list'] = gasprices.order_by('-date', 'time').values_list('purchase_price', flat=True)[:100]

    return render(request, 'eprijzen/eprijzen.html', context)



def days_processing(energyprices, date):
    """ Some text to explain what this function does """

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