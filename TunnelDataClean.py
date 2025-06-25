import pandas as pd
import plotly.express as px
import sys
import csv
import numpy as np
import plotly.graph_objects as go
from statsmodels.graphics.tsaplots import plot_acf
import plotly.io as pio
from datetime import datetime

# This is a specific code to fix errors made in the recording of errors with the wind tunnel data
# This doesn't overwrite the original data but instead generates new files with corrections made
# Notes are made as to issues with the data made at the time of data collection throughout this script.
# For more details see WindTunnelDataDescription.xlsx file

##N.B. RunID is encoded strangely, Tare is always a str, but sometimes the number values
# are also strings.
# When loading data (other than doing this) need to ensure to set RunID column to all equal str


def load_ft_pr(frame):
    global LiftDrag, LiftDrag2, LiftDrag3, PressureCoef, PressureCoef2, PressureCoef3, RawLiftDrag, RawLiftDrag2, RawLiftDrag3  # This saves all these variables as global variables
    if frame == 378:
        first = 12  # This is the trialID number assigned when performing the experiment
        second = 13
        third = 14
    if frame == 384:
        first = 18
        second = 19
        third = 20
    if frame == 391:
        first = 3
        second = 4
        third = 5
    if frame == 395:
        first = 15
        second = 16
        third = 17
    if frame == 401:
        first = 9
        second = 10
        third = 11
    if frame == 'Tare':
        first = 6
        second = 7
        third = 8

    # Load F/T data
    LiftDrag = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{first}_PFT_FRAMEID{frame}_Medium.csv').sort_values('RunID',
                                                                                                                ascending=True)
    LiftDrag2 = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{second}_PFT_FRAMEID{frame}_High.csv').sort_values('RunID',
                                                                                                               ascending=True)
    LiftDrag3 = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{third}_PFT_FRAMEID{frame}_Low.csv').sort_values('RunID',
                                                                                                             ascending=True)
    RawLiftDrag = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{first}_RFT_FRAMEID{frame}_Medium.csv')
    RawLiftDrag2 = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{second}_RFT_FRAMEID{frame}_High.csv')
    RawLiftDrag3 = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{third}_RFT_FRAMEID{frame}_Low.csv')

    # Load pressure data
    PressureCoef = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{first}_PPR_FRAMEID{frame}_Medium.csv').sort_values('RunID',
                                                                                                                ascending=True)
    PressureCoef2 = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{second}_PPR_FRAMEID{frame}_High.csv').sort_values('RunID',
                                                                                                               ascending=True)
    PressureCoef3 = pd.read_csv(
        fr'*Insert pathname*/{frame}/TRIALID{third}_PPR_FRAMEID{frame}_Low.csv').sort_values('RunID',
                                                                                                             ascending=True)
# load_ft_pr(378) #No issues with frame 378 recording of data
# load_ft_pr(384) #No issues with frame 384 recording of data
# load_ft_pr(391) #No issues with frame 391 recording of data
# load_ft_pr(395) #No issues with frame 395 recording of data

########################################

load_ft_pr(401) #Issues with Medium and low recording of data

#Medium
    #RUNID 29 actually is 12 AOA
    #RUNID 30 actually is 11 AOA
    #RUNID 50 actually is -9 AOA
LiftDrag.loc[LiftDrag['RunID'] == 29, 'AOA'] = 12
RawLiftDrag.loc[RawLiftDrag['RunID'] == 29, 'AOA'] = 12
LiftDrag.loc[LiftDrag['RunID'] == 30, 'AOA'] = 11
RawLiftDrag.loc[RawLiftDrag['RunID'] == 30, 'AOA'] = 11
LiftDrag.loc[LiftDrag['RunID'] == 50, 'AOA'] = -9
RawLiftDrag.loc[RawLiftDrag['RunID'] == 50, 'AOA'] = -9
print(LiftDrag)

#Low
    #RUNID 2 is actually error recording of -1AOA, so just delete this row and shift all others a RUNID lower

LiftDrag3.loc[LiftDrag3['RunID'] == 47, 'AOA'] = -5
RawLiftDrag3.loc[RawLiftDrag3['RunID'] == 47, 'AOA'] = -5

LiftDrag3 = LiftDrag3.drop(LiftDrag3[LiftDrag3['RunID'] == 2].index)
RawLiftDrag3 = RawLiftDrag3.drop(RawLiftDrag3[RawLiftDrag3['RunID'] == 2].index)

# Decrement subsequent 'RunID' values by 1
mask = LiftDrag3['RunID'] > 2
LiftDrag3.loc[mask, 'RunID'] -= 1
print(LiftDrag3)

filtered_dataTARE = RawLiftDrag3[RawLiftDrag3['RunID'] == 'Tare']
filtered_data = RawLiftDrag3.drop(RawLiftDrag3[RawLiftDrag3['RunID'] == 'Tare'].index)
filtered_data['RunID'] = filtered_data['RunID'].astype(int) # Have to do this because not recognising everything as float

mask = filtered_data['RunID'] > 2
filtered_data.loc[mask, 'RunID'] -= 1

RawLiftDrag3 = pd.concat([filtered_dataTARE, filtered_data], axis=0)

# Resave LiftDrag back as a new CSV file
LiftDrag.to_csv('*Insert pathname*/Cleaned_data/401/TRIALID9_PFT_FRAMEID401_Medium.csv', index=False)  # Change 'LiftDrag_modified.csv' to your desired file name
LiftDrag2.to_csv('*Insert pathname*/Cleaned_data/401/TRIALID10_PFT_FRAMEID401_High.csv', index=False)  # Change 'LiftDrag_modified.csv' to your desired file name
LiftDrag3.to_csv('*Insert pathname*/Cleaned_data/401/TRIALID11_PFT_FRAMEID401_Low.csv', index=False)  # Change 'LiftDrag_modified.csv' to your desired file name

RawLiftDrag.to_csv('*Insert pathname*/Cleaned_data/401/TRIALID9_RFT_FRAMEID401_Medium.csv', index=False)  # Change 'RawLiftDrag_modified.csv' to your desired file name
RawLiftDrag2.to_csv('*Insert pathname*/Cleaned_data/401/TRIALID10_RFT_FRAMEID401_High.csv', index=False)  # Change 'RawLiftDrag_modified.csv' to your desired file name
RawLiftDrag3.to_csv('*Insert pathname*/Cleaned_data/401/TRIALID11_RFT_FRAMEID401_Low.csv', index=False)  # Change 'RawLiftDrag_modified.csv' to your desired file name

#######################################################


load_ft_pr('Tare') #Issues with High and low recording of data

#High
#RUNID 40 actually is AOA = 1
LiftDrag2.loc[LiftDrag2['RunID'] == 40, 'AOA'] = 1
RawLiftDrag2.loc[RawLiftDrag2['RunID'] == 40, 'AOA'] = 1


#Low
#RUNID 1 was rotated during measurement, just delete this row and shift all others a RUNID lower

LiftDrag3 = LiftDrag3.drop(LiftDrag3[LiftDrag3['RunID'] == 1].index)

# Decrement subsequent 'RunID' values by 1
mask = LiftDrag3['RunID'] > 1
LiftDrag3.loc[mask, 'RunID'] -= 1
print(LiftDrag3)

filtered_dataTARE = RawLiftDrag3[RawLiftDrag3['RunID'] == 'Tare']
filtered_data = RawLiftDrag3.drop(RawLiftDrag3[RawLiftDrag3['RunID'] == 'Tare'].index)
filtered_data['RunID'] = filtered_data['RunID'].astype(int) # Have to do this because not recognising everything as float
filtered_data = filtered_data.drop(filtered_data[filtered_data['RunID'] == 1].index)

mask = filtered_data['RunID'] > 1
filtered_data.loc[mask, 'RunID'] -= 1

RawLiftDrag3 = pd.concat([filtered_dataTARE, filtered_data], axis=0)
print(RawLiftDrag3)


# Resave LiftDrag back as a new CSV file
LiftDrag.to_csv('*Insert pathname*/Cleaned_data/Tare/TRIALID6_PFT_FRAMEIDTare_Medium.csv', index=False)  # Change 'LiftDrag_modified.csv' to your desired file name
LiftDrag2.to_csv('*Insert pathname*/Cleaned_data/Tare/TRIALID7_PFT_FRAMEIDTare_High.csv', index=False)  # Change 'LiftDrag_modified.csv' to your desired file name
LiftDrag3.to_csv('*Insert pathname*/Cleaned_data/Tare/TRIALID8_PFT_FRAMEIDTare_Low.csv', index=False)  # Change 'LiftDrag_modified.csv' to your desired file name

RawLiftDrag.to_csv('*Insert pathname*/Cleaned_data/Tare/TRIALID6_RFT_FRAMEIDTare_Medium.csv', index=False)  # Change 'RawLiftDrag_modified.csv' to your desired file name
RawLiftDrag2.to_csv('*Insert pathname*/Cleaned_data/Tare/TRIALID7_RFT_FRAMEIDTare_High.csv', index=False)  # Change 'RawLiftDrag_modified.csv' to your desired file name
RawLiftDrag3.to_csv('*Insert pathname*/Cleaned_data/Tare/TRIALID8_RFT_FRAMEIDTare_Low.csv', index=False)  # Change 'RawLiftDrag_modified.csv' to your desired file name

print(RawLiftDrag3)