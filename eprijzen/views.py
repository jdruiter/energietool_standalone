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
    period = request.GET.get('period')
    if not period:
        return render(request, 'eprijzen/eprijzen.html', context)

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