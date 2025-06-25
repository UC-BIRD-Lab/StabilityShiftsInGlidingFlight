import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import numpy as np
import csv
from scipy.interpolate import UnivariateSpline
import plotly.graph_objects as go
from scipy import interpolate, __version__
from scipy.stats import bootstrap
import numpy as np
from plotly.subplots import make_subplots

### This file is modified from my original script from master's project
# called Binning_flights to streamline the production of figure for paper.

####### THIS FILE CONTAINS BINNING METHOD TO AVERAGE FLIGHTS AT THE SAME GAP SIZE
##### THIS IS MOST UP TO DATE VERSION OF METHODOLOGY FOR PLOTTING WINGSPAN VS DISTANCE CHANGE

####### This file contains 3 outputs -
#### Assess tilt of a flight - finds only those that are suitable
#### Examine bins for a given flight condition
#### Plot median wingspan for each flight condition on the same graph

# This file is to create an alternative method of presenting my wingspan against distance data

# So in this file I intend to create a big dataset with all of the flights stacked on top of each other,
# create a histogram for each gap size with the bin size creating a median flight for each bin using group stats.

# choose the figure font
font_dict = dict(family='Arial',
                 size=16,
                 color='black'
                 )

# First thing to do is quantitatively assess whether flights had tilt on them or not.

#  # # # # Assessing tilt in flights

fig = px.line(title=f'TROUBLESHOOT Tilt')
tilt = pd.DataFrame(columns=['Flight_Num', 'Tilt'])
good_flight = pd.DataFrame(columns=['Flight_Num', 'Tilt'])
bad_flight = pd.DataFrame(columns=['Flight_Num', 'Tilt'])

for p in range(1, 66):
    if p < 10:
        flight_trial_number = "0" + str(p)
    else:
        flight_trial_number = str(p)

    if flight_trial_number == '45':
        pass
    else:
        MinMax = pd.read_csv(
            fr'*Insert pathname*/YxWingspan/Trial{flight_trial_number}.csv').sort_values(
            'Frame', ascending=True)

        x_l = MinMax['AvWingtip Y']
        y_l = abs(MinMax['MaxX_Z'] - MinMax['MinX_Z'])

        fig.add_scatter(x=x_l, y=y_l, mode='lines+markers', name=str({flight_trial_number}), line=dict(color="#eb8f34"),
                        text=MinMax["Frame"])

        fig.update_xaxes(autorange='reversed')
        fig.update_xaxes(title="Distance (mm) ")
        fig.update_yaxes(title="Amount of Tilt (difference in height of wingtips)")

        print(flight_trial_number)
        print(np.mean(abs(y_l)))

        if np.mean(
                abs(y_l)) > 92:  # Can change this depending on the amount of roll that can be considered 'level'. sin(a) x 1055 (roughly max wingspan) can give values of around 92 if a = 5, or around 55 if a = 3.
            # Christina said was valid in aerospace to make "small angle approximation" so saying that any angle under 10 degrees is valid, but need to get reference from her on this, so could increase flights considered
            TILT = True
            bad_flight.loc[0] = [flight_trial_number, TILT]
            print('TILT DETECTED IN' + flight_trial_number)
            bad_flight.index = bad_flight.index + 1
            tilt.loc[0] = [flight_trial_number, TILT]
            tilt.index = tilt.index + 1
        else:
            TILT = False
            good_flight.loc[0] = [flight_trial_number, TILT]
            good_flight.index = good_flight.index + 1
            tilt.loc[0] = [flight_trial_number, TILT]
            tilt.index = tilt.index + 1
# fig.show()

around_perch_data = [3, 5, 6, 7, 8, 19, 21, 22, 23, 24, 25, 29, 31, 32, 34, 45, 57, 58, 59, 62, 64,
                     65]  # These are all the points where bird either went around gap or hit the gap rather than tucking in judged when flights were recorded
around_perch = pd.DataFrame(around_perch_data, columns=['Flight_Num'])
around_perch['Flight_Num'] = around_perch['Flight_Num'].astype(str).str.zfill(
    2)  # This adds zeroes to the beginning of each number so that they can be compared to our saved data

suitable = pd.merge(good_flight, around_perch, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge',
                                                                                                              axis=1)  # This removes from our 'good flight' based on angle all those flights which went around the perch

# # # # # Reading in CSVs as variables

MinMax_List = []

for i in suitable['Flight_Num']:
    MinMax = "MinMax" + str(i)
    MinMax_List.append(MinMax)

MinMax_dict = {}  # This creates dictinoary
for i in MinMax_List:
    MinMax_dict[i] = pd.read_csv(
        f'*Insert pathname*/YxWingspan/Trial{i[-2:]}.csv').sort_values('Frame',
                                                                                                              ascending=True)  # Reads in csv and assigns it as a value to the correct minmax (a key)

for key, val in MinMax_dict.items():
    exec(
        key + '=val')  # Makes a variable with name of the key (the thing that labels the list) and assigns it to the value in the list (the flight data table)

# This has succesfully created every flight trial in 'suitable' as its own MinMax variable that can be called on

############################ Adding all flights together into one big dataframe ######################

AllFlight = pd.DataFrame(
    columns=['Flight_Num', 'Frame', 'MinX_X', 'MinX_Y', 'MinX_Z', 'MaxX_X', 'MaxX_Y', 'MaxX_Z', 'Wingspan',
             'AvWingtip Y', 'AvWingtip Z', 'Euclid'])
AllFlight37 = pd.DataFrame(
    columns=['Flight_Num', 'Frame', 'MinX_X', 'MinX_Y', 'MinX_Z', 'MaxX_X', 'MaxX_Y', 'MaxX_Z', 'Wingspan',
             'AvWingtip Y', 'AvWingtip Z', 'Euclid'])
AllFlight30 = pd.DataFrame(
    columns=['Flight_Num', 'Frame', 'MinX_X', 'MinX_Y', 'MinX_Z', 'MaxX_X', 'MaxX_Y', 'MaxX_Z', 'Wingspan',
             'AvWingtip Y', 'AvWingtip Z', 'Euclid'])
AllFlight50 = pd.DataFrame(
    columns=['Flight_Num', 'Frame', 'MinX_X', 'MinX_Y', 'MinX_Z', 'MaxX_X', 'MaxX_Y', 'MaxX_Z', 'Wingspan',
             'AvWingtip Y', 'AvWingtip Z', 'Euclid'])
AllFlight70 = pd.DataFrame(
    columns=['Flight_Num', 'Frame', 'MinX_X', 'MinX_Y', 'MinX_Z', 'MaxX_X', 'MaxX_Y', 'MaxX_Z', 'Wingspan',
             'AvWingtip Y', 'AvWingtip Z', 'Euclid'])

###################  Creating big dataframe with all numbers in it
for i in MinMax_List:
    flight_trial = eval(i)
    AllFlight = pd.concat([AllFlight, flight_trial], axis=0)

# Creating big dataframe for just gap size 37

for i in MinMax_List:
    flight_trial = eval(i)  # This evaluates i not as a string but as a value.
    # print(flight_trial['Flight_Num'].values[0]) # This is just proof of concept that doing column and values[0] returns just one number we can use to match conditions.
    if flight_trial['Flight_Num'].values[0] >= 0 and flight_trial['Flight_Num'].values[
        0] <= 20:  # This is the condition that defines the gap size so we can group them
        AllFlight37 = pd.concat([AllFlight37, flight_trial], axis=0)
    elif flight_trial['Flight_Num'].values[0] >= 61 and flight_trial['Flight_Num'].values[0] <= 65:
        AllFlight37 = pd.concat([AllFlight37, flight_trial], axis=0)
    else:
        pass

# Creating big dataframe for just gap size 30

for i in MinMax_List:
    flight_trial = eval(i)  # This evaluates i not as a string but as a value.
    # print(flight_trial['Flight_Num'].values[0]) # This is just proof of concept that doing column and values[0] returns just one number we can use to match conditions.
    if flight_trial['Flight_Num'].values[0] >= 21 and flight_trial['Flight_Num'].values[
        0] <= 35:  # This is the condition that defines the gap size so we can group them
        AllFlight30 = pd.concat([AllFlight30, flight_trial], axis=0)
    else:
        pass

# Creating big dataframe for just gap size 50

for i in MinMax_List:
    flight_trial = eval(i)  # This evaluates i not as a string but as a value.
    # print(flight_trial['Flight_Num'].values[0]) # This is just proof of concept that doing column and values[0] returns just one number we can use to match conditions.
    if flight_trial['Flight_Num'].values[0] >= 36 and flight_trial['Flight_Num'].values[
        0] <= 50:  # This is the condition that defines the gap size so we can group them
        AllFlight50 = pd.concat([AllFlight50, flight_trial], axis=0)
    else:
        pass

# Creating big dataframe for just gap size 70

for i in MinMax_List:
    flight_trial = eval(i)  # This evaluates i not as a string but as a value.
    # print(flight_trial['Flight_Num'].values[0]) # This is just proof of concept that doing column and values[0] returns just one number we can use to match conditions.
    if flight_trial['Flight_Num'].values[0] >= 51 and flight_trial['Flight_Num'].values[
        0] <= 60:  # This is the condition that defines the gap size so we can group them
        AllFlight70 = pd.concat([AllFlight70, flight_trial], axis=0)
    else:
        pass

############################### Visualising count of points in each bin for each gap size group

### BIN SETTINGS

start = -1090
end = 1520
size = 90

for i in (37, 50, 70):
    Allflightdata = eval("AllFlight" + str(i))
    name = "Bins for Gap Width" + str(i)
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=Allflightdata['AvWingtip Y'],
                               xbins=dict(start=start, end=end,
                                          size=size)))  # Between -1100 and 760 is the bit we want in high resolution, which is the big change in wingspan
    fig.update_xaxes(autorange="reversed")  # Since direction of positive flight is from positive to negative y
    fig.update_layout(title=name)
    # fig.show()

bins = pd.Series(np.arange(start, end,
                           size))  # This is creating bins as a list of values between -1150 and 1600 with a bin size of 50
labels = pd.Series(np.arange(start, (end - size),
                             size))  # This is creating labels for the bins. I want the label to be the front edge of bin (i.e. for bin 1600 to 1550, I want it to label 1550, so have set it like this
AllFlight37['bin'] = pd.cut(AllFlight37['AvWingtip Y'], bins=bins,
                            labels=labels)  # This adds bins as a column to Allflight based on the Wingtip value and number of bins selected (which is the same as is done on the graphs).
AllFlight30['bin'] = pd.cut(AllFlight30['AvWingtip Y'], bins=bins, labels=labels)
AllFlight50['bin'] = pd.cut(AllFlight50['AvWingtip Y'], bins=bins, labels=labels)
AllFlight70['bin'] = pd.cut(AllFlight70['AvWingtip Y'], bins=bins, labels=labels)

# # # # # # Performing group stats

########################################################################################

# # # # # # # Median and IQ range method - much simpler and works.

median_AllFlight37 = pd.DataFrame(columns=['bin', 'median', 'LowerBound', 'UpperBound'])
median_AllFlight50 = pd.DataFrame(columns=['bin', 'median', 'LowerBound', 'UpperBound'])
median_AllFlight70 = pd.DataFrame(columns=['bin', 'median', 'LowerBound', 'UpperBound'])

for j in (37, 50, 70):
    AllFlightdata = eval("AllFlight" + str(j))
    for i in range(start, (end - size), size):
        median_calcs = AllFlightdata.loc[AllFlightdata['bin'] == i]
        median = np.median(median_calcs['Wingspan'])

        # First quartile (Q1)
        Q1 = np.percentile(median_calcs['Wingspan'], 25, method='midpoint')
        # Third quartile (Q3)
        Q3 = np.percentile(median_calcs['Wingspan'], 75, method='midpoint')

        if j == 37:
            median_AllFlight37.loc[0] = [i, median, Q1, Q3]  # adding a row
            median_AllFlight37.index = median_AllFlight37.index + 1
        elif j == 50:
            median_AllFlight50.loc[0] = [i, median, Q1, Q3]  # adding a row
            median_AllFlight50.index = median_AllFlight50.index + 1
        elif j == 70:
            median_AllFlight70.loc[0] = [i, median, Q1, Q3]  # adding a row
            median_AllFlight70.index = median_AllFlight70.index + 1

fig = px.line(template="simple_white")
color = 'rgb(77,175,74)'
fillcolor = 'rgba(77,175,74,0.2)'
for i in (37, 50, 70):
    name = "Gap Width" + str(i)
    median = eval("median_AllFlight" + str(i))['median']
    # Distance = eval("median_AllFlight" + str(i))['bin']
    Distance = eval("median_AllFlight" + str(i))['bin'] + 580
    upper_bound = eval("median_AllFlight" + str(i))['UpperBound']
    lower_bound = eval("median_AllFlight" + str(i))['LowerBound']
    orig_data = eval("AllFlight" + str(i))['Wingspan']
    # AvWingtipY = eval("AllFlight" + str(i))['AvWingtip Y']
    AvWingtipY = eval("AllFlight" + str(i))['AvWingtip Y'] + 580
    individual_flight = eval("AllFlight" + str(i))['Flight_Num']
    if i == 37:
        color = 'rgb(77,175,74)'
        fillcolor = 'rgba(77,175,74,0.4)'
        transparent_point = 'rgba(77,175,74,0.1)'
    elif i == 30:
        color = 'rgb(247,129,191)'
        fillcolor = 'rgba(247,129,191,0.4)'
        transparent_point = 'rgba(247,129,191,0.1)'
    elif i == 50:
        color = 'rgb(255,127,0)'
        fillcolor = 'rgba(255,127,0,0.4)'
        transparent_point = 'rgba(255,127,0,0.1)'
    elif i == 70:
        color = 'rgb(55,126,184)'
        fillcolor = 'rgba(55,126,184,0.4)'
        transparent_point = 'rgba(55,126,184,0.1)'
    fig.add_traces([
        go.Scatter(x=Distance, y=median, mode='markers', name=name, line=dict(color=color), showlegend=False),
        go.Scatter(x=Distance, y=lower_bound, mode='lines', line={'dash': 'dash', 'color': color, 'width': 0},
                   showlegend=False),
        go.Scatter(x=Distance, y=upper_bound, mode='lines', line={'dash': 'dash', 'color': color, 'width': 0},
                   fillcolor=fillcolor, fill='tonexty', showlegend=False),
        go.Scatter(x=AvWingtipY, y=orig_data, mode='markers', showlegend=False, line=dict(color=transparent_point),
                   text=individual_flight, marker_size=5)])

    # These are set up to be in colourblind friendly colours and slight transparency on the confidence interval lines
    # Can either show all graphs separately by placing fig.show() within for loop, or all together outside the loop

#### Just for one flight

# Distance = eval(MinMax_List[1])['AvWingtip Y'] + 580 # Selecting flight 10.
# Wingspan = eval(MinMax_List[1])['Wingspan']
# print(eval(MinMax_List[1]))
#
# fig.add_scatter(x=Distance, y=Wingspan, mode='lines+markers', name=str('flight11'), line=dict(color='black'),showlegend=False)

    # #### All size 37cm
    #
    # Distance = AllFlight37['AvWingtip Y'] + 580 # Selecting flight 10.
    # Wingspan = AllFlight37['Wingspan']
    #
    # fig.add_scatter(x=Distance, y=Wingspan, mode='markers', name=name, line=dict(color='rgb(77,175,74)'),showlegend=False)

fig.add_vline(x=0, line_width=2.4, line_dash="dash", line_color="black")  # Location of gap

fig.add_hline(y=370, line_width=2.4, line_dash="dash",
              line_color="black")  # indicator of gap size 37 cm # annotation_text="Gap size 37cm",
fig.add_hline(y=500, line_width=2.4, line_dash="dash",
              line_color="black")  # indicator of gap size 50 cm # annotation_text="Gap size 50cm",
fig.add_hline(y=700, line_width=2.4, line_dash="dash",
              line_color="black")  # indicator of gap size 70 cm # annotation_text="Gap size 70cm",

fig.add_annotation(xref="paper", yref="y", x=0.88, y=400, text="37cm", showarrow=False,
                   font=dict(family='Arial', size=22, color='rgb(77,175,74)'), align="center", valign="middle")
fig.add_annotation(xref="paper", yref="y", x=0.88, y=530, text="50cm", showarrow=False,
                   font=dict(family='Arial', size=22, color='rgb(255,127,0)'), align="center", valign="middle")
fig.add_annotation(xref="paper", yref="y", x=0.88, y=730, text="70cm", showarrow=False,
                   font=dict(family='Arial', size=22, color='rgb(55,126,184)'), align="center", valign="middle")

fig.update_xaxes(range=(2250, -975))
fig.update_yaxes(range=(100, 1150))
fig.update_xaxes(title_text="Distance to gap obstacle (mm)",
                 showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                 tickcolor='black'
                 )
fig.update_yaxes(title_text="Wingspan (mm)",
                 showline=True, linewidth=0.5, linecolor='black', mirror=True,
                 ticks='inside', tickwidth=2.4,
                 tickcolor='black'
                 )
fig.update_layout(font=font_dict,  # font formatting
                  # remove white space
                  )
fig.update_layout(width=1500, height=1000)
fig.update_xaxes(domain=(0.1, 0.9))
fig.update_yaxes(domain=(0.5, 1))
fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))

fig.show()

########################################
########################################
########################################
########################################
########################################
########################################
########################################
########################################
########################################