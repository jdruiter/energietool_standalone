import sys, os, json
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from pprint import pprint
import requests

from eprijzen.models import Energyprice, Gasprice, EnergypriceEurope, GaspriceEurope
import logging
logger = logging.getLogger('management-commands')

"""Telegram:
@knightpoint: 545589145
API key: 45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc
740 API tokens
"""

class Command(BaseCommand):

    help = 'Update energy and gas price tables' \
           'Electricity prices available from 2017,' \
           'Gas prices available from 2018 (only NL).' \
           'python manage.py update_prices -c NL -p today|3day|prev_week|prev_month' \
           'python manage.py update_prices -c NL --start 2024-01-01 --end 2024-01-31  (YYYY-MM-DD)'

    def add_arguments(self, parser):
        parser.add_argument('period', nargs='?', type=str, help="Period: today|3day|prev_week|prev_month")
        # parser.add_argument('-p', '--period', type=str, help="Period: today|3day|prev_week|prev_month")
        parser.add_argument('-c', '--country', type=str, default='NL', help="Country (default NL")
        parser.add_argument('-s', '--start', type=str, help="Start date (2024-01-01)")
        parser.add_argument('-e', '--end',   type=str, help="End date (2024-01-31)")

    def handle(self, *args, **options):

        country = options['country'] or 'NL'
        period = options['period']
        start = options['start']
        end = options['end']

        today = datetime.now()

        if start and end:
            date, todate = start, end

        elif start:
            date, todate = start, start

        elif period:

            if period == 'today':
                date = today.strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

            elif period == '3day':
                date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
                todate = (today + timedelta(days=1)).strftime('%Y-%m-%d')

            elif period == 'prev_week':
                date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

            elif period == 'prev_month':
                date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

            else:
                return print("Need a valid period for the query")

        print("From: " + date)
        print("To: " + todate)

        params = {
            "user_id": "545589145",
            "api_key": "04de0f863ecc9f16c22bb4e3356876322079549aabf62ca9c5605b89596e362a616295543d9177afd7cce40afc0a4b4e",
            "country": country,
            "date": date,
            "todate": todate
        }
        result = requests.get('https://api.energieprijzenbot.nl/energy/api/v1.0/ha', params=params)

        res = result.json()
        if res.get('message') != 'Success':
            print("{} {}".format(result.status_code, res.get('message')))
            sys.exit()

        ''' Write to file (debug) '''
        # data = res.get('data')
        # filename = '_json/'+str(date)+'.json'
        # with open(filename, 'w') as f:
        #     f.write(json.dumps(data))

        ''' Start the parsing '''
        energy = res.get('data').get('e')
        gas = res.get('data').get('g')

        for e in energy:
            day = e.get('datetime')
            date = day.split('T')[0]        # 2023-03-10
            time = day.split('T')[1][:5]    # 10:00  (db has time 10:00, json gives 10:00:00)
            purchase_price = e.get('purchase_price')
            extra_fee_price = e.get('extra_fee_price')
            all_in_price = e.get('all_in_price')
            if country == 'NL':
                obj, created = Energyprice.objects.update_or_create(country_id='NL', date=date, time=time,
                                                                       defaults={'purchase_price': round(purchase_price, 4),
                                                                                 'extra_fee_price': round(extra_fee_price, 4),
                                                                                 'all_in_price': round(all_in_price, 4) } )
            else:
                obj, created = EnergypriceEurope.objects.update_or_create(country_id=country, date=date, time=time,
                                                                       defaults={'purchase_price': round(purchase_price, 4),
                                                                                 'extra_fee_price': round(extra_fee_price, 4),
                                                                                 'all_in_price': round(all_in_price, 4) } )
            status = 'new' if created else 'updated'
            print(f"Energie: {date} {time}  {purchase_price:2f} ({status} in db)")


        for g in gas:
            day = g.get('datetime')
            date = day.split('T')[0]
            time = day.split('T')[1][:5]  #10:00
            purchase_price = g.get('purchase_price')
            extra_fee_price = g.get('extra_fee_price')
            all_in_price = g.get('all_in_price')

            if country == 'NL':
                obj, created = Gasprice.objects.update_or_create(country_id='NL', date=date, time=time,
                                                                   defaults={'purchase_price': round(purchase_price, 4),
                                                                             'extra_fee_price': round(extra_fee_price, 4),
                                                                             'all_in_price': round(all_in_price, 4) } )
            else:
                obj, created = GaspriceEurope.objects.update_or_create(country_id=country, date=date, time=time,
                                                                 defaults={'purchase_price': round(purchase_price, 4),
                                                                           'extra_fee_price': round(extra_fee_price, 4),
                                                                           'all_in_price': round(all_in_price, 4)})

            status = 'new' if created else 'updated'
            print(f"Gas: {date} {time}  {purchase_price:2f}  ({status} in db)")