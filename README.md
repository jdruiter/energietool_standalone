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