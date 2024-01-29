# Energytool-NL

# /admin/
login: nazar
pw: nazar

# TODO
1. Check if the data in EnergyPrice and GasPrice tables are complete: every day and every hour should be present
2. You can get years 2017-2021 into the database from files energieprijzen.csv and gasprijzen.csv (inside folder _import)
   (Hint: use django-import-export) and chop import files into small pieces of max 500 rows
3. Check the files inside management/commands/ and run some commands to test the API
4. See the TODO's in views.py: now the real work starts!


# Info
Prijzen: 
* purchase_price = kale inkoop prijs
* extra_fee_price is de inkoopprijs met daarbij de door jouw ingesteld (in telegram) inkoopvergoeding en BTW (2022 9% 2022, 2023 21%)
* all_in_price = inkoopprijs + inkoopvergoeding en ODE + EnergieBelasting (EB) en BTW
`
*Opslag* bij dynamische energieleveranciers is een toeslag bovenop de kostprijs van energie. Het is een manier voor leveranciers om de prijsschommelingen en risico’s die gepaard gaan met de inkoop van energie op de 
markt te dekken. Dit bedrag kan variëren afhankelijk van de marktsituatie en het beleid van de leverancier.

*Vastrecht* is een vast bedrag dat u per maand betaalt aan uw energieleverancier. Dit bedrag dekt de administratieve kosten van de leverancier en blijft over het algemeen constant, ongeacht uw energieverbruik. Het 
vastrecht kan per leverancier verschillen en is een belangrijke factor bij het kiezen van een energiecontract.