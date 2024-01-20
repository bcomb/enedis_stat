import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

region_utc = 'Europe/Paris'

data_path = 'data/2023/'
enedis_consumption_file = data_path + 'enedis-hours.csv'   # per hours (or better) format !
price_file= data_path + 'price.csv'                        # price for bleu/vert/tempo
hchp_file= data_path + 'hchp.csv'                          # hp/hc timerange info
tempo_calendar_file= data_path + 'tempo_calendar.csv'      # BLEU/ROUGE/BLANC tempo day

        # Read CSV file with date and avg_consumption columns
data = pd.read_csv(enedis_consumption_file, sep=';', header=None, names=['date', 'avg_consumption'])
#data = pd.read_csv(os.path.join(script_dir, csv_file), sep=';', header=None, names=['date', 'avg_consumption']))

# Ensure the 'date' column is in datetime format with he desired UTC
data['date'] = pd.to_datetime(data['date'], utc=True)
data['date'] = data['date'].dt.tz_convert(region_utc)

# print row data contain invalid data in any column
invalid_entries = data[data.isnull().any(axis=1)]
if not invalid_entries.empty:
    print("[Warning] Contain some invalid entries:")
    print(invalid_entries)

# Replace missing avg_consumptions with 0
data.fillna(0, inplace=True)

# In the per hours enedis dataset, the avg_consumption represent the average consumption for the period
# Compute period of the avg_consumption (for the frist entry consider it's the same as the second)
data['period'] = data['date'] - data['date'].shift(1)
data.loc[0, 'period'] = data.loc[1, 'period']

# Compute the real comsumption for the period
data['consumption'] = data['avg_consumption'] * data['period'].dt.total_seconds() / 3600

####
# HCHP (Heure Creuse Heure Pleine)
####

# Determine hchp
hchp = pd.read_csv(hchp_file, sep=';')
# Return hc or hp depending of timerange of hchtable
def check_time_ranges(date, hchp):
    time = date.strftime('%H:%M:%S')
    for i in range(len(hchp)):
        min_time = hchp.iloc[i, 0]
        max_time = hchp.iloc[i, 1]
        if min_time <= time <= max_time:
            return 'hc'
    return 'hp'
data['hchp'] = data['date'].apply(lambda x: check_time_ranges(x, hchp))

####
# TEMPO COLOR
####

# THIS IS THE TIME CONSUMING PART (A day optimize that...)
# O(n^2) !!!
# Determining the color for tempo
tempo_calendar = pd.read_csv(tempo_calendar_file, sep=';')

def check_tempo_calendar(date, tempo_calendar):
    day = date.strftime('%Y-%m-%d') # date formatted as 2023-01-01
    for i in range(len(tempo_calendar)):
        if day == tempo_calendar.iloc[i, 0]:
            return tempo_calendar.iloc[i, 1]
    return 'unknown'

data['tempo_color'] = data['date'].apply(lambda x: check_tempo_calendar(x, tempo_calendar))

# Check for unknown in order to inform
unknowns = data[data['tempo_color'] == 'unknown']
if not unknowns.empty:
    print("[Warning] Unknown tempo color:")
    print(unknowns)

####
# PRICING
####
            
# Read price
price = pd.read_csv(price_file, sep=';')

def get_price(offer, type):
    return price.loc[price['offer'] == offer, type].values[0]

# Compute blue price
base_price = price.loc[price['offer'] == 'bleu', 'base'].values[0]
data['price_bleu'] = data['consumption'] / 1000.0 * base_price

# Compute vert price
base_price = price.loc[price['offer'] == 'vert', 'base'].values[0]
data['price_vert'] = data['consumption'] / 1000.0 * base_price

def compute_price_hphc(row, price_hchp):
    return price_hchp[row['hchp']] * row['consumption'] / 1000.0

# Compute blue_hphc price
price_hchp = { 'hc' : get_price('bleu','hc'), 'hp' : get_price('bleu','hp') }
data['price_bleu_hchp'] = data.apply(lambda row: compute_price_hphc(row, price_hchp), axis=1)

# Compute vert_hphc price
price_hchp = { 'hc' : get_price('vert','hc'), 'hp' : get_price('vert','hp') }
data['price_vert_hchp'] = data.apply(lambda row: compute_price_hphc(row, price_hchp), axis=1)

def compute_price_tempo_hphc(row, price_tempo_hphc):
    return price_tempo_hphc[ row['tempo_color'] ][ row['hchp'] ] * row['consumption'] / 1000.0

price_tempo_hphc = {}                                          
price_tempo_hphc['BLEU'] = { 'hc' : get_price('tempo_bleu','hc'), 'hp' : get_price('tempo_bleu','hp') }
price_tempo_hphc['ROUGE'] = { 'hc' : get_price('tempo_rouge','hc'), 'hp' : get_price('tempo_rouge','hp') }
price_tempo_hphc['BLANC'] = { 'hc' : get_price('tempo_blanc','hc'), 'hp' : get_price('tempo_blanc','hp') }
price_tempo_hphc['unknown'] = price_tempo_hphc['BLEU']

data['price_tempo_hphc'] = data.apply(lambda row: compute_price_tempo_hphc(row, price_tempo_hphc), axis=1)

# consumption_by_month = data.groupby(data['date'].dt.to_period('M'))['consumption'].sum()

price_bleu_by_month = data.groupby(data['date'].dt.to_period('M'))['price_bleu'].sum()
price_vert_by_month = data.groupby(data['date'].dt.to_period('M'))['price_vert'].sum()
price_bleu_hchp_by_month = data.groupby(data['date'].dt.to_period('M'))['price_bleu_hchp'].sum()
price_vert_hchp_by_month = data.groupby(data['date'].dt.to_period('M'))['price_vert_hchp'].sum()
price_tempo_hphc_by_month = data.groupby(data['date'].dt.to_period('M'))['price_tempo_hphc'].sum()

all_price = pd.concat([price_bleu_by_month, price_bleu_hchp_by_month,price_vert_by_month, price_vert_hchp_by_month,price_tempo_hphc_by_month], axis=1)
print(all_price)

annual_price = all_price.sum()
print("Annual estimate:")
print(annual_price)