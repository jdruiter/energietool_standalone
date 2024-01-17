import requests
from datetime import datetime, timedelta
import csv

"""
Frank energie GraphQL
API is quite unstable, changes a lot 
Writes to CSV

"""


def FrankEnergy():
    now = datetime.now()
    yesterday = datetime.now() + timedelta(days=-1)
    tomorrow = datetime.now() + timedelta(days=1)
    startdate = yesterday.strftime("%Y-%m-%d")
    enddate = now.strftime("%Y-%m-%d")

    if int(now.strftime("%H")) > 15:
        tomorrow = datetime.now() + timedelta(days=2)
        startdate = now.strftime("%Y-%m-%d")
        enddate = tomorrow.strftime("%Y-%m-%d")

    headers = {"content-type": "application/json"}

    query = {
        "query": """
                    query MarketPrices($startDate: Date!, $endDate: Date!) {
                        marketPricesElectricity(startDate: $startDate, endDate: $endDate) {
                            from till marketPrice marketPriceTax sourcingMarkupPrice energyTaxPrice
                        }
                        marketPricesGas(startDate: $startDate, endDate: $endDate) {
                            from till marketPrice marketPriceTax sourcingMarkupPrice energyTaxPrice
                        }
                    }
                """,
        "variables": {"startDate": str(startdate), "endDate": str(enddate)},
        "operationName": "MarketPrices"
    }

    response = requests.post('https://frank-graphql-prod.graphcdn.app', json=query)
    data = response.json()

    frank_electra_file = "frank_electra.csv"
    frank_gas_file = "frank_gas.csv"

    frank_headers = ['till', 'from', 'marketPrice', 'priceIncludingMarkup']

    with open(frank_electra_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=frank_headers)
        writer.writeheader()
        writer.writerows(data['data']['marketPricesElectricity'])

    with open(frank_gas_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=frank_headers)
        writer.writeheader()
        writer.writerows(data['data']['marketPricesGas'])

    for electra in data['data']['marketPricesElectricity']:
        print(electra['till'], electra['from'], electra['marketPrice'], electra['priceIncludingMarkup'])

    for gas in data['data']['marketPricesGas']:
        print(gas['till'], gas['from'], gas['marketPrice'], gas['priceIncludingMarkup'])


if __name__ == "__main__":
    FrankEnergy()
