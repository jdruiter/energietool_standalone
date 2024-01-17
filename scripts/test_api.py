import sys
import json
import requests
from datetime import datetime, timedelta
from pprint import pprint

"""
# You get one full day per request: 00:00 - 23:00, only NL
# Datum format: YYYY-MM-DD

$ purchase_price = kale inkoop prijs
$ extra_fee_price is de inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (nu 9% 2022 en 2023 21%)
$ all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW (nu 9% 2022 en 2023 21%)
Historische data in de database is de purchase_price

"""


params = {"user_id": "545589145", "api_key":"45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc", "country":"NL", "date": "2023-03-08", "todate": "2023-03-08"}
result = requests.get('https://api.energieprijzenbot.nl/energy/api/v1.0/ha', params=params)
data = result.json().get('data')
# pprint(data.get('e'))

f = open('output.json', 'w')
f.write(json.dumps(data))
f.close()

energieprijzen = data.get('e')
print("EnergyPrice:")
for day in energieprijzen:
    print("{}  {}".format( day.get('datetime'), day.get('purchase_price')))

print("\nGasPrice")
gasprijzen = data.get('g')
for day in gasprijzen:
    print("{}  {}".format( day.get('datetime'), day.get('purchase_price')))