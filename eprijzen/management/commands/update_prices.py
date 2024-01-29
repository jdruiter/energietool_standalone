import sys, os, json
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from pprint import pprint
import requests

from eprijzen.models import EnergyPrice, GasPrice
import logging
logger = logging.getLogger('management-commands')

"""Telegram:
@knightpoint: 545589145
API key: 45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc
740 API tokens
"""

class Command(BaseCommand):

    help = 'Update energy and gas price tables' \
           'Electricity prices available from 2017' \
           'Gas prices available from 2018 (only NL)' \
           'python manage.py update_prices --period today|tomorrow|yesterday|prev_week|prev_month' \
           'python manage.py update_prices --start 2024-01-01 --end 2024-01-31  (YYYY-MM-DD)' \
           'python manage.py update_prices -c NL -p today' \

    def add_arguments(self, parser):
        # parser.add_argument('positional_arg', type=int)
        parser.add_argument('-s', '--start', type=str, help="Start date (2024-01-01)")
        parser.add_argument('-e', '--end',   type=str, help="End date (2024-01-31)")
        parser.add_argument('-p', '--period', type=str, help="Period: today|tomorrow|yesterday|prev_week|prev_month")
        parser.add_argument('-c', '--country', type=str, default='NL', help="Country (default NL")

    def handle(self, *args, **options):

        period = options['period']
        start = options['start']
        end = options['end']
        country = options['country'] or 'NL'

        today = datetime.now()
        date = today
        todate = today

        if start and end:
            date = start
            todate = end

        elif start and not end:
            date = start
            todate = start

        elif period:

            if period == 'today':
                date = today.strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

            elif period == 'morgen':
                morgen = today + timedelta(days=1)
                date = morgen.strftime('%Y-%m-%d')
                todate = morgen.strftime('%Y-%m-%d')

            elif period == 'gisteren':
                gisteren = today - timedelta(days=1)
                date = gisteren.strftime('%Y-%m-%d')
                todate = gisteren.strftime('%Y-%m-%d')

            elif period == 'vorige_week':
                begin = today - timedelta(days=7)
                date = begin.strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

            elif period == 'vorige_maand':
                begin = today - timedelta(days=30)
                date = begin.strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

        else:
            return print("Need a start and end date to do the query")


        print("From: " + str(date))
        print("To: " + str(todate))

        params = {
            "user_id": "545589145",
            "api_key": "45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc",
            "country": country,
            "date": date,
            "todate": todate
        }
        result = requests.get('https://api.energieprijzenbot.nl/energy/api/v1.0/ha', params=params)

        res = result.json()
        if res.get('message') != 'Success':
            print("{} {}".format(result.status_code, res.get('message')))
            sys.exit()

        data = res.get('data')

        ''' Write to file (debug) '''
        filename = '_json/'+str(date)+'.json'
        with open(filename, 'w') as f:
            f.write(json.dumps(data))

        ''' Start the parsing '''
        energy = res.get('data').get('e')
        gas = res.get('data').get('g')

        print("Energie inkoopprijs:")
        for e in energy:
            # db has time 10:00, json gives 10:00:00
            # date = datetime.strptime(day.split('T')[0], '%Y-%m-%d')
            # time = datetime.strptime(day.split('T')[1], '%H:%M:%S').time()
            day = e.get('datetime')
            date = day.split('T')[0]        # 2023-03-10
            time = day.split('T')[1][:5]    # 10:00
            purchase_price = e.get('purchase_price')
            extra_fee_price = e.get('extra_fee_price')
            all_in_price = e.get('all_in_price')
            obj, created = EnergyPrice.objects.update_or_create(country_id='NL', date=date, time=time,
                                                                   defaults={'purchase_price': round(purchase_price, 4),
                                                                             'extra_fee_price': round(extra_fee_price, 4),
                                                                             'all_in_price': round(all_in_price, 4) } )
            status = 'new' if created else 'updated'
            print(f"Energie: {date} {time}  {purchase_price:2f} ({status} in db)")

        print("\nGas inkoopprijs:")
        for g in gas:
            day = g.get('datetime')
            date = day.split('T')[0]
            time = day.split('T')[1][:5]  #10:00
            purchase_price = g.get('purchase_price')
            extra_fee_price = g.get('extra_fee_price')
            all_in_price = g.get('all_in_price')

            obj, created = GasPrice.objects.update_or_create(country_id='NL', date=date, time=time,
                                                                   defaults={'purchase_price': round(purchase_price, 4),
                                                                             'extra_fee_price': round(extra_fee_price, 4),
                                                                             'all_in_price': round(all_in_price, 4) } )
            status = 'new' if created else 'updated'
            print(f"Gas: {date} {time}  {purchase_price:2f}  ({status} in db)")