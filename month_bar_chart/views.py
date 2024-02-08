from django.shortcuts import render
from eprijzen.models import Energyprice
from datetime import datetime, timedelta
from django.db.models import Avg
import random

from pprint import pprint

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def generate_random_color():
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return color

def plot_graph(request):
    year = request.GET.get('year')
    if not year:
        year = 2022

    item_spec = []
    for month_number in range(1, 13):
        monthly_data = Energyprice.objects.filter(date__month=month_number, date__year = year, country_id="NL")
        average_value = monthly_data.aggregate(Avg('purchase_price'))['purchase_price__avg']
        label = months[month_number-1]
        color = generate_random_color()

        data_for_linechart = []
        for entry in monthly_data:
            data_for_linechart.append([datetime.combine(entry.date, entry.time).timestamp() * 1000, round(entry.purchase_price, 2)])

        item_spec.append([label, average_value, color, data_for_linechart])

    context = {
        "item_spec": item_spec,
        "year": year
    }


    # Old code for week bar chart visualization
    """
    current_date = datetime(2022, 8, 27)
    start_of_week = current_date - timedelta(days=6)
    date_range = [start_of_week + timedelta(days=x) for x in range(0, 7)]

    item_spec = []
    for date in date_range:
        daily_data = Energyprice.objects.filter(date=date, country_id = "NL")
        daily_data = daily_data.order_by('time')

        # data for bar chart
        average_value = daily_data.aggregate(Avg('purchase_price'))['purchase_price__avg']
        label = date.strftime("%d.%m.%Y")
        color = generate_random_color()

        # data for linechart
        data_for_linechart = []
        for entry in daily_data:
            data_for_linechart.append([datetime.combine(entry.date, entry.time).timestamp()*1000, entry.purchase_price])


        item_spec.append([label, average_value, color, data_for_linechart])

    context = {
        "item_spec": item_spec
    }
"""
    return render(request, 'charts/month_bar_chart.html', context)