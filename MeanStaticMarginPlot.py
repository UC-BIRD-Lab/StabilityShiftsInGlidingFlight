import pandas as pd
import plotly.express as px
import sys
import csv
import numpy as np
import plotly.graph_objects as go
from statsmodels.graphics.tsaplots import plot_acf
import plotly.io as pio
from datetime import datetime
from scipy.stats import linregress
from scipy import stats
from tqdm import tqdm
import matplotlib.pyplot as plt

pd.set_option("display.precision", 7)
font_dict=dict(family='Arial',
               size=28,
               color='black'
               )

##### This is modified from CLIFTerrorPlots to plot mean static margin against configuration

# This is modified from a testing script called Sensitivity analysis.py
def read_data(trialID, frame, reynolds, summary):
    reynolds = str(reynolds)
    summary = str(summary)
    data = pd.read_csv(
        fr'*Insert pathname*/{summary}/TRIALID{trialID}FRAMEID{frame}_{reynolds}_{summary}.csv',
        dtype={'RunID': str},
    )
    return data


def read_data_mod(trialID, frame, reynolds, summary):
    reynolds = str(reynolds)
    summary = str(summary)

    data = pd.read_csv(
        fr'*Insert pathname*/{summary}/TRIALID{trialID}FRAMEID{frame}_{reynolds}_{summary}.csv',
        dtype={'RunID': str},
    )

    return data

def sd_add_sub(errors):
    adderror = (errors ** 2).sum() ** 0.5
    return adderror

##############################################################
##############################################################
##############################################################

SMdata = pd.DataFrame()
SMdata = pd.DataFrame(columns=[
                'Frame', 'Reynolds',
                'CMcgα/CLαmean', 'CMcgα/CLαsd'
            ])
count = 0

for frame in tqdm((378, 384, 391, 395, 401)):
    if frame == 378:
        first = 12  # This is the trialID number assigned when performing the experiment
        second = 13
        third = 14
        upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
        lower = -8
        added = ''  # Just leaving this blank because it's moved for frame 401.
    if frame == 384:
        first = 18
        second = 19
        third = 20
        upper = 13
        lower = -3
        added = ''
    if frame == 391:
        first = 3
        second = 4
        third = 5
        upper = 10
        lower = -10
        added = ''
    if frame == 395:
        first = 15
        second = 16
        third = 17
        upper = 15
        lower = -10
        added = ''
    # Need to have special condition for frame 401 as it is in different pathname
    if frame == 401:
        first = 9
        second = 10
        third = 11
        upper = 15
        lower = -15
        added = 'Cleaned_data/'

    for trialID in (first, second, third):
        if trialID == first:
            reynolds = 'Medium'
            TareID = 6
        elif trialID == second:
            reynolds = 'High'
            TareID = 7
        elif trialID == third:
            reynolds = 'Low'
            TareID = 8

        CLIFTData = read_data_mod(trialID, frame, reynolds, 'CLIFTSummary')
        LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]

        ### Calculating the mean static margin and the standard deviation on it

        # print(len(LinearRegion['CMcgα/CLαsd'])-LinearRegion['CMcgα/CLαsd'].isna().sum())

        meanSD = sd_add_sub(LinearRegion['CMcgα/CLαsd'])/(len(LinearRegion['CMcgα/CLαsd'])-LinearRegion['CMcgα/CLαsd'].isna().sum()) #isna accounts for however many nans are present in linear region
        print(np.nanmean(LinearRegion['CMcgα/CLαmean']))
        # print(np.nanmedian(LinearRegion['CMcgα/CLαmean']))
        print(np.nanmean(LinearRegion['CMcgα/CLαmean']))

        count = count+1

        SMdata.loc[count] = [int(frame), reynolds, np.nanmean(LinearRegion['CMcgα/CLαmean']), meanSD]


SMdata.reset_index()

SMdataMedium = SMdata[SMdata['Reynolds'] == 'Medium']
SMdataHigh = SMdata[SMdata['Reynolds'] == 'High']
SMdataLow = SMdata[SMdata['Reynolds'] == 'Low']

# SMdataMedium.to_csv(f'SMdataMedium.csv',index=False)
# SMdataHigh.to_csv(f'SMdataHigh.csv',index=False)
# SMdataLow.to_csv(f'SMdataLow.csv',index=False)

cmap = plt.cm.plasma_r  # You can choose any colormap you prefer
norm = plt.Normalize(-0.4, 0.4)  # Adjust according to your data range
def map_value_to_color(value):
    return cmap(norm(value))

###################################### PLOTTING EVERY REYNOLDS CONDITION

# for reynolds in ['Medium', 'High', 'Low']:
#     test = SMdata[SMdata['Reynolds'] == reynolds]
#     colour_values = (-test['CMcgα/CLαmean']).apply(map_value_to_color)
#     colour_values_rgb = [f'rgb({int(col[0] * 255)}, {int(col[1] * 255)}, {int(col[2] * 255)})' for col in colour_values]
#     test['colour'] = colour_values_rgb
#     fig = px.line(title='MeanSM progression across morphing progression in reynolds' + str(reynolds), template="simple_white")
#     fig.add_scatter(x=test['Frame'], y=-test['CMcgα/CLαmean'], mode='markers', marker=dict(color=test['colour'],size=10),
#                     error_y=dict(type='data',  # The type of error bars ('data' means the values are data-dependent)
#                                   array=test['CMcgα/CLαsd'],  # The error values along the x-axis
#                                   visible=True, color='black'  # Make sure the error bars are visible
#                                   ))
#     fig.update_layout(
#         xaxis_title='Configuration',  # X-axis title
#         yaxis_title='Normalized mean static margin <br>(% of c<sub>r<sub>max</sub></sub>)',  # Y-axis title
#     )
#     fig.update_xaxes(type='category')  # Setting x-axis type to categorical
#     fig.update_yaxes(range=[-0.4, 0.4])  # Setting y-axis limits
#
#     fig.update_xaxes(dtick=1)
#     fig.update_yaxes(dtick=0.2)
#     # Remove axis lines
#     fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
#                      tickcolor='black')
#     fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
#                      tickcolor='black')
#
#     # Remove gridlines
#     fig.update_xaxes(showgrid=False)
#     fig.update_yaxes(showgrid=False)
#
#     # Adding transparent grey box over negative y values
#     fig.update_layout(
#         shapes=[
#             {
#                 'type': 'rect',
#                 'xref': 'paper',
#                 'yref': 'paper',
#                 'x0': 0.25,
#                 'y0': 0.5,
#                 'x1': 0.75,
#                 'y1': 0.75,
#                 'fillcolor': 'grey',
#                 'opacity': 0.2,
#                 'line': {'width': 0}
#             }
#         ]
#     )
#     # Set font and size for title and axis labels
#     fig.update_layout(font=font_dict,  # font formatting
#                       # remove white space
#                       )
#     fig.update_layout(width=1500, height=1000)
#     fig.update_xaxes(domain=(0.25, 0.75))
#     fig.update_yaxes(domain=(0.5, 1))
#     fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))
#
#     fig.show()
#
#
# ### Just as a record of the values, we'll take this for Medium treatment
#
# MaximumSM = -SMdataMedium['CMcgα/CLαmean'].max()
# MinimumSM = -SMdataMedium['CMcgα/CLαmean'].min()
#
# print(test)
#
#



######################################################################

####### Generating a Dataframe of the mean and sd of the SM USED in flight

SMused = pd.DataFrame()
SMused = pd.DataFrame(columns=[
                'Frame', 'Reynolds',
                'CMcgα/CLαmean', 'CMcgα/CLαsd'
            ])
count = 0

for frame in tqdm((378, 384, 391, 395, 401)):
    if frame == 378:
        first = 12  # This is the trialID number assigned when performing the experiment
        second = 13
        third = 14
        upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
        lower = -8
        added = ''  # Just leaving this blank because it's moved for frame 401.
        AOAup = 6
        AOAdown = 4
    if frame == 384:
        first = 18
        second = 19
        third = 20
        upper = 13
        lower = -5
        added = ''
        AOAup = -3
        AOAdown = -5
    if frame == 391:
        first = 3
        second = 4
        third = 5
        upper = 10
        lower = -10
        added = ''
        AOAup = 20  # Basically just making it out of range
        AOAdown = -20
    if frame == 395:
        first = 15
        second = 16
        third = 17
        upper = 15
        lower = -10
        added = ''
        AOAup = 20
        AOAdown = -20
    # Need to have special condition for frame 401 as it is in different pathname
    if frame == 401:
        first = 9
        second = 10
        third = 11
        upper = 15
        lower = -15
        added = 'Cleaned_data/'
        AOAup = 20
        AOAdown = -20

    for trialID in (first, second, third):
        if trialID == first:
            reynolds = 'Medium'
            TareID = 6
        elif trialID == second:
            reynolds = 'High'
            TareID = 7
        elif trialID == third:
            reynolds = 'Low'
            TareID = 8

        CLIFTData = read_data_mod(trialID, frame, reynolds, 'CLIFTSummary')
        LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]
        NonLinear = LinearRegion[(LinearRegion['AOA'] >= AOAdown) & (LinearRegion['AOA'] <= AOAup)]

        ### Calculating the mean static margin and the standard deviation on it

        meanSD = sd_add_sub(NonLinear['CMcgα/CLαsd'])/(len(NonLinear['CMcgα/CLαsd'])-NonLinear['CMcgα/CLαsd'].isna().sum()) #isna accounts for however many nans are present in linear region
        print(np.nanmean(NonLinear['CMcgα/CLαmean']))

        count = count+1

        SMused.loc[count] = [int(frame), reynolds, np.nanmean(NonLinear['CMcgα/CLαmean']), meanSD]

    if frame == 384:
        print(count)
print(SMused)

SMusedMedium = SMused[SMused['Reynolds'] == 'Medium']
SMusedHigh = SMused[SMused['Reynolds'] == 'High']
SMusedLow = SMused[SMused['Reynolds'] == 'Low']

SMusedMedium.to_csv(f'SMusedMedium.csv',index=False)
SMusedHigh.to_csv(f'SMusedHigh.csv',index=False)
SMusedLow.to_csv(f'SMusedLow.csv',index=False)

#### STATIC MARGIN PLOT WITH THE INSTANTANEOUS GRADIENT BEHIND IT

reynolds = 'Medium'
test = SMused[SMused['Reynolds'] == reynolds]
colour_values = (-test['CMcgα/CLαmean']).apply(map_value_to_color)
colour_values_rgb = [f'rgb({int(col[0] * 255)}, {int(col[1] * 255)}, {int(col[2] * 255)})' for col in colour_values]
test['colour'] = colour_values_rgb
fig = px.line(title='SM progression USED across morphing progression in reynolds' + str(reynolds), template="simple_white")
for frame in tqdm((378, 384, 391, 395, 401)):
    if frame == 378:
        first = 12  # This is the trialID number assigned when performing the experiment
        second = 13
        third = 14
        upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
        lower = -8
        added = ''  # Just leaving this blank because it's moved for frame 401.
        AOAup = 6
        AOAdown = 4
    if frame == 384:
        first = 18
        second = 19
        third = 20
        upper = 13
        lower = -3
        added = ''
        AOAup = -3
        AOAdown = -5
    if frame == 391:
        first = 3
        second = 4
        third = 5
        upper = 10
        lower = -10
        added = ''
        AOAup = 20 #Basically just making it out of range
        AOAdown = -20
    if frame == 395:
        first = 15
        second = 16
        third = 17
        upper = 15
        lower = -10
        added = ''
        AOAup = 20
        AOAdown = -20
    # Need to have special condition for frame 401 as it is in different pathname
    if frame == 401:
        first = 9
        second = 10
        third = 11
        upper = 15
        lower = -15
        added = 'Cleaned_data/'
        AOAup = 20
        AOAdown = -20

    CLIFTData = read_data_mod(first, frame, reynolds, 'CLIFTSummary')
    LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]
    LinearRegion['frame'] = frame
    print(frame,LinearRegion['CMcgα/CLαmean'].max()-LinearRegion['CMcgα/CLαmean'].min())
    colour_values = (-LinearRegion['CMcgα/CLαmean']).apply(map_value_to_color)
    colour_values_rgb = [f'rgb({int(col[0] * 255)}, {int(col[1] * 255)}, {int(col[2] * 255)})' for col in
                         colour_values]
    LinearRegion['colour'] = colour_values_rgb
    # Assuming 'frame' is the specified variable
    # jitter_range = 1  # You can adjust this range as needed
    #
    # # Adding jitter to the x-values based on the 'frame' variable
    # jitter = np.random.uniform(-jitter_range, jitter_range, size=len(LinearRegion['frame']))
    # LinearRegion['frame'] = LinearRegion['frame'] + jitter

    fig.add_scatter(x=LinearRegion['frame'], y=-LinearRegion['CMcgα/CLαmean'], mode='markers',
                    marker=dict(color='black', size=8, opacity = 0.2,
                                line=dict(width=0.6,
                                        color='black')
                                )
                    ,showlegend=False)

    NonLinear = LinearRegion[(LinearRegion['AOA'] >= AOAdown) & (LinearRegion['AOA'] <= AOAup)]
    NonLinear['frame'] = frame
    fig.add_scatter(x=NonLinear['frame'], y=-NonLinear['CMcgα/CLαmean'], mode='markers',
                    marker=dict(color=NonLinear['colour'], size=8, opacity = 0.5,
                                line=dict(width=0.6,
                                        color='black')
                                )
                    ,showlegend=False)

    if frame == 384: #Highlighting the out of linear range AOA
        NonLinear = CLIFTData[(CLIFTData['AOA'] >= -5) & (CLIFTData['AOA'] <= -4)]
        NonLinear['frame'] = frame
        colour_values = (-NonLinear['CMcgα/CLαmean']).apply(map_value_to_color)
        colour_values_rgb = [f'rgb({int(col[0] * 255)}, {int(col[1] * 255)}, {int(col[2] * 255)})' for col in
                             colour_values]
        NonLinear['colour'] = colour_values_rgb

        fig.add_scatter(x=NonLinear['frame']-0.5, y=-NonLinear['CMcgα/CLαmean'], mode='markers',
                        marker=dict(color=NonLinear['colour'], size=8, opacity=0.5,
                                    line=dict(width=0.6,
                                              color='black')
                                    )
                        , showlegend=False)


#Unhashtag the following to get just the mean values of the static margin based on the 'points used'
# fig.add_scatter(x=test['Frame']+0.5, y=-test['CMcgα/CLαmean'], mode='markers', marker=dict(color=test['colour'],size=12,line=dict(width=0.5,
#                                         color='black')),
#                 error_y=dict(type='data',  # The type of error bars ('data' means the values are data-dependent)
#                               array=test['CMcgα/CLαsd'],  # The error values along the x-axis
#                               visible=True, color='black'  # Make sure the error bars are visible
#                               ),showlegend=False) # Christina didn't like mean being present

fig.update_layout(
    xaxis_title='Configuration',  # X-axis title
    yaxis_title='Normalized static margin <br>(% of c<sub>r<sub>max</sub></sub>)',  # Y-axis title
)
fig.update_xaxes(type='category')  # Setting x-axis type to categorical
fig.update_yaxes(range=[-0.5, 0.5])  # Setting y-axis limits

fig.update_xaxes(dtick = 1)
fig.update_yaxes(dtick=0.2)
# Remove axis lines
fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                 tickcolor='black')
fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                 tickcolor='black')

# Remove gridlines
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

# Adding transparent grey box over negative y values
fig.update_layout(
    shapes=[
        {
            'type': 'rect',
            'xref': 'paper',
            'yref': 'paper',
            'x0': 0.25,
            'y0': 0.5,
            'x1': 0.75,
            'y1': 0.75,
            'fillcolor': 'grey',
            'opacity': 0.2,
            'line': {'width': 0}
        }
    ]
)
# Set font and size for title and axis labels
fig.update_layout(font=font_dict,  # font formatting
                  # remove white space
                  )
fig.update_layout(width=1500, height=1000)
fig.update_xaxes(domain=(0.25, 0.75))
fig.update_yaxes(domain=(0.5, 1))
fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))

fig.show()

