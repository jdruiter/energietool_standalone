import sys, os, json
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from pprint import pprint
import requests

from eprijzen.models import Energyprice, Gasprice
import logging
logger = logging.getLogger('management-commands')

"""Telegram eprijzen bot:
@knightpoint: 545589145
API key: 45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc
@nazar: 424718795
API key: 9f8ff82d85848a5d4002b102aaefa70d46feea779297d29fb927e61797f84f29b775188b07b56f21d83e0920b2c4b35f
"""

class Command(BaseCommand):
    API_USER_ID = "424718795"
    API_KEY = "9f8ff82d85848a5d4002b102aaefa70d46feea779297d29fb927e61797f84f29b775188b07b56f21d83e0920b2c4b35f"

    help = 'Update energy and gas price tables' \
           'Electricity prices available from 2017,' \
           'Gas prices available from 2018 (only NL).' \
           'python manage.py update_prices -c NL -p today|3day|last_week|last_month' \
           'python manage.py update_prices -c NL --start 2024-01-01 --end 2024-01-31  (YYYY-MM-DD)'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--period', type=str, help="Period: today|3day|last_week|last_month")
        parser.add_argument('-c', '--country', type=str, default='NL', help="Country (default NL")
        parser.add_argument('-s', '--start', type=str, help="Start date (2024-01-01)")
        parser.add_argument('-e', '--end',   type=str, help="End date (2024-01-31)")

    def handle(self, *args, **options):

        country = options['country'].upper() or 'NL'
        period = options['period']
        start = options['start'] or None
        end = options['end'] or None

        today = datetime.now()
        date, todate = None, None
        if start and end:
            date, todate = start, end

        elif period:

            if period == 'today':
                date = today.strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

            elif period == '3day':
                date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
                todate = (today + timedelta(days=1)).strftime('%Y-%m-%d')

            elif period == 'last_week':
                date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

            elif period == 'last_month':
                date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
                todate = today.strftime('%Y-%m-%d')

        if not (date and todate):
            return "Give a period, or a start and end date. \nFor help, use python manage.py update_prices -h"

        print("From: " + date)
        print("To:   " + todate)

        params = {
            "user_id": self.API_USER_ID,
            "api_key": self.API_KEY,
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
            obj, created = Energyprice.objects.update_or_create(country_id=country, date=date, time=time,
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

            obj, created = Gasprice.objects.update_or_create(country_id='NL', date=date, time=time,
                                                               defaults={'purchase_price': round(purchase_price, 4),
                                                                         'extra_fee_price': round(extra_fee_price, 4),
                                                                         'all_in_price': round(all_in_price, 4) } )
            status = 'new' if created else 'updated'
            print(f"Gas: {date} {time}  {purchase_price:2f}  ({status} in db)")