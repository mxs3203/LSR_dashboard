
import re

import pandas as pd
import numpy as np


I_WANT_Meter = 71
OUTPUT_NAME_FOR_CURVE = "measurement1" # without .IRR
PRESSURE_FILE = r"C:\Users\mxs32\Desktop\Cast3_05092023_1719_1733\SBE39plus_03910409_2023_05_09.asc"
DW_FILE = r"C:\Users\mxs32\Desktop\Cast3_05092023_1719_1733\measurment1_DW.tsv"
MERGE_SEC_TOLERANCE = 2

def psiToM(psi):
    return(psi * 0.70324961490205)

print(psiToM(5.5))

# fixing pressure reading
pressure = pd.read_csv(PRESSURE_FILE, sep=",", skiprows=10, header=None)
pressure.columns = ['temp', 'PSI', 'date', 'TIMETAG2']
pressure['TIMETAG2'] = pressure['TIMETAG2'].str.strip()
pressure['TIMETAG2'] = pd.to_datetime(pressure['TIMETAG2'], format='%H:%M:%S')
pressure['meters'] = pressure['PSI'].apply(lambda x: psiToM(x)+1)

# Fixing data reading
data = pd.read_csv(DW_FILE, sep="\t", skiprows=3)
data = data.tail(-1)
data['TIMETAG2', 'milisec'] = data['TIMETAG2'].str.strip()
data['TIMETAG2'] = data['TIMETAG2'].str.split(".",expand=True)[0]
data['TIMETAG2'] = pd.to_datetime(data['TIMETAG2'], format='%H:%M:%S')
data = data.drop(columns=['Index', 'SN', 'INTTIME(ED)', 'SAMPLE(DELAY)','DARK_SAMP(ED)', 'DARK_AVE(ED)', 'SPECTEMP', 'FRAME(COUNTER)', 'TIMER', 'CHECK(SUM)'])

merged_df = pd.merge_asof(data, pressure, on='TIMETAG2', tolerance=pd.Timedelta(seconds=MERGE_SEC_TOLERANCE))
max_meter = merged_df['meters'].values.max()
if I_WANT_Meter > max_meter:
    exit("The desired meters are beyond what was measured...")

if I_WANT_Meter in merged_df['meters'].values:
    filtered_df = merged_df[merged_df['meters'] == I_WANT_Meter]
else:
    # Find the closest value
    closest_value_index = np.abs(merged_df['meters'] - I_WANT_Meter).idxmin()
    closest_value = merged_df.loc[closest_value_index, 'meters']
    filtered_df = merged_df[merged_df['meters'] == closest_value]

# if more rows, just take the first one
if filtered_df.shape[0] > 1:
    filtered_df = filtered_df.head(1)
elif filtered_df.shape[0] == 0:
    print("This should not happen")
else:
    print("Exactly 1 rows matches...")

filtered_df = filtered_df.drop(columns=['DATETAG', 'TIMETAG2','temp','PSI','date','meters', filtered_df.columns[257] ]).T
# Here we change the columns, transformed the to approapriate type
# filter the 350-750 spectrum and reorganize the column order
filtered_df['nm'] = filtered_df.index
filtered_df.columns = ['value', 'nm']
filtered_df['value'] = filtered_df['value'].astype('float')
filtered_df['nm'] = filtered_df['nm'].apply(lambda x: re.findall(r'\(([^\)]+)\)', x)[0])
filtered_df['nm'] = filtered_df['nm'].astype('float')
filtered_df['ignore'] = -1
filtered_df = filtered_df[['nm', 'ignore', 'value']]
filtered_df = filtered_df[filtered_df['nm'].between(350, 750)]
print(filtered_df.shape)

size_difference = 14

# Calculate the number of rows to insert between each row in A
insert_rows = int(np.ceil(size_difference / len(filtered_df)))
# Repeat each row in A by the number of insert_rows
expanded_A = pd.concat([filtered_df] * insert_rows, ignore_index=True)
# Take the mean every insert_rows rows in expanded_A
expanded_A = expanded_A.groupby(expanded_A.index // insert_rows).mean()
# Append remaining rows from A if necessary
remaining_rows = size_difference
expanded_A = pd.concat([expanded_A, filtered_df.iloc[:remaining_rows]], ignore_index=True)
expanded_A = expanded_A.sort_values("nm")
expanded_A.to_csv(OUTPUT_NAME_FOR_CURVE + ".IRR", sep=" ", index=False)