from django.shortcuts import render
from eprijzen.models import Energyprice
from datetime import datetime
from django.db.models import Sum
from django.db.models.functions import ExtractYear

import random
from pprint import pprint

# month labels for the month bar chart
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# random color function
def generate_random_color():
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return color

def plot_chart(request):
    sum_by_year = Energyprice.objects.filter(country_id="NL").annotate(year=ExtractYear('date')).values('year').annotate(total_price=Sum('purchase_price'))

    # getting data for year chart
    years =  [entry['year'] for entry in list(sum_by_year)]
    year_prices = [entry['total_price'] for entry in list(sum_by_year)]
    colors = [generate_random_color() for i in range(len(years))]

    # getting data for month chart
    months_bar_values = {}
    for year in years:
        months_labels = []
        months_values = []
        for month in range(1, 13):
            prices_for_month = Energyprice.objects.filter(date__year=year, date__month=month)
            total_price_for_month = prices_for_month.aggregate(total_price=Sum('purchase_price'))['total_price'] or 0
            months_labels.append(months[month-1])
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