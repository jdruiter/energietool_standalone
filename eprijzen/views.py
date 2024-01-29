from datetime import date, datetime, timedelta
from django.shortcuts import render, HttpResponse, render
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.mail import send_mail
import requests
import json

from eprijzen.models import Energyprice, Gasprice

import logging
logger = logging.getLogger('eprijzen')
apilogger = logging.getLogger('api-results')


def show_energyprices_nl(request):
    """ Show energy and gas prices for NL """

    context = {}
    period = request.GET['period']
    if not period:
        return render(request, 'eprijzen/eprijzen.html', context)

    print(period)

    energyprices = Energyprice.objects.all()
    gasprices = Gasprice.objects.all()
    if period == 'today':
        energyprices = energyprices.filter(date=date.today())
        gasprices = gasprices.filter(date=date.today())
    elif period == 'tomorrow':
        energyprices = energyprices.filter(date=date.today()+timedelta(days=1))
        gasprices = gasprices.filter(date=date.today()+timedelta(days=1))
    elif period == 'yesterday':
        energyprices = energyprices.filter(date=date.today()-timedelta(days=1))
        gasprices = gasprices.filter(date=date.today()-timedelta(days=1))
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



"""
API_SECRET_STRING = 'updatedb11'
 
def update_period(request, secretstring, periode):
    # Makes API call to update the database

    if secretstring != API_SECRET_STRING: 
        return HttpResponse("Give the right secret string to update the database")

    vandaag = date.today()
    morgen = date.today() + timedelta(days=1)
    gisteren = date.today() - timedelta(days=1)
    vorige_week = date.today() - timedelta(days=7)
    vorige_maand = date.today() - timedelta(days=31)

    if not periode:
        return HttpResponse("Give period: today|tomorrow|yesterday|prev_week|prev_month")
    elif periode == 'today':
        api_update_energieprijzen(vandaag, vandaag)
    elif periode == 'tomorrow':
        api_update_energieprijzen(morgen, morgen)
    elif periode == 'yesterday':
        api_update_energieprijzen(gisteren, gisteren)
    elif periode == 'prev_week':
        api_update_energieprijzen(vorige_week, vandaag)
    elif periode == 'prev_month':
        api_update_energieprijzen(vorige_maand, vandaag)


def api_update_prices(request, secretstring, fromdate, todate):
    # API get prices of (fromdate, todate)
    # eprijs.nl/secretstring/update_price/01-01-2023/31-01-2023/
    
    if secretstring != API_SECRET_STRING: 
        return HttpResponse("Give the right secret string to update the database")
    
    start = datetime.strptime(fromdate, '%Y-%m-%d')
    end   = datetime.strptime(todate,   '%Y-%m-%d')

    if start.year != end.year:
        return HttpResponse("Max 365 days in same year")

    api_update_energieprijzen(start, end)



def api_update_energieprijzen(fromdate, todate):
    # Does the actual API request to eprijzen.nl api for specific dates, to update database
    # fromdate, todate format: 2023-12-31

    print("From: " + str(fromdate))
    print("To: " + str(todate))

    params = {
        "user_id": "545589145",
        "api_key": "45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc",
        "country": "NL",
        "date": fromdate,
        "todate": todate
    }
    res = requests.get('https://api.energieprijzenbot.nl/energy/api/v1.0/ha', params=params)

    result = res.json()
    if result.get('message') != 'Success':
        return HttpResponse("{} {}".format(res.status_code, result.get('message')))

    data = result.get('data')

    ''' Write to file (debug) '''
    # toon hoogste en laagste prijs van de dag
    filename = 'json/' + str(fromdate) + '.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(data))

    ''' Start the parsing '''
    energy = result.get('data').get('e')
    gas = result.get('data').get('g')

    for e in energy:
        day = e.get('datetime')
        date = day.split('T')[0]
        time = day.split('T')[1]
        purchase_price = e.get('purchase_price')
        extra_fee_price = e.get('extra_fee_price')
        all_in_price = e.get('all_in_price')
        obj, created = Energyprice.objects.update_or_create(country_id='NL', date=date, time=time,
                                                               defaults={'purchase_price': round(purchase_price, 4),
                                                                         'extra_fee_price': round(extra_fee_price, 4),
                                                                         'all_in_price': round(all_in_price, 4)})
        status = 'new' if created else 'updated'
        apilogger.info("{} {}".format(status, str(obj)))

    for g in gas:
        day = g.get('datetime')
        date = day.split('T')[0]
        time = day.split('T')[1]
        purchase_price = g.get('purchase_price')
        extra_fee_price = g.get('extra_fee_price')
        all_in_price = g.get('all_in_price')
        obj, created = Gasprice.objects.update_or_create(country_id='NL', date=date, time=time,
                                                           defaults={'purchase_price': round(purchase_price, 4),
                                                                     'extra_fee_price': round(extra_fee_price, 4),
                                                                     'all_in_price': round(all_in_price, 4)})
        status = 'new' if created else 'updated'
        apilogger.info("{} {}".format(status, str(obj)))

    print(json.dumps(res, indent=4, sort_keys=True))

"""