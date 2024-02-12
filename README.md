# Energytool-NL

A web app with beautiful charts of energy prices in the Netherlands.

* Live energy prices
* Live gas prices
* Historical energy prices in graphs
* Historical gas prices in charts


## How to use

Create a virtualenv and install the python packages
`$ pip install -r requirements.txt`

The given sqlite database is used as database. Connection settings are in settings.py
Change settings.py as needed. 

Run the server:
`python manage.py runserver`

See your webpage on http://localhost:8000

To update the prices, use:
`$ python manage.py update_prices --start 2024-01-01 --end 2024-01-31`
Changes dates as needed (YYYY-MM-DD).

The script that calls the API with energypries is in /eprijzen/management/commands/update_prices.py


## Get live energy prices on your phone

1. Install Telegram
2. Connect to eprijzen bot: https://eprijzen.nl/project/telegram/
3. Get an account with /a

```example telegram commands:
/nu 
/vandaag
/morgen
/verleden a 2022-05-14
```


## Build your own

The Telegram bot is used to control the API that gives energy prices.

Use the Telegram bot to: 
1. Renew API key 
2. change price settings (incl/ecxl tax) 

```
/i
/i help 
/api 
/api_key   #nieuwe 

/sp k   #kale prijzen 
/sp o   #met opslag
/sp a 	# all in prijzen (inkoop+opslag+ode+eb+btw)
/sp help 
/instellingen 
```


# Info (NL)

* purchase_price = kale inkoop prijs
* extra_fee_price = kale inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (2022 9% 2022, 2023 21%)
* all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW (nu 9% 2022 en 2023 21%)

*Opslag* bij dynamische energieleveranciers is een toeslag bovenop de kostprijs van energie. Het is een manier voor leveranciers om de prijsschommelingen en risico’s die gepaard gaan met de inkoop van energie op de 
markt te dekken. Dit bedrag kan variëren afhankelijk van de marktsituatie en het beleid van de leverancier.

*Vastrecht* is een vast bedrag dat u per maand betaalt aan uw energieleverancier. Dit bedrag dekt de administratieve kosten van de leverancier en blijft over het algemeen constant, ongeacht uw energieverbruik. Het 
vastrecht kan per leverancier verschillen en is een belangrijke factor bij het kiezen van een energiecontract.


# Info (EN)
* purchase_price = what energy company pays
* extra_fee_price = price + taxes
* all_in_price = price + taxes + more taxes  (what consumers will pay)