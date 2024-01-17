"""Telegram:
@knightpoint: 545589145
API key: 45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc
740 API tokens
login with userid en api key
"""
import sys, os, json

'''
# Go parse the file
# You get one full day per request: 00:00 - 23:00   (only NL)

$ purchase_price = kale inkoop prijs
$ extra_fee_price is de inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (nu 9% 2022 en 2023 21%)
$ all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW (nu 9% 2022 en 2023 21%)

'''

f = open('output/prijzen_1day.json', 'r')
res = json.loads(f.read())
print(res.get('message'))

energy = res.get('data').get('e')
gas = res.get('data').get('g')

for e in energy:
    day = e.get('datetime')
    date = day.split('T')[0]
    time = day.split('T')[1]
    inkoopprijs = e.get('purchase_price')
    extra_fee_price = e.get('extra_fee_price')
    all_in_price = e.get('all_in_price')
    print(f"Energie: {date} {time}  {all_in_price}")

for g in gas:
    day = g.get('datetime')
    date = day.split('T')[0]
    time = day.split('T')[1]
    inkoopprijs = g.get('purchase_price')
    extra_fee_price = g.get('extra_fee_price')
    all_in_price = g.get('all_in_price')
    print(f"Gas: {day}: {all_in_price}")


f.close()