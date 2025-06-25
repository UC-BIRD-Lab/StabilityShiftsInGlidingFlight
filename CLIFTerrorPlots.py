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
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import statsmodels.api as sm

#
pd.set_option("display.precision",7)
font_dict=dict(family='Arial',
               size=28,
               color='black'
               )

##### This code reads in the files generated from CoefficientLiftErrorToCSV
    # to plot CMcga/CLa with appropriate error bars.

    #This is modified from a testing script called Sensitivity analysis.py
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
        lower = -15
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
            color = "#FF0000"
        elif trialID == second:
            reynolds = 'High'
            TareID = 7
            color = "#FF6800"
        elif trialID == third:
            reynolds = 'Low'
            TareID = 8
            color = "#FFA200"


        CLIFTData = read_data_mod(trialID,frame,reynolds,'CLIFTSummary')
        LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]


        ### Plotting CLift for each frame

        fig = px.line(title=f'CLift against AOA {frame}{reynolds}', template="plotly_white")
        fig.add_scatter(x=CLIFTData['AOA'], y=CLIFTData['CLIFTmean'], mode='lines + markers', marker=dict(color='lightgrey'),
                        error_y=dict(type='data',  # The type of error bars ('data' means the values are data-dependent)
                            array=CLIFTData['CLIFTsd'],  # The error values along the x-axis
                            visible=True,color='lightgrey'  # Make sure the error bars are visible
                        ))
        fig.add_scatter(x=LinearRegion['AOA'], y=LinearRegion['CLIFTmean'], mode='lines + markers', marker=dict(color=color),
                        error_y=dict(type='data',  # The type of error bars ('data' means the values are data-dependent)
                                     array=LinearRegion['CLIFTsd'],  # The error values along the x-axis
                                     visible=True, color='black'  # Make sure the error bars are visible
                                     ))
        fig.update_layout(
            xaxis_title='AOA',  # X-axis title
            yaxis_title='C<sub>L<sub>')

        fig.update_xaxes(dtick=5)
        fig.update_yaxes(dtick=0.2)

        # Remove axis lines
        fig.update_xaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
                         tickwidth=2.4,
                         tickcolor='black')
        fig.update_yaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
                         tickwidth=2.4,
                         tickcolor='black')

        # Remove gridlines
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

        # Set font and size for title and axis labels
        fig.update_layout(font=font_dict,  # font formatting
                          # remove white space
                          )
        fig.update_layout(width=1200, height=1000)
        fig.update_xaxes(domain=(0, 0.5))
        fig.update_yaxes(domain=(0.5, 1))
        fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))
        fig.update_xaxes(range=[-22, 22])
        fig.update_yaxes(range=[-0.5, 1.3])
        # fig.show()

        #### Plotting SM for each frame

        # fig = px.line(title=f'Lift against AOA {frame}{reynolds}', template="plotly_white")
        # fig.add_scatter(x=CLIFTData['AOA'], y=CLIFTData['LIFTmean'], mode='lines + markers', marker=dict(color='black'),
        #                 error_y=dict(type='data',  # The type of error bars ('data' means the values are data-dependent)
        #                     array=CLIFTData['LIFTsd'],  # The error values along the x-axis
        #                     visible=True,color='red'  # Make sure the error bars are visible
        #                 ))
        # fig.update_layout(
        #     xaxis_title='AOA',  # X-axis title
        #     yaxis_title='Mean Lift (N))')
        # fig.show()

        ##### Plotting CMcga/CLa for each frame

        # fig = px.line(title=f'CMcgα/CLαmean against AOA {frame}{reynolds}', template="plotly_white")
        # fig.add_scatter(x=CLIFTData['AOA'], y=CLIFTData['CMcgα/CLαmean'], mode='lines + markers', marker=dict(color='black'),
        #                 error_y=dict(type='data',  # The type of error bars ('data' means the values are data-dependent)
        #                     array=CLIFTData['CMcgα/CLαsd'],  # The error values along the x-axis
        #                     visible=True,color='red'   # Make sure the error bars are visible
        #                 ))
        # fig.update_layout(
        #     xaxis_title='AOA',  # X-axis title
        #     yaxis_title='CMcgα/CLαmean')
        # fig.show()
        #
        ##### Plotting CMcga/CLa for each frame LINEAR REGION
        #
        # fig = px.line(title=f'CMcgα/CLαmean against AOA {frame}{reynolds} LINEAR REGION', template="plotly_white")
        # fig.add_scatter(x=LinearRegion['AOA'], y=LinearRegion['CMcgα/CLαmean'], mode='lines + markers', marker=dict(color='black'),
        #                 error_y=dict(type='data',  # The type of error bars ('data' means the values are data-dependent)
        #                     array=LinearRegion['CMcgα/CLαsd'],  # The error values along the x-axis
        #                     visible=True,color='red'   # Make sure the error bars are visible
        #                 ))
        # fig.update_layout(
        #     xaxis_title='AOA',  # X-axis title
        #     yaxis_title='CMcgα/CLαmean')
        # #fig.show()


########## CM against CL all frames on same graph

fig = px.line(title=f'CM/CL in progression through gap obstacle', template="plotly_white")
fig.update_layout(
            xaxis_title='CL',  # X-axis title
            yaxis_title='CM<sub>cg<sub>')

for frame in tqdm((378, 384, 391, 395, 401)):
    if frame == 378:
        first = 12  # This is the trialID number assigned when performing the experiment

    if frame == 384:
        first = 18

    if frame == 391:
        first = 3

    if frame == 395:
        first = 15

    if frame == 401:
        first = 9
        
    CLIFTData = read_data(first,frame,'Medium', 'CLIFTsummary')
    
    fig.add_scatter(x=CLIFTData['CLIFTmean'], y=CLIFTData['CMOMcgmean'], mode='lines+markers',
                text=CLIFTData['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame),
                    error_x=dict(type='data', array=CLIFTData['CLIFTsd'],
                                 visible=True
                                 ),
                    error_y=dict(type='data', array=CLIFTData['CMOMcgsd'],
                                 visible=True
                                 ))


    fig.update_xaxes(dtick=0.2)
    fig.update_yaxes(dtick=0.1)
    # Remove axis lines
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                     tickcolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                     tickcolor='black')

    # Remove gridlines
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    # Set font and size for title and axis labels
    fig.update_layout(font=font_dict,  # font formatting
                      # remove white space
                      )
    fig.update_layout(width=2500, height=1000)
    fig.update_xaxes(domain=(0.25, 0.75))
    fig.update_yaxes(domain=(0.5, 1))
    fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))

#fig.show()

# ########## CM against CL all frames on same graph NO ERROR BARS
#

for cgshift in (-0.2,-0.15,-0.1,-0.05,0,0.05,0.1,0.15,0.2):

    fig = px.line(title=f'CM/CL in progression through gap obstacle NO ERROR' + 'cgshift =' + str(cgshift), template="plotly_white")
    fig.update_layout(
        xaxis_title='C<sub>L<sub>',  # X-axis title
        yaxis_title='C<sub>M<sub>cg<sub><sub>')

    cmap = plt.cm.plasma_r  # You can choose any colormap you prefer
    norm = plt.Normalize(-0.4, 0.4)  # Adjust according to your data range


    # Define function for colormap mapping
    def map_value_to_color(value):
        return cmap(norm(value))

    for frame in tqdm((378, 384, 391, 395, 401)):

        SMused = pd.read_csv('*Insert pathname*/SMusedMedium.csv')
        SMused = SMused[SMused['Frame'] == frame]

        if frame == 378:
            first = 12  # This is the trialID number assigned when performing the experiment
            second = 13
            third = 14
            upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
            lower = -8
            added = ''  # Just leaving this blank because it's moved for frame 401.
            weightmatch = 73.0 #The ID number for the AOA reading which matches body weight
            AOAup = 6
            AOAdown = 4
        if frame == 384:
            first = 18
            second = 19
            third = 20
            upper = 13
            lower = -3
            added = ''
            weightmatch = 81.0
            AOAup = -3
            AOAdown = -5
        if frame == 391:
            first = 3
            second = 4
            third = 5
            upper = 10
            lower = -10
            added = ''
            weightmatch = 79.0
        if frame == 395:
            first = 15
            second = 16
            third = 17
            upper = 15
            lower = -15
            added = ''
            weightmatch = 38.0
        # Need to have special condition for frame 401 as it is in different pathname
        if frame == 401:
            first = 9
            second = 10
            third = 11
            upper = 15
            lower = -15
            weightmatch = 78.0

        
        CLIFTData = read_data(first, frame, 'Medium', 'CLIFTsummary')
        CLIFTData['CMOMadjust'] = CLIFTData['CMOMcgmean']-(CLIFTData['CLIFTmean']*cgshift)
        LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]
        AOAused = CLIFTData[(CLIFTData['AOA'] >= AOAdown) & (CLIFTData['AOA'] <= AOAup)]

        colour = map_value_to_color(-LinearRegion['CMcgα/CLαmean'])
        # Convert array to RGB string
        colour_rgb = [f'rgb({int(col[0] * 255)}, {int(col[1] * 255)}, {int(col[2] * 255)})' for col in
                             colour]
        LinearRegion['colour'] = colour_rgb

        colourAOA = map_value_to_color(-AOAused['CMcgα/CLαmean'])
        # Convert array to RGB string
        colourAOA_rgb = [f'rgb({int(col[0] * 255)}, {int(col[1] * 255)}, {int(col[2] * 255)})' for col in
                      colourAOA]
        AOAused['colour'] = colourAOA_rgb

        Weightmatchdata = CLIFTData[CLIFTData['RunID'] == str(weightmatch)]

        if frame == 378 or frame == 384:
            for i in range(len(CLIFTData) - 1):
                fig.add_scatter(
                    x=CLIFTData['CLIFTmean'].iloc[i:i + 2],
                    y=CLIFTData['CMOMadjust'].iloc[i:i + 2],
                    mode='lines+markers',  # Use both lines and markers
                    line=dict(color='lightgrey'),  # Use default line width
                    marker=dict(),  # Use default marker size
                    showlegend=False  # Hide trace from the legend
                )
            for i in range(len(LinearRegion) - 1):
                fig.add_scatter(
                    x=LinearRegion['CLIFTmean'].iloc[i:i + 2],
                    y=LinearRegion['CMOMadjust'].iloc[i:i + 2],
                    mode='lines+markers',  # Use both lines and markers
                    line=dict(color='lightgrey'),  # Use default line width
                    marker=dict(),  # Use default marker size
                    showlegend=False  # Hide trace from the legend
                )
            for i in range(len(AOAused) - 1):
                fig.add_scatter(
                    x=AOAused['CLIFTmean'].iloc[i:i + 2],
                    y=AOAused['CMOMadjust'].iloc[i:i + 2],
                    mode='lines+markers',  # Use both lines and markers
                    line=dict(color=AOAused['colour'].iloc[i]),  ## IMPORTANT: CHANGE THESE COLOURS TO BLACK FOR SHOWING CGSHIFT
                    marker=dict(color=AOAused['colour'].iloc[i]),  # Use default marker size
                    showlegend=False  # Hide trace from the legend
                )
        else:
            for i in range(len(CLIFTData) - 1):
                fig.add_scatter(
                    x=CLIFTData['CLIFTmean'].iloc[i:i + 2],
                    y=CLIFTData['CMOMadjust'].iloc[i:i + 2],
                    mode='lines+markers',  # Use both lines and markers
                    line=dict(color='lightgrey'),  # Use default line width
                    marker=dict(),  # Use default marker size
                    showlegend=False  # Hide trace from the legend
                )
            for i in range(len(LinearRegion) - 1):
                fig.add_scatter(
                    x=LinearRegion['CLIFTmean'].iloc[i:i + 2],
                    y=LinearRegion['CMOMadjust'].iloc[i:i + 2],
                    mode='lines+markers',  # Use both lines and markers
                    line=dict(color='black'),  # IMPORTANT: CHANGE THESE COLOURS TO BLACK FOR SHOWING CGSHIFT
                    marker=dict(color='black'),  # Use default marker size
                    showlegend=False  # Hide trace from the legend
                )
        fig.update_xaxes(dtick=0.2)
        fig.update_yaxes(dtick=0.1)
        # Remove axis lines
        fig.update_xaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
                         tickwidth=2.4,
                         tickcolor='black')
        fig.update_yaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
                         tickwidth=2.4,
                         tickcolor='black')
        fig.add_hline(y = 0, annotation_text= '', line=dict(color='black', width=2, dash='dash'))
        fig.add_vline(x = 0, annotation_text= '', line=dict(color='black', width=2, dash='dash'))

        #fig.add_scatter(x=0.672/LinearRegion['coefficientmean'],y=CLIFTData['CMOMadjust'],
                        #mode='markers+text',  # Add 'text' to the mode to show text
                        #text=[str(frame) + ' matching flying weight'],  # Text label for the marker
                        #textposition='bottom left',textfont=dict(
            #size=8  # Set font size
        #), name = str(frame) + ' matching flying weight'
        #)
        # fig.add_scatter(
        #     x=Weightmatchdata['CLIFTmean'],
        #     y=Weightmatchdata['CMOMadjust'],
        #     mode='markers',  # Add 'text' to the mode to show text
        #     marker=dict(
        #         size=20,
        #         color='red',  # Light grey color
        #         opacity=0.25  # Make the marker transparent
        #     ),
        #     name=str(frame) + ' matching flying weight'
        # )


        # Remove gridlines
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

        fig.update_xaxes(range=[-0.5, 1.3])  # Setting y-axis limits
        fig.update_yaxes(range=[-0.75, 0.05])  # Setting y-axis limits

        # Set font and size for title and axis labels
        fig.update_layout(font=font_dict,  # font formatting
                          # remove white space
                          )
        fig.update_layout(width=1750, height=1000)
        fig.update_xaxes(domain=(0.25, 0.75))
        fig.update_yaxes(domain=(0.5, 1))
        fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))

    fig.show()



#########################################################
#########################################################
#########################################################
#########################################################
#########################################################
#########################################################
#########################################################

######### THE REST OF THESE GRAPHS SHOW HOW MODELS FIT

#
#
#
# ########## CM against CL all frames on same graph NO ERROR BARS LINEAR FIT
#
# fig = px.line(title=f'CM/CL in progression through gap obstacle NO ERROR', template="plotly_white")
# fig.update_layout(
#     xaxis_title='C<sub>L<sub>',  # X-axis title
#     yaxis_title='C<sub>M<sub>cg<sub><sub>')
#
# cmap = plt.cm.plasma_r  # You can choose any colormap you prefer
# norm = plt.Normalize(-0.4, 0.4)  # Adjust according to your data range
#
# # Define function for colormap mapping
# def map_value_to_color(value):
#     return cmap(norm(value))
#
# for frame in tqdm((378, 384, 391, 395, 401)):
#
#     SMused = pd.read_csv('*Insert pathname*/SMusedMedium.csv')
#     SMused = SMused[SMused['Frame'] == frame]
#
#     if frame == 378:
#         first = 12  # This is the trialID number assigned when performing the experiment
#         upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
#         lower = -8
#     if frame == 384:
#         first = 18
#         upper = 13
#         lower = -3
#
#     if frame == 391:
#         first = 3
#         upper = 10
#         lower = -10
#
#     if frame == 395:
#         first = 15
#         upper = 15
#         lower = -15
#
#     if frame == 401:
#         first = 9
#         upper = 15
#         lower = -15
#
#     colour = map_value_to_color(-SMused['CMcgα/CLαmean'])
#     # Convert array to RGB string
#     colour = tuple(colour)
#     colour_rgb = f'rgb({int(colour[0][0] * 255)}, {int(colour[0][1] * 255)}, {int(colour[0][2] * 255)})'
#
#     CLIFTData = read_data(first, frame, 'Medium', 'CLIFTsummary')
#     LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]
#
#
#     fig.add_scatter(x=CLIFTData['CLIFTmean'], y=CLIFTData['CMOMcgmean'], mode='lines+markers',
#                     text=CLIFTData['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame), marker=dict(color='lightgrey'), line=dict(color='lightgrey'))
#     fig.add_scatter(x=LinearRegion['CLIFTmean'], y=LinearRegion['CMOMcgmean'], mode='lines+markers',
#                     text=LinearRegion['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame),
#                     marker=dict(color=colour_rgb), line=dict(color=colour_rgb))
#
#     # Assuming LinearRegion is your DataFrame
#     x = LinearRegion['CLIFTmean']
#     y = LinearRegion['CMOMcgmean']
#
#     # Adding a constant term to the predictor
#     x = sm.add_constant(x)
#
#     # Fitting the model
#     model = sm.OLS(y, x).fit()
#
#     # Getting the AIC value
#     aic = model.aic
#
#     # Getting the coefficients
#     intercept, slope = model.params
#
#     print(frame,"Linear AIC value:", aic, "slope:", slope)
#     # Getting the R-squared value
#     adjusted_r_squared = model.rsquared_adj
#     print("Adjusted R-squared value:", adjusted_r_squared)
#     p_values = model.pvalues
#     print("P-values of coefficients:", p_values)
#
#     # Generating points for the line
#     x_line = [min(x['CLIFTmean']), max(x['CLIFTmean'])]
#     y_line = [slope * xi + intercept for xi in x_line]
#
#     # Line plot of the fitted line
#     fig.add_scatter(x=x_line, y=y_line, mode='lines+markers',
#                     name='Fitted line',
#                     marker=dict(color='green'), line=dict(color='green', width = 5))
#
#     fig.update_xaxes(dtick=0.2)
#     fig.update_yaxes(dtick=0.1)
#     # Remove axis lines
#     fig.update_xaxes(zeroline = False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
#                      tickcolor='black')
#     fig.update_yaxes(zeroline = False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
#                      tickcolor='black')
#
#     # Remove gridlines
#     fig.update_xaxes(showgrid=False)
#     fig.update_yaxes(showgrid=False)
#
#     # Set font and size for title and axis labels
#     fig.update_layout(font=font_dict,  # font formatting
#                       # remove white space
#                       )
#     fig.update_layout(width=2500, height=1000)
#     fig.update_xaxes(domain=(0.25, 0.75))
#     fig.update_yaxes(domain=(0.5, 1))
#     fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))
#
# #fig.show()
#
# ########## CM against CL all frames on same graph NO ERROR BARS QUADRATIC
#
# fig = px.line(title=f'CM/CL in progression through gap obstacle NO ERROR', template="plotly_white")
# fig.update_layout(
#     xaxis_title='C<sub>L<sub>',  # X-axis title
#     yaxis_title='C<sub>M<sub>cg<sub><sub>')
#
# cmap = plt.cm.plasma_r  # You can choose any colormap you prefer
# norm = plt.Normalize(-0.4, 0.4)  # Adjust according to your data range
#
#
# # Define function for colormap mapping
# def map_value_to_color(value):
#     return cmap(norm(value))
#
#
# for frame in tqdm((378, 384, 391, 395, 401)):
#
#     SMused = pd.read_csv('*Insert pathname*/SMusedMedium.csv')
#     SMused = SMused[SMused['Frame'] == frame]
#
#     if frame == 378:
#         first = 12  # This is the trialID number assigned when performing the experiment
#         upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
#         lower = -8
#     if frame == 384:
#         first = 18
#         upper = 13
#         lower = -3
#
#     if frame == 391:
#         first = 3
#         upper = 10
#         lower = -10
#
#     if frame == 395:
#         first = 15
#         upper = 15
#         lower = -15
#
#     if frame == 401:
#         first = 9
#         upper = 15
#         lower = -15
#
#     colour = map_value_to_color(-SMused['CMcgα/CLαmean'])
#     # Convert array to RGB string
#     colour = tuple(colour)
#     colour_rgb = f'rgb({int(colour[0][0] * 255)}, {int(colour[0][1] * 255)}, {int(colour[0][2] * 255)})'
#
#     CLIFTData = read_data(first, frame, 'Medium', 'CLIFTsummary')
#     LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]
#
#     fig.add_scatter(x=CLIFTData['CLIFTmean'], y=CLIFTData['CMOMcgmean'], mode='lines+markers',
#                     text=CLIFTData['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame),
#                     marker=dict(color='lightgrey'), line=dict(color='lightgrey'))
#     fig.add_scatter(x=LinearRegion['CLIFTmean'], y=LinearRegion['CMOMcgmean'], mode='lines+markers',
#                     text=LinearRegion['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame),
#                     marker=dict(color=colour_rgb), line=dict(color=colour_rgb))
#
#     # Assuming LinearRegion is your DataFrame
#     x = LinearRegion['CLIFTmean']
#     y = LinearRegion['CMOMcgmean']
#     # Adding polynomial features
#     x_poly = sm.add_constant(pd.DataFrame({'x': x, 'x_squared': x ** 2}))
#     # Fitting the quadratic model
#     model = sm.OLS(y, x_poly).fit()
#     # Getting the AIC value
#     aic = model.aic
#     print(frame, "Quadratic AIC value:", aic)
#     # Getting the R-squared value
#     adjusted_r_squared = model.rsquared_adj # We want this as it takes into acocunt the number of predictors in the model
#     print("Adjusted R-squared value:", adjusted_r_squared)
#     p_values = model.pvalues
#     print("P-values of coefficients:", p_values)
#
#     coefficients = model.params[1:]  # Exclude the intercept
#     intercept = model.params[0]
#
#     print("Coefficients QUADRATIC:", coefficients)
#     print("Intercept:", intercept)
#
#     # Generating points for the quadratic curve
#     x_line = np.linspace(min(x), max(x), 100)
#     x_line_poly = sm.add_constant(pd.DataFrame({'x': x_line, 'x_squared': x_line ** 2}))
#     y_line = model.predict(x_line_poly)
#
#     # Line plot of the fitted line
#     fig.add_scatter(x=x_line, y=y_line, mode='lines+markers',
#                     name='Fitted line',
#                     marker=dict(color='green'), line=dict(color='green'))
#
#     fig.update_xaxes(dtick=0.2)
#     fig.update_yaxes(dtick=0.1)
#     # Remove axis lines
#     fig.update_xaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
#                      tickwidth=2.4,
#                      tickcolor='black')
#     fig.update_yaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
#                      tickwidth=2.4,
#                      tickcolor='black')
#
#     # Remove gridlines
#     fig.update_xaxes(showgrid=False)
#     fig.update_yaxes(showgrid=False)
#
#     # Set font and size for title and axis labels
#     fig.update_layout(font=font_dict,  # font formatting
#                       # remove white space
#                       )
#     fig.update_layout(width=2500, height=1000)
#     fig.update_xaxes(domain=(0.25, 0.75))
#     fig.update_yaxes(domain=(0.5, 1))
#     fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))
#
# #fig.show()
#
# ########## CM against CL all frames on same graph NO ERROR BARS
#
# fig = px.line(title=f'CM/CL in progression through gap obstacle NO ERROR', template="plotly_white")
# fig.update_layout(
#     xaxis_title='C<sub>L<sub>',  # X-axis title
#     yaxis_title='C<sub>M<sub>cg<sub><sub>')
#
# cmap = plt.cm.plasma_r  # You can choose any colormap you prefer
# norm = plt.Normalize(-0.4, 0.4)  # Adjust according to your data range
#
#
# # Define function for colormap mapping
# def map_value_to_color(value):
#     return cmap(norm(value))
#
#
# for frame in tqdm((378, 384, 391, 395, 401)):
#
#     SMused = pd.read_csv('*Insert pathname*/SMusedMedium.csv')
#     SMused = SMused[SMused['Frame'] == frame]
#
#     if frame == 378:
#         first = 12  # This is the trialID number assigned when performing the experiment
#         upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
#         lower = -8
#     if frame == 384:
#         first = 18
#         upper = 13
#         lower = -3
#
#     if frame == 391:
#         first = 3
#         upper = 10
#         lower = -10
#
#     if frame == 395:
#         first = 15
#         upper = 15
#         lower = -15
#
#     if frame == 401:
#         first = 9
#         upper = 15
#         lower = -15
#
#     colour = map_value_to_color(-SMused['CMcgα/CLαmean'])
#     # Convert array to RGB string
#     colour = tuple(colour)
#     colour_rgb = f'rgb({int(colour[0][0] * 255)}, {int(colour[0][1] * 255)}, {int(colour[0][2] * 255)})'
#
#     CLIFTData = read_data(first, frame, 'Medium', 'CLIFTsummary')
#     LinearRegion = CLIFTData[(CLIFTData['AOA'] >= lower) & (CLIFTData['AOA'] <= upper)]
#
#     fig.add_scatter(x=CLIFTData['CLIFTmean'], y=CLIFTData['CMOMcgmean'], mode='lines+markers',
#                     text=CLIFTData['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame),
#                     marker=dict(color='lightgrey'), line=dict(color='lightgrey'))
#     fig.add_scatter(x=LinearRegion['CLIFTmean'], y=LinearRegion['CMOMcgmean'], mode='lines+markers',
#                     text=LinearRegion['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame),
#                     marker=dict(color=colour_rgb), line=dict(color=colour_rgb))
#
#     # Assuming LinearRegion is your DataFrame
#     x = LinearRegion['CLIFTmean']
#     y = LinearRegion['CMOMcgmean']
#     ## Adding polynomial features
#     x_poly = sm.add_constant(pd.DataFrame({'x': x, 'x_squared': x ** 2, 'x_cubed': x ** 3}))
#     # Fitting the quadratic model
#     model = sm.OLS(y, x_poly).fit()
#     # Getting the AIC value
#     aic = model.aic
#     # Getting the R-squared value
#     print(frame, "Cubic AIC value:", aic)
#     adjusted_r_squared = model.rsquared_adj
#     print("Adjusted R-squared value:", adjusted_r_squared)
#     p_values = model.pvalues
#     print("P-values of coefficients:", p_values)
#     # Generating points for the cubic curve
#     x_line = np.linspace(min(x), max(x), 100)
#     x_line_poly = sm.add_constant(pd.DataFrame({'x': x_line, 'x_squared': x_line ** 2, 'x_cubed': x_line ** 3}))
#     y_line = model.predict(x_line_poly)
#
#     # Line plot of the fitted line
#     fig.add_scatter(x=x_line, y=y_line, mode='lines+markers',
#                     name='Fitted line',
#                     marker=dict(color='green'), line=dict(color='green'))
#
#     fig.update_xaxes(dtick=0.2)
#     fig.update_yaxes(dtick=0.1)
#     # Remove axis lines
#     fig.update_xaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
#                      tickwidth=2.4,
#                      tickcolor='black')
#     fig.update_yaxes(zeroline=False, showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside',
#                      tickwidth=2.4,
#                      tickcolor='black')
#
#     # Remove gridlines
#     fig.update_xaxes(showgrid=False)
#     fig.update_yaxes(showgrid=False)
#
#     # Set font and size for title and axis labels
#     fig.update_layout(font=font_dict,  # font formatting
#                       # remove white space
#                       )
#     fig.update_layout(width=2500, height=1000)
#     fig.update_xaxes(domain=(0.25, 0.75))
#     fig.update_yaxes(domain=(0.5, 1))
#     fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))
#
# #fig.show()
#
#
