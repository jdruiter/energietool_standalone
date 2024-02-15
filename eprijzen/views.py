from datetime import datetime, timedelta, date, timezone
from django.shortcuts import render, HttpResponse, render
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.db.models import Avg, F, Sum
from django.db.models.functions import ExtractYear
import requests
import json
import random
from pprint import pprint

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
    return render(request, 'eprijzen/base.html', {})



def linechart(request):
    """ Shows zoomable linechart with energyprices and gaspricecs NL """

    # if the user opens the page for the first time, use todays month and year
    now = datetime.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))
    month_name = MONTHS[month - 1]

    energyprices = Energyprice.objects.filter(country_id="NL", date__month=month, date__year=year).order_by('date', 'time')
    print(datetime(2024, 1, 20).timestamp()*1000)
    energy_prices_data = []
    for entry in energyprices:
        energy_prices_data.append( [datetime.combine(entry.date, entry.time, tzinfo=timezone.utc).timestamp()*1000, entry.purchase_price] )
    #energy_prices_data = [ [f"{e.date} {e.time}", e.all_in_price] for e in energyprices]

    context = {
        "energy_prices_data":energy_prices_data,
        "month": month,
        "year": year,
        "month_name": month_name,
    }

    return render(request, 'charts/linechart.html', context)


def year_barchart(request):
    context = {}

    for model, model_name in zip([Energyprice, Gasprice], ["energy", "gas"]):
        avg_by_year = model.objects.filter(country_id="NL").annotate(year=ExtractYear('date')).values('year').annotate(total_price=Avg('purchase_price'))

        # getting data for year chart
        years =  [entry['year'] for entry in list(avg_by_year)]
        year_prices = [round(entry['total_price'], 2) for entry in list(avg_by_year)]
        colors = [generate_random_color() for i in range(len(years))]

        # getting data for month chart
        months_bar_values = {}
        for year in years:
            months_labels = []
            months_values = []
            for month in range(1, 13):
                prices_for_month = model.objects.filter(date__year=year, date__month=month)
                total_price_for_month = prices_for_month.aggregate(total_price=Avg('purchase_price'))['total_price'] or 0
                months_labels.append(MONTHS[month-1])
                months_values.append(round(total_price_for_month, 2))

            months_bar_values[year] = [list(item) for item in list(zip(months_labels, months_values))]

        data = [list(e) for e in list(zip(years, colors, year_prices))]

        ind = 0
        for year in years:
            data[ind].append(months_bar_values[year])
            ind += 1


        context[model_name + "_data"] = data
        context["number_of_years_" + model_name] = len(years)

        if model_name == "gas":
            pprint(data)


    return render(request, 'charts/year_bar_chart.html', context)


def month_barchart(request):
    year = request.GET.get('year', 2023)

    item_spec = []
    for month_number in range(1, 13):
        monthly_data = Energyprice.objects.filter(date__month=month_number, date__year = year, country_id="NL")
        average_value = monthly_data.aggregate(Avg('purchase_price'))['purchase_price__avg']

        if average_value:
            average_value = round(average_value, 2)
            label = MONTHS[month_number-1]
            color = generate_random_color()

            data_for_linechart = []
            for entry in monthly_data:
                data_for_linechart.append([datetime.combine(entry.date, entry.time, tzinfo=timezone.utc).timestamp() * 1000, round(entry.purchase_price, 2)])

            item_spec.append([label, average_value, color, data_for_linechart])



    context = {
        "item_spec": item_spec,
        "year": year,
        "number_of_months": len(item_spec)
    }

    return render(request, 'charts/month_bar_chart.html', context)


def week_barchart(request):
    """ Show clickable barchart
    Todo start the chart always at 2024. Users can go prev year and next year through time
    """

    date = request.GET.get("startOfWeek", None)

    if date:
        start_of_week = datetime.strptime(date, '%Y-%m-%dT%H:%M')
        date_range = [start_of_week + timedelta(days=x) for x in range(0, 7)]
    else:
        current_date = datetime.now()
        current_date = current_date.replace(tzinfo=timezone.utc)
        start_of_week = current_date - timedelta(days=current_date.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        date_range = [start_of_week + timedelta(days=x) for x in range((current_date - start_of_week).days + 1)]

    item_spec = []
    for date in date_range:
        daily_data = Energyprice.objects.filter(date=date, country_id="NL")
        daily_data = daily_data.order_by('time')

        average_value = daily_data.aggregate(Avg('all_in_price'))['all_in_price__avg']
        if average_value:
            # data for bar chart
            average_value = round(average_value, 2)
            label = date.strftime("%A")
            color = generate_random_color()

            # data for linechart
            data_for_linechart = []
            for entry in daily_data:
                data_for_linechart.append([datetime.combine(entry.date, entry.time, tzinfo=timezone.utc).timestamp() * 1000, entry.all_in_price])

            item_spec.append([label, average_value, color, data_for_linechart])

    context = {
        "start_of_week": start_of_week.strftime('%Y-%m-%dT%H:%M'),
        "item_spec": item_spec,
        "number_of_days": len(item_spec),
    }

    print(start_of_week.strftime('%Y-%m-%dT%H:%M'))
    return render(request, 'charts/week_bar_chart.html', context)  # todo make own html page