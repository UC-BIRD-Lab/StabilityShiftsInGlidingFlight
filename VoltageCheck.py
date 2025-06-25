import pandas as pd
import plotly.express as px
import sys
import csv
import numpy as np
import plotly.graph_objects as go
from statsmodels.graphics.tsaplots import plot_acf

# This script is similar to Force Torque plot but instead checks the underlying voltage data collected.
# It is necessary to confirm that the voltage data has a correct looking profile (e.g. noise in both directions)


TARELiftDrag = pd.read_csv(fr'*Insert pathname*/Tare/TRIALIDTareApparatus2_RFT_FRAMEIDTareApparatus_Medium.csv')
TARELiftDrag['RunID'] = TARELiftDrag['RunID'].astype(str) #Some IDs are as INT and some as STR so just make all strings

for i in range(0,10):
    trial = i
    if i == 0:
        condition = TARELiftDrag['RunID'] == 'Tare'
    else:
        condition = TARELiftDrag['RunID'] == str(trial)
    TARE1 = TARELiftDrag[condition]
    mean = np.mean(TARE1['Dev1/ai1'])
    std = np.std(TARE1['Dev1/ai1'])

    fig = px.line(title=f'DOORtest{i} + {mean} + {std}', template="plotly_white")
    fig.add_scatter(y=TARE1['Dev1/ai1'], mode='markers', line=dict(color="red"), text=TARE1['RunID'])
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_xaxes(ticks="inside")
    fig.update_yaxes(ticks="inside")
    fig.update_xaxes(title="Time")
    fig.update_yaxes(title="Voltage")
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                     tickcolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                     tickcolor='black')
    fig.update_layout(
        margin = dict(l=40, r=40, t=40, b=40))  # Adjust the margins
    # Set x-axis limits between -11 and 21
    fig.show()

















##### DOOR TESTS

##### RAW PRESSURE VOLTAGES for door tests


RAWDOORLiftDrag = pd.read_csv(fr'*Insert pathname*/Doors and drift2/TRIALIDTestDoorsAndDrift2_RPR_FRAMEID Test_Medium.csv')
RAWDOORLiftDrag['RunID'] = RAWDOORLiftDrag['RunID'].astype(str) #Some IDs are as INT and some as STR so just make all strings

for i in range(0,12):
    trial = i
    if i == 0:
        condition = RAWDOORLiftDrag['RunID'] == 'Tare'
    else:
        condition = RAWDOORLiftDrag['RunID'] == str(trial)
    RAWDOOR1 = RAWDOORLiftDrag[condition]
    mean = np.mean(RAWDOOR1['Dev1/ai1'])
    std = np.std(RAWDOOR1['Dev1/ai1'])

    fig = px.line(title=f'DOORtest{i} + {mean} + {std}', template="plotly_white")
    fig.add_scatter(y=RAWDOOR1['Dev1/ai1'], mode='markers', line=dict(color="red"), text=RAWDOORLiftDrag['RunID'],name='q_s')
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_xaxes(ticks="inside")
    fig.update_yaxes(ticks="inside")
    fig.update_xaxes(title="Time")
    fig.update_yaxes(title="Voltage")
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                     tickcolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                     tickcolor='black')
    fig.update_layout(
        margin = dict(l=40, r=40, t=40, b=40))  # Adjust the margins
    # Set x-axis limits between -11 and 21
    #fig.show()

##### RAW FORCE/TORQUE VOLTAGE

RAWFORCELiftDrag = pd.read_csv(fr'*Insert pathname*/Doors and drift2/TRIALIDTestDoorsAndDrift2_RFT_FRAMEID Test_Medium.csv')
RAWFORCELiftDrag['RunID'] = RAWFORCELiftDrag['RunID'].astype(str) #Some IDs are as INT and some as STR so just make all strings
condition = RAWFORCELiftDrag['RunID'] == '1'
RAWFORCE1 = RAWFORCELiftDrag[condition]

fig = px.line(title=f'DOOR', template="plotly_white")
fig.add_scatter(y=RAWFORCE1['Dev2/ai0'], mode='markers', line=dict(color="red"), text=RAWDOORLiftDrag['RunID'],name='q_s')
fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
fig.update_xaxes(ticks="inside")
fig.update_yaxes(ticks="inside")
fig.update_xaxes(title="Time")
fig.update_yaxes(title="Voltage")
fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')
fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')
fig.update_layout(
    margin = dict(l=40, r=40, t=40, b=40))  # Adjust the margins
# Set x-axis limits between -11 and 21
#fig.show()


##### RAW PRESSURE VOLTAGE when testing voltage interferences

RAWVoltageTest = pd.read_csv(fr'*Insert pathname*/Tests/TRIALIDTestVoltage_RPR_FRAMEID378_Medium.csv')
RAWVoltageTest['RunID'] = RAWVoltageTest['RunID'].astype(str) #Some IDs are as INT and some as STR so just make all strings
condition = RAWVoltageTest['RunID'] == '2'
RAWVOLTS1 = RAWVoltageTest[condition]

fig = px.line(title=f'DOOR', template="plotly_white")
fig.add_scatter(y=RAWVOLTS1['Dev1/ai0'], mode='markers', line=dict(color="red"), text=RAWVOLTS1['RunID'],name='q_s')
fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
fig.update_xaxes(ticks="inside")
fig.update_yaxes(ticks="inside")
fig.update_xaxes(title="Time")
fig.update_yaxes(title="Voltage")
fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')
fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')
fig.update_layout(
    margin = dict(l=40, r=40, t=40, b=40))  # Adjust the margins
# Set x-axis limits between -11 and 21
#fig.show()


#### Processed pressure

DOORLiftDrag = pd.read_csv(fr'*Insert pathname*/Tests/TRIALIDTestDoorsAndDrift_PPR_FRAMEID378_Medium.csv').sort_values('RunID', ascending=True)

fig = px.line(title=f'DOOR', template="plotly_white")
fig.add_scatter(x=DOORLiftDrag['RunID'], y=DOORLiftDrag['q_s'], mode='lines+markers', line=dict(color="red"), text=DOORLiftDrag['RunID'],name='q_s')
fig.add_scatter(x=DOORLiftDrag['RunID'], y=DOORLiftDrag['q_j'], mode='lines+markers', line=dict(color="blue"), text=DOORLiftDrag['RunID'],name='q_j')
fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
fig.update_xaxes(ticks="inside")
fig.update_yaxes(ticks="inside")
fig.update_xaxes(title="RunID")
fig.update_yaxes(title="Pa")
fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')
fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True,ticks='inside',tickwidth=2.4,
                 tickcolor='black')
fig.update_layout(
    margin = dict(l=40, r=40, t=40, b=40))  # Adjust the margins
# Set x-axis limits between -11 and 21
#fig.show()