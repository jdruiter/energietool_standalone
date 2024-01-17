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

""" Example:
params = { "user_id": "545589145", "api_key": "45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc", "country": "NL"}
params = {
    "user_id": "545589145",
    "api_key": "45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc",
    "country": "NL",        # NL only
    "date": "2023-03-01",   #YYYY-MM-DD
    "todate": "2023-03-02", #YYYY-MM-DD
}
res = requests.get('https://api.energieprijzenbot.nl/energy/api/v1.0/ha', params=params).json()
"""

class Command(BaseCommand):

    help = 'Update energy and gas price tables (NL)' \
           'python manage.py update_prijzen --periode vandaag|gisteren|morgen|vorige_week|vorige_maand' \
           'python manage.py update_prijzen --start 2020-01-01 --eind 2020-01-03   (YYYY-MM-DD)'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start', type=str, help="Start datum (2020-12-01)")
        parser.add_argument('-e', '--eind', type=str, help="Eind datum (2020-12-31)")
        parser.add_argument('-p', '--periode', type=str, help="Periode: vandaag|morgen|gisteren|vorige_week|vorige_maand")


    def handle(self, *args, **options):

        periode = options['periode']
        start = options['start']
        eind = options['eind']

        vandaag = datetime.now()
        date = vandaag
        todate = vandaag

        if start and eind:
            date = start
            todate = eind

        elif start and not eind:
            date = start
            todate = start

        elif periode:

            if periode == 'vandaag':
                date = vandaag.strftime('%Y-%m-%d')
                todate = vandaag.strftime('%Y-%m-%d')

            elif periode == 'morgen':
                morgen = vandaag + timedelta(days=1)
                date = morgen.strftime('%Y-%m-%d')
                todate = morgen.strftime('%Y-%m-%d')

            elif periode == 'gisteren':
                gisteren = vandaag - timedelta(days=1)
                date = gisteren.strftime('%Y-%m-%d')
                todate = gisteren.strftime('%Y-%m-%d')

            elif periode == 'vorige_week':
                begin = vandaag - timedelta(days=7)
                date = begin.strftime('%Y-%m-%d')
                todate = vandaag.strftime('%Y-%m-%d')

            elif periode == 'vorige_maand':
                begin = vandaag - timedelta(days=30)
                date = begin.strftime('%Y-%m-%d')
                todate = vandaag.strftime('%Y-%m-%d')

        else:
            return print("Need a start and end date to do the query")


        print("From: " + str(date))
        print("To: " + str(todate))

        params = {
            "user_id": "545589145",
            "api_key": "45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc",
            "country": "NL",
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
            # bug: update_or_create and filter() does not find, will insert a new row regardless
            # date2 = datetime.strptime(day.split('T')[0], '%Y-%m-%d')
            # time2 = datetime.strptime(day.split('T')[1], '%H:%M:%S').time()
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