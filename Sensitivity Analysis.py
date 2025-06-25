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


pd.set_option("display.precision",7)
font_dict=dict(family='Arial',
               size=16,
               color='black'
               )

# This script is a modified version of ForceTorquePlot which conducts a sensitivity analysis
# First we want to convert CM to be about the CG, to make the metric CMCG (check notes on how to do this).
# Then we can check the gradient of the line CL and CM(cg) at every point against AOA
# We can then divide each of the CMslope (which is CMcgalpha) by CLslope (CLalpha) to give the -static margin
# We can plot this against AOA or RunID

# Functions from ForceTorquePlot.py are needed:
# process_lift_drag()
# This is nested within the load_ft_pr() function to add columns of lift, drag, CL,CD and CMom
# Also loads all the variables that change depending on the frame

# load_ft_pr() #Input just the frame number you need.
# This is coded specifically to the run numbers used in this experiment and pathname
# This isn't hard to change provided directory formatting is consistent.

#Added features involve calculation of the gradients at each point for CL and CMOM, to compute CMcgalpha/CLalpha

##### THE MAIN FUNCTION IS GRAPH OUTPUT WITH 2 OUTPUTS
# Output 1 is a plot of RunID against CL and CMOM to show what we would expect the gradients to be (i.e. CLalpha)
# Output 2 is a plot of SM or NP against AOA and calculates the mean values of these for the linear region defined (upper and lower)
    # The values are summarised in a table and scatterplot immediately following its use

#Final function is CMCL graph (based on CMCL_compare script) - must cycle through using for loop
#Output 1 adds a line based on one frame on a CMcg against CL graph, with fig.show() used after for loop


#Wind tunnel data with only Tare Apparatus - need to subtract LIFT,DRAG and TZ
TareApp = pd.read_csv(fr'*Insert pathname*/Tare/TRIALID6_PFT_FRAMEIDTare_Medium.csv').sort_values('RunID',ascending=True)
TareApp2 = pd.read_csv(fr'*Insert pathname*/Tare/TRIALID7_PFT_FRAMEIDTare_High.csv').sort_values('RunID',ascending=True)
TareApp3 = pd.read_csv(fr'*Insert pathname*/Tare/TRIALID8_PFT_FRAMEIDTare_Low.csv').sort_values('RunID',ascending=True)


def slope(x1, y1, x2, y2):
    s = (y2 - y1) / (x2 - x1)
    return s

def liftdrag_Tare(TareData):
    TareData['AOA'] = pd.to_numeric(TareData['AOA'])  # Have to convert AOA to numeric
    TareData['LIFT'] = (-TareData['Fy'] * np.cos(np.radians(TareData['AOA']))) - (TareData['Fx'] * np.sin(
        np.radians(TareData[
                       'AOA'])))  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
    TareData['DRAG'] = (TareData['Fx'] * np.cos(np.radians(TareData['AOA']))) + (-TareData['Fy'] * np.sin(
        np.radians(TareData[
                       'AOA'])))  # Equation to calculate drag. N.B. lift acts in -Y direction, and drag acts in +X direction


    return TareData

TareApp = liftdrag_Tare(TareApp)
TareApp2 = liftdrag_Tare(TareApp2)
TareApp3 = liftdrag_Tare(TareApp3)


def process_lift_drag(lift_name, pressure_name,frame,Reynolds):  #### All the data/things that need to be changed loaded in a function
    global LSA
    ###### Lift and Drag calculation
    if frame == 401:  # Because this is left hand wing, lift acts in positive Y, and drag in positive X.
        lift_name['AOA'] = pd.to_numeric(lift_name['AOA'])  # Have to convert AOA to numeric
        lift_name['LIFT'] = (lift_name['Fy'] * np.cos(np.radians(lift_name['AOA']))) - (lift_name['Fx'] * np.sin(np.radians(lift_name['AOA'])))  # Equation to calculate lift
        lift_name['DRAG'] = (lift_name['Fx'] * np.cos(np.radians(lift_name['AOA']))) + (lift_name['Fy'] * np.sin(
            np.radians(lift_name['AOA'])))  # Equation to calculate drag. N.B. lift acts in -Y direction, and drag acts in +X direction

    else:  # All other frames are right hand, meaning lift is in negative Y, and drag in positive X
        lift_name['AOA'] = pd.to_numeric(lift_name['AOA'])  # Have to convert AOA to numeric
        lift_name['LIFT'] = (-lift_name['Fy'] * np.cos(np.radians(lift_name['AOA']))) - (lift_name['Fx'] * np.sin(
            np.radians(lift_name['AOA'])))  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        lift_name['DRAG'] = (lift_name['Fx'] * np.cos(np.radians(lift_name['AOA']))) + (-lift_name['Fy'] * np.sin(
            np.radians(lift_name[
                           'AOA'])))  # Equation to calculate drag. N.B. lift acts in -Y direction, and drag acts in +X direction

    ###### MUST ALSO TAKE AWAY THE RELEVANT TARE VALUES - FROM LIFT, DRAG and TZ

    ##### Coefficient Calculation
    # Lifting Surface Area - loads in all of these with only the correct one being called for the situation

    # ##### PLANFORM SURFACE AREA
    #
    # LSA378 = 63111.60812 / 1000000
    # LSA384 = 56653.65947 / 1000000
    # LSA391 = 31465.4482 / 1000000
    # LSA395 = 28940.47741 / 1000000
    # LSA401 = 24493.73066 / 1000000

    #### UPPER WETTED SURFACE AREA
    LSA378 = 69804.92804 / 1000000  # Estimated mm^2 lifting surface area of bird in m^3
    LSA384 = 66948.11509 / 1000000
    LSA391 = 44815.75492 / 1000000
    LSA395 = 34911.45671 / 1000000
    LSA401 = 30271.41647 / 1000000

    # I THINK WE USE UPPER WETTED FOR LSA - BUT ASK CHRISTINA

    # ##### LOWER WETTED SURFACE AREA
    # LSA378 = 70945.84563/ 1000000
    # LSA384 = 67564.47256/ 1000000
    # LSA391 = 45232.77582/ 1000000
    # LSA395 = 35238.00184/ 1000000
    # LSA401 = 33861.93148/ 1000000

    LSA = eval('LSA' + str(frame))  # This loads only the relevant LSA to the frame selected in function
    density = pressure_name['Density'].iloc[0]
    velocity = lift_name['Airspeed(m/s)']
    dynamicpressure = density * velocity * velocity / 2
    coefficient = np.mean(dynamicpressure) * LSA #Strictly this isn't correct, as taking mean of dynamic pressure across all 81 AOA readings rather than using the specific one for each

    ###### MUST ALSO TAKE AWAY THE RELEVANT TARE VALUES - FROM LIFT, DRAG and TZ

    if Reynolds == 'Medium':
        lift_name['LIFT'] = lift_name['LIFT'] - TareApp['LIFT']
        lift_name['DRAG'] = lift_name['DRAG'] - TareApp['DRAG']
    elif Reynolds == 'High':
        lift_name['LIFT'] = lift_name['LIFT'] - TareApp2['LIFT']
        lift_name['DRAG'] = lift_name['DRAG'] - TareApp2['DRAG']
    elif Reynolds == 'Low':
        lift_name['LIFT'] = lift_name['LIFT'] - TareApp3['LIFT']
        lift_name['DRAG'] = lift_name['DRAG'] - TareApp3['DRAG']

    lift_name['CLIFT'] = lift_name['LIFT'] / coefficient  # CL is just lift/coefficient
    lift_name['CDRAG'] = lift_name['DRAG'] / coefficient  # CDrag is just drag/coefficient


    if frame == 401:  # Because this is left hand wing, Tz acts in opposite direction to with right hand wing, so current +Tz actually represents pitch down moment so must be multiplied by -1
        if Reynolds == 'Medium':
            lift_name['Tz'] = lift_name['Tz'] + TareApp['Tz'] #Want to add to this value as it is currently acting in pitch down direction, so this weakens what has been measured
        elif Reynolds == 'High':
            lift_name['Tz'] = lift_name['Tz'] + TareApp2['Tz']
        elif Reynolds == 'Low':
            lift_name['Tz'] = lift_name['Tz'] + TareApp3['Tz']
        lift_name['CMOM'] = -lift_name['Tz'] / (coefficient * 0.1679)  # Equation involves dividing by chord length as well

    else:  # +Tz in right wing case represents a pitch up moment which is what we want
        if Reynolds == 'Medium':
            lift_name['Tz'] = lift_name['Tz'] - TareApp['Tz'] #Want to minus away from this value
        elif Reynolds == 'High':
            lift_name['Tz'] = lift_name['Tz'] - TareApp2['Tz']
        elif Reynolds == 'Low':
            lift_name['Tz'] = lift_name['Tz'] - TareApp3['Tz']
        lift_name['CMOM'] = lift_name['Tz'] / (coefficient * 0.1679)  # Equation involves dividing by chord length as well
        
    
    
    ######## ADDED CALCULATIONS FOR CMOMaboutCG and CMOMcgalpha/CLalpha


    #Making CMOM about the cg

    # CG Location
    CG = 0.512242294
    Rod = 0.3913
    dist = Rod-CG # Need to check this is the right calculation

    lift_name['CMOMcg'] = lift_name['CMOM'] - (lift_name['CLIFT']*(dist)) #This includes adds CMOM calculated about the centre of gravity

    ## CMOMcgalpha / CLalpha

    #### 'CMcgα/CLα' Calculation

    lift_name['CLdiff'] = np.insert(np.diff(lift_name['CLIFT'], axis=0), 0, np.nan)  # This calculates a column of the differences between each adjacent CLIFT value (so adding them together gives deltaY of gradient)
    lift_name['CMOMdiff'] = np.insert(np.diff(lift_name['CMOM'], axis=0), 0, np.nan) #Doing this as test to make sure CMOMcg calc is correct
    lift_name['CMOMcgdiff'] = np.insert(np.diff(lift_name['CMOMcg'], axis=0), 0, np.nan)

    # Add in a column for the gradient of CL about each point (calculated between the point itself and 2 adjacent points on either side).
    lift_name['CLgrad'] = np.nan  # Initialize the column with NaN
    lift_name['CLgradtest'] = np.nan  # Initialize the column with NaN
    lift_name['CMOMgrad'] = np.nan  # Initialize the column with NaN
    lift_name['CMOMcggrad'] = np.nan  # Initialize the column with NaN
    lift_name['test'] = np.nan  # Initialize the column with NaN
    lift_name['RollingValues'] = np.nan  # Initialize the column for rolling values

    # Make masks of certain conditions

    # Need 2 masks as we have a direction in our dataset, where from RunID 1 to 21 and 61 to 81
    # we are increasing our AOA incrementally (so adding the np.diff for the value before and after
    # gives delta Y over an AOA change of +2) But between RunID 21 and 61 we have to make -1 multiplied by
    # our delta Y as it is over an AOA change of -2

    mask_1 = ((lift_name['RunID'].between(1, 21)) | (lift_name['RunID'].between(61, 81))) & (~((lift_name['RunID'].isin([1, 21, 61, 81])) | (lift_name['AOA'].isin([20,-20]))))  # This mask prevents calculation on the points which are RUNID 1 and 81 (so where they lack one of the adjacent points) as well as when
    mask_2 = (lift_name['RunID'].between(21, 61)) & (~((lift_name['RunID'].isin([21, 61])) | (lift_name['AOA'].isin([20, -20]))))

    # So first want to calculate CL grad as deltaCL/deltaAOA (which is just 2)

    lift_name.loc[mask_1, 'CLgrad'] = (lift_name['CLdiff'] + lift_name['CLdiff'].shift(-1)) / 2 #N.B. shift -1 takes the row below (so the next runID)
    lift_name.loc[mask_2, 'CLgrad'] = -(lift_name['CLdiff'] + lift_name['CLdiff'].shift(-1)) / 2

    # clgrad_df = pd.DataFrame()
    #
    # for i in range(len(lift_name['RunID'])):
    #     # Select corresponding values of CLIFT and AOA where RUNID is i, i-1, and i+1
    #     selected_data = lift_name[lift_name['RunID'].isin([i, i - 1, i + 1])][['AOA', 'CLIFT']]
    #     selected_slope = stats.linregress(selected_data).slope
    #     # Set the value in the 'CLGradTest' column of the lift_name DataFrame
    #     print(i, selected_slope, "selected slope")
    #     clgrad_df = pd.concat([clgrad_df, pd.DataFrame({'CLgrad': [selected_slope]})], ignore_index=True)
    #     print("why is this different")
    #     print(clgrad_df, "clgraddf")
    # lift_name['CLgradtest'] = clgrad_df['CLgrad']
    #
    # # Concatenate the new column onto the existing lift_name DataFrame

    # Then do same for CMOMcg

    lift_name.loc[mask_1, 'CMOMgrad'] = (lift_name['CMOMdiff'] + lift_name['CMOMdiff'].shift(-1)) / 2
    lift_name.loc[mask_2, 'CMOMgrad'] = -(lift_name['CMOMdiff'] + lift_name['CMOMdiff'].shift(-1)) / 2
    
    lift_name.loc[mask_1, 'CMOMcggrad'] = (lift_name['CMOMcgdiff'] + lift_name['CMOMcgdiff'].shift(-1)) / 2
    lift_name.loc[mask_2, 'CMOMcggrad'] = -(lift_name['CMOMcgdiff'] + lift_name['CMOMcgdiff'].shift(-1)) / 2

    # Then calculate -static margin

    lift_name['CMcgα/CLα'] = lift_name['CMOMcggrad'] / (lift_name['CLgrad'])  # This includes CMOM calculated about the centre of gravity to give -static margin
    lift_name['NP'] = -(lift_name['CMOMgrad'] / lift_name['CLgrad']) + Rod # This calculates static margin
    lift_name['SM'] = lift_name['NP'] - CG # This calculates static margin

    return lift_name  # This lets me return the LiftDrag variable with the lift and drag added onto it



def load_ft_pr(frame): # This exports the frame input as dataframe (using the process lift drag function)
    global LiftDrag, LiftDrag2, LiftDrag3, PressureCoef, PressureCoef2, PressureCoef3, coefficient, coefficient2, coefficient3, upper, lower, LinearRegion, LinearRegionAverage  # This saves all these variables as global variables
    if frame == 378:
        first = 12  # This is the trialID number assigned when performing the experiment
        second = 13
        third = 14
        upper = 7  # This is the AOA bounds for linear region of graph - this is just based on eyeballing the linear region of lift graph (doesn't matter about Cm)
        lower = -8
        added = '' #Just leaving this blank because it's moved for frame 401.
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
    #Need to have special condition for frame 401 as it is in different pathname
    if frame == 401:
        first = 9
        second = 10
        third = 11
        upper = 15
        lower = -15
        added = 'Cleaned_data/'

    # Load F/T data
    LiftDrag = pd.read_csv(
        fr'*Insert pathname*/{added}{frame}/TRIALID{first}_PFT_FRAMEID{frame}_Medium.csv').sort_values('RunID',
                                                                                                                ascending=True)
    LiftDrag2 = pd.read_csv(
        fr'*Insert pathname*/{added}{frame}/TRIALID{second}_PFT_FRAMEID{frame}_High.csv').sort_values('RunID',
                                                                                                               ascending=True)
    LiftDrag3 = pd.read_csv(
        fr'*Insert pathname*/{added}{frame}/TRIALID{third}_PFT_FRAMEID{frame}_Low.csv').sort_values('RunID',
                                                                                                             ascending=True)

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

    ### Process Lift, Drag, CL, CDrag and CMom

    LiftDrag = process_lift_drag(LiftDrag, PressureCoef, frame,'Medium')
    LiftDrag2 = process_lift_drag(LiftDrag2, PressureCoef2, frame,'High')
    LiftDrag3 = process_lift_drag(LiftDrag3, PressureCoef3, frame,'Low')

    LinearRegion = LiftDrag[(LiftDrag['AOA'] >= lower) & (LiftDrag['AOA'] <= upper)]
    LinearRegionAverage = np.nanmean(LinearRegion['CMcgα/CLα'])


    
    
def graph_output(frame, graph1,graph2):
    global fig
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"plot_figure_{timestamp}.pdf"

    if graph1 == 0: # This is a check of what gradients should look like
        pass
    else:

        ###### CLift against RUNID to check what gradient will look like.

        fig = px.line(title=f'TROUBLESHOOT CLift against RUNID' + str(frame), template="plotly_white")
        fig.add_scatter(x=LiftDrag['RunID'], y=LiftDrag['CLIFT'], mode='lines+markers',
                        text=LiftDrag['AOA'], name='Pitching Moment against CL Medium' + str(frame))
        fig.show()

        ###### CMOMcg against RUNID to check what gradient will look like.

        fig = px.line(title=f'TROUBLESHOOT CMOMcg against RUNID' + str(frame), template="plotly_white")
        fig.add_scatter(x=LiftDrag['RunID'], y=LiftDrag['CMOMcg'], mode='lines+markers',
                        text=LiftDrag['AOA'], name='Pitching Moment against CL Medium' + str(frame))
        #fig.show()

    if graph2 == 0: #These are the static margin plots
        pass
    else:

        # # # CMcgα/CLα against AOA Whole Range

    
        fig = px.line(title=f'Whole Range CMcgα/CLα against AOA' + str(frame), template="plotly_white")
        fig.add_scatter(x=LiftDrag['AOA'], y=LiftDrag['CMcgα/CLα'], mode='lines + markers',
                        text=LiftDrag['RunID'], name='Pitching Moment against CL Medium')
        fig.add_vline(x=upper, line=dict(color='black'))  # Add a red vertical line at beginning of our defined linear region
        fig.add_vline(x=lower, line=dict(color='black'))  # Add a red vertical line at end of our defined linear region
        fig.update_layout(
            xaxis_title='Angle of Attack (degrees)',  # X-axis title
            yaxis_title='CMcgα/CLα')
        fig.show()
        # Previously used this for obtaining median value of SM in title
            # ',median SM value = ' + str(-np.nanmedian(LiftDrag['CMcgα/CLα'])



        # # # CMcgα/CLα against AOA only Linear Region

    
        fig = px.line(title=f'Linear Region Range CMcgα/CLα against AOA' + str(frame) + ',mean SM value = ' + str(-np.nanmean(LinearRegion['CMcgα/CLα'])), template="plotly_white")
        fig.add_scatter(x=LinearRegion['AOA'], y=LinearRegion['CMcgα/CLα'], mode='lines + markers',
                        text=LinearRegion['RunID'], name='Pitching Moment against CL Medium')
        fig.update_layout(
            xaxis_title='Angle of Attack (degrees)',  # X-axis title
            yaxis_title='CMcgα/CLα')
        fig.show()


        meanNP = np.nanmean(LinearRegion['NP'])
        meanSMval = -np.nanmean(LinearRegion['CMcgα/CLα'])

        meanSM.append([frame,meanNP,meanSMval]) #Append the meanSM values to list for later use

        # Static margin, but this is just minus of the CMcgα/CLα, so now hashed out

        # fig = px.line(title=f'TROUBLESHOOT SM against AOA' + str(frame) + ',median SM value = ' + str(np.nanmedian(LiftDrag['SM'])), template="plotly_white")
        # fig.add_scatter(x=LiftDrag['AOA'], y=LiftDrag['SM'], mode='lines+markers',
        #                 text=LiftDrag['RunID'], name='Pitching Moment against CL Medium')
        # fig.show()

def CMCLgraph(frame, graph1,graph2):
    if graph1 == 0: # This is a check of what gradients should look like
        pass
    else:
        ###### Cm/Cl
        fig.add_scatter(x=LiftDrag['CLIFT'], y=LiftDrag['CMOMcg'], mode='lines+markers',
                        text=LiftDrag['RunID'], name='Pitching Moment (about CG) against CL Medium' + str(frame))

    if graph2 == 0: # This is a check of what gradients should look like
        pass
    else:
        ###### ONLY LINEAR RANGE
        if i == 378:
            colour = "#ff0000"
        if i == 384:
            colour = "#ff4d00"
        if i == 391:
            colour = "#ff7400"
        if i == 395:
            colour = "#ff9a00"
        if i == 401:
            colour = "#ffc100"

        fig.add_scatter(x=LinearRegion['CLIFT'], y=LinearRegion['CMOMcg'], mode='lines+markers', marker=dict(color=colour),
                        text=LinearRegion['RunID'], showlegend=False)


meanSM = []

for i in (378,378):
    load_ft_pr(i) #Input just the frame number you need (this is coded specifically to the run numbers used in this experiment)
    graph_output(i,0,1)

######## CREATING TABLE

meanSM = pd.DataFrame(meanSM)
stability = ['Unstable' if val < 0 else 'Stable' for val in meanSM[2]]

# Creating a table of values
fig = go.Figure(data=[go.Table(
    header=dict(values=['Frame', 'Mean NP position (over Linear Range)', 'CG position', 'Mean Static Margin Value', 'Stability'],
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[meanSM[0], meanSM[1], [0.512242294] * len(meanSM[0]), meanSM[2], stability],
               fill_color='lavender',
               align='left')
)])

# Update layout properties if needed
fig.update_layout(
    title='Table of Values',
    height=600,  # Set the height of the table
    width=1000    # Set the width of the table
)

# Display the table
pio.show(fig)


##### Plotting SM for each frame

fig = px.line(title=f'NP shift across frames', template="plotly_white")
fig.add_scatter(x=meanSM[0], y=meanSM[1], mode='lines + markers',
                name='Neutral Point Location')
fig.update_layout(
    xaxis_title='Frame',  # X-axis title
    yaxis_title='Mean NP position (as percentage of chord)',
    yaxis=dict(range=[0, 1]),  # Set y-axis range between 0 and 1
    xaxis=dict(type='category', categoryorder='array', categoryarray=meanSM[0]),# Set x-axis as categorical
    height=650,  # Set the height of the plot
    width=500,  # Set the width of the plot
    margin=dict(l=40, r=40, t=40, b=40),  # Adjust margin to accommodate the plot
)


fig.add_hline(y = 0.512242294)
fig.show()

fig = px.line(title=f'SM across frames', template="plotly_white")
fig.add_scatter(x=meanSM[0], y=meanSM[2], mode='lines + markers',
                name='Static Margin value')
fig.update_layout(
    xaxis_title='Frame',  # X-axis title
    yaxis_title='Mean Static Margin value',
    yaxis=dict(range=[-0.5, 0.5]),  # Set y-axis range between 0 and 1
    xaxis=dict(type='category', categoryorder='array', categoryarray=meanSM[0]),
    height=650,  # Set the height of the plot
    width=500,  # Set the width of the plot
    margin=dict(l=40, r=40, t=40, b=40),  # Adjust margin to accommodate the plot
)
fig.show()


################### COMBINED CMCL compare plot

fig = px.line(title=f'CMOMcg against CLift all Frames', template="plotly_white")
fig.update_layout(
            xaxis_title='CLift',  # X-axis title
            yaxis_title='CMOMcg')

for i in (378, 384, 391, 395, 401):
    load_ft_pr(i)  # Input just the frame number you need (this is coded specifically to the run numbers used in this experiment)
    CMCLgraph(i,1,0)
fig.show()

#Only linear range

fig = px.line(title=f'CM/CL in progression through gap obstacle', template="plotly_white")
fig.update_layout(
            xaxis_title='CLift',  # X-axis title
            yaxis_title='CMOMcg')

for i in (378, 384, 391, 395, 401):
    load_ft_pr(i)  # Input just the frame number you need (this is coded specifically to the run numbers used in this experiment)
    CMCLgraph(i,0,1)
fig.update_xaxes(range=(-0.4, 1.2))
fig.update_yaxes(range=(-0.4, 0))
fig.update_xaxes(title_text="CL",
                 showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                 tickcolor='black'
                 )
fig.update_yaxes(title_text="CMcg",
                 showline=True, linewidth=0.5, linecolor='black', mirror=True,
                 ticks='inside', tickwidth=2.4,
                 tickcolor='black'
                 )
fig.update_layout(font=font_dict  # font formatting
                  # remove white space
                  )
fig.update_layout(width=1500, height=1000)
fig.update_xaxes(domain=(0.1, 0.9))
fig.update_yaxes(domain=(0.5, 1))
fig.update_layout(margin=dict(l=100, r=50, t=50, b=50, pad=0))
fig.show()

#############


