from datetime import datetime, timedelta, date
from django.shortcuts import render, HttpResponse, render
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.db.models import Avg, F, Sum
from django.db.models.functions import ExtractYear
import requests
import json
import random

from eprijzen.models import Energyprice, Gasprice

import logging
logger = logging.getLogger('eprijzen')
apilogger = logging.getLogger('api-results')

# month labels for the month bar chart
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def generate_random_color():
    # generates a hex random color
    # color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    color = "#{:06x}".format(random.randint(0, 999999))  #more darker colors
    return color

def homepage(request):
    return render(request, 'eprijzen/homepage.html', {})

def linechart(request):
    """ Shows zoomable linechart with energyprices and gaspricecs NL """

    # if the user opens the page for the first time, use todays month and year
    now = datetime.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))
    month_name = MONTHS[month - 1]

    energyprices = Energyprice.objects.filter(country_id="NL", date__month=month, date__year=year).order_by('date', 'time')

    energy_prices_data = []
    for entry in energyprices:
        energy_prices_data.append( [datetime.combine(entry.date, entry.time).timestamp()*1000, entry.all_in_price] )
    # energy_prices_data = [ [f"{e.date} {e.time}", e.all_in_price] for e in energyprices]
    print(energy_prices_data[:10])

    context = {
        "energy_prices_data":energy_prices_data,
        "month": month,
        "year": year,
        "month_name": month_name,
    }

    return render(request, 'charts/linechart.html', context)


def year_barchart(request):

    # sum_by_year = Energyprice.objects.filter(country_id="NL").annotate(year=ExtractYear('date')).values('year').annotate(total_price=Sum('all_in_price'))
    avg_by_year = Energyprice.objects.filter(country_id="NL").annotate(year=ExtractYear('date')).values('year').annotate(total_price=Avg('all_in_price'))

    # getting data for year chart
    years =  [entry['year'] for entry in list(avg_by_year)]
    year_prices = [entry['total_price'] for entry in list(avg_by_year)]
    colors = [generate_random_color() for i in range(len(years))]

    # getting data for month chart
    months_bar_values = {}
    for year in years:
        months_labels = []
        months_values = []
        for month in range(1, 13):
            prices_for_month = Energyprice.objects.filter(date__year=year, date__month=month)
            total_price_for_month = prices_for_month.aggregate(total_price=Sum('all_in_price'))['total_price'] or 0   # todo use Avg, annotate?
            # create 2 functions: total_price_per_month() and avg_prive_per_month(), so we can choose
            months_labels.append(MONTHS[month-1])
            months_values.append(round(total_price_for_month))

        months_bar_values[year] = [list(item) for item in list(zip(months_labels, months_values))]

    item_spec = [list(e) for e in list(zip(years, colors, year_prices))]

    ind = 0
    for year in years:
        item_spec[ind].append(months_bar_values[year])
        ind += 1

    context = {
        "item_spec": item_spec
    }

    return render(request, 'charts/barchart.html', context)


def month_barchart(request):
    year = request.GET.get('year', 2023)

    item_spec = []
    for month_number in range(1, 13):
        monthly_data = Energyprice.objects.filter(date__month=month_number, date__year = year, country_id="NL")
        average_value = monthly_data.aggregate(Avg('purchase_price'))['purchase_price__avg']
        label = MONTHS[month_number-1]
        color = generate_random_color()

        data_for_linechart = []
        for entry in monthly_data:
            data_for_linechart.append([datetime.combine(entry.date, entry.time).timestamp() * 1000, round(entry.purchase_price, 2)])

        item_spec.append([label, average_value, color, data_for_linechart])

    context = {
        "item_spec": item_spec,
        "year": year
    }

    return render(request, 'charts/month_bar_chart.html', context)


def week_barchart(request):
    """ Show clickable barchart
    Todo start the chart always at 2024. Users can go prev year and next year through time
    """
    # current_date = datetime(2022, 8, 27)
    current_date = datetime.now()
    start_of_week = current_date - timedelta(days=6)
    date_range = [start_of_week + timedelta(days=x) for x in range(0, 7)]

    item_spec = []
    for date in date_range:
        daily_data = Energyprice.objects.filter(date=date, country_id="NL")
        daily_data = daily_data.order_by('time')

        # data for bar chart
        average_value = daily_data.aggregate(Avg('all_in_price'))['all_in_price__avg']
        label = date.strftime("%d.%m.%Y")
        color = generate_random_color()

        # data for linechart
        data_for_linechart = []
        for entry in daily_data:
            data_for_linechart.append([datetime.combine(entry.date, entry.time).timestamp() * 1000, entry.all_in_price])

        item_spec.append([label, average_value, color, data_for_linechart])

    context = {
        "year": current_date.year,
        "item_spec": item_spec
    }
    return render(request, 'charts/month_bar_chart.html', context)  # todo make own html page