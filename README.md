# Energytool-NL

## API - Get (fresh and historical) prices from API eprijzen.nl:
```
params = { "user_id": "545589145", "api_key": "45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc", "country": "NL"}
params = {
    "user_id": "545589145",
    "api_key": "45ccecb17449e0bfbfbca8c2b6342db63a6a12fd37dcfb18095ba40409a8a926f286390058efd185978e0ee377b733cc",
    "country": "NL",        # NL only
    "date": "2023-03-01",   #YYYY-MM-DD
    "todate": "2023-03-02", #YYYY-MM-DD
}
res = requests.get('https://api.energieprijzenbot.nl/energy/api/v1.0/ha', params=params).json()
```

Use /eprijzen/management/commands/update_prijzen.py to call this api:
$ python manage.py update_prijzen --start 2024-01-17 --end 2024-01-29


## API Telegram bot
https://eprijzen.nl/project/telegram/

Use Telegram bot to: 
1. Renew API key 
2. change price settings (incl/ecxl tax) 

/i
/i help 
/api 
/api_key   #nieuwe 

/sp k   #kale prijzen 
/sp o   #met opslag
/sp a 	# all in prijzen (inkoop+opslag+ode+eb+btw)
/sp help 
/nu 
/vandaag
/morgen
/verleden a 2022-05-14
/instellingen 

purchase_price = kale inkoop prijs
extra_fee_price is de inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (nu 9% 2022 en 2023 21%)
all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW (nu 9% 2022 en 2023 21%)




# localhost:8000/admin/
user: nazar, pw nazar
$python manage.py changepassword
$python manage.py createsuperuser

# TODO
1. Check if the data in Energyprice and Gasprice tables are complete: every day and every hour should be present
2. Check the files inside management/commands/ and run some commands to test the API


# Info (NL)
Prijzen: 
* purchase_price = kale inkoop prijs
* extra_fee_price = kale inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (2022 9% 2022, 2023 21%)
* all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW
`
*Opslag* bij dynamische energieleveranciers is een toeslag bovenop de kostprijs van energie. Het is een manier voor leveranciers om de prijsschommelingen en risico’s die gepaard gaan met de inkoop van energie op de 
markt te dekken. Dit bedrag kan variëren afhankelijk van de marktsituatie en het beleid van de leverancier.

*Vastrecht* is een vast bedrag dat u per maand betaalt aan uw energieleverancier. Dit bedrag dekt de administratieve kosten van de leverancier en blijft over het algemeen constant, ongeacht uw energieverbruik. Het 
vastrecht kan per leverancier verschillen en is een belangrijke factor bij het kiezen van een energiecontract.