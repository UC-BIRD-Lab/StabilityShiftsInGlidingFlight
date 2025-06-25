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


# This script is a modified version of ForceTorquePlot that plots all the frames on same graph
# Generating 5 lines:
# CMom against CL at Medium Reynolds

# Only three functions are needed:
# process_lift_drag()
# This is nested within the load_ft_pr() function to add columns of lift, drag, CL,CD and CMom
# Also loads all the variables that change depending on the frame

# load_ft_pr() #Input just the frame number you need.
# This is coded specifically to the run numbers used in this experiment and pathname)
# This isn't hard to change provided directory formatting is consistent.

# graph_output() #Input 1s for graphs you want to see, and 0 for those you don't)
# see listing on top

def best_fit(X, Y):
    xbar = sum(X) / len(X)
    ybar = sum(Y) / len(Y)
    n = len(X)  # or len(Y)

    numer = sum([xi * yi for xi, yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi ** 2 for xi in X]) - n * xbar ** 2

    b = numer / denum
    a = ybar - b * xbar

    print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b


def slope(x1, y1, x2, y2):
    s = (y2 - y1) / (x2 - x1)
    return s


def process_lift_drag(lift_name, pressure_name,
                      frame):  #### All the data/things that need to be changed loaded in a function
    global LSA
    ###### Lift and Drag calculation
    if frame == 401:  # Because this is left hand wing, lift acts in positive Y, and drag in positive X.
        lift_name['AOA'] = pd.to_numeric(lift_name['AOA'])  # Have to convert AOA to numeric
        lift_name['LIFT'] = (lift_name['Fy'] * np.cos(np.radians(lift_name['AOA']))) - (lift_name['Fx'] * np.sin(
            np.radians(lift_name[
                           'AOA'])))  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        lift_name['DRAG'] = (lift_name['Fx'] * np.cos(np.radians(lift_name['AOA']))) + (lift_name['Fy'] * np.sin(
            np.radians(lift_name[
                           'AOA'])))  # Equation to calculate drag. N.B. lift acts in -Y direction, and drag acts in +X direction
    else:  # All other frames are right hand, meaning lift is in negative Y, and drag in positive X
        lift_name['AOA'] = pd.to_numeric(lift_name['AOA'])  # Have to convert AOA to numeric
        lift_name['LIFT'] = (-lift_name['Fy'] * np.cos(np.radians(lift_name['AOA']))) - (lift_name['Fx'] * np.sin(
            np.radians(lift_name[
                           'AOA'])))  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        lift_name['DRAG'] = (lift_name['Fx'] * np.cos(np.radians(lift_name['AOA']))) + (-lift_name['Fy'] * np.sin(
            np.radians(lift_name[
                           'AOA'])))  # Equation to calculate drag. N.B. lift acts in -Y direction, and drag acts in +X direction

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
    coefficient = np.mean(dynamicpressure) * LSA

    lift_name['CLIFT'] = lift_name['LIFT'] / coefficient  # CL is just lift/coefficient
    lift_name['CDRAG'] = lift_name['DRAG'] / coefficient  # CDrag is just drag/coefficient

    if frame == 401:  # Because this is left hand wing, Tz acts in opposite direction to with right hand wing, so Tz represents pitch down moment so must be multiplied by -1
        lift_name['CMOM'] = -lift_name['Tz'] / (
                    coefficient * 0.1679)  # Equation involves dividing by chord length as well
    else:  # +Tz in right wing case represents a pitch up moment, so must be multiplied by -1
        lift_name['CMOM'] = lift_name['Tz'] / (
                    coefficient * 0.1679)  # Equation involves dividing by chord length as well

    return lift_name  # This lets me return the LiftDrag variable with the lift and drag added onto it


def load_ft_pr(frame):
    global LiftDrag, LiftDrag2, LiftDrag3, PressureCoef, PressureCoef2, PressureCoef3, coefficient, coefficient2, coefficient3  # This saves all these variables as global variables
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

    LiftDrag = process_lift_drag(LiftDrag, PressureCoef, frame)
    LiftDrag2 = process_lift_drag(LiftDrag2, PressureCoef2, frame)
    LiftDrag3 = process_lift_drag(LiftDrag3, PressureCoef3, frame)

    # Define the angles between which a line of best fit is made (relevant for NP calculation from slopes)

def graph_output(frame, graph5):
    global fig
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"plot_figure_{timestamp}.pdf"

    if graph5 == 0:
        pass
    else:

        ###### Cm/Cl

        fig.add_scatter(x=LiftDrag['CLIFT'], y=LiftDrag['CMOM'], mode='lines+markers',
                        text=LiftDrag['RunID'], name='Pitching Moment against CL Medium' + str(frame))



fig = px.line(title=f'TROUBLESHOOT Cm against Cl ALL FRAMES', template="plotly_white")

for i in (378, 384, 391, 395, 401):
    load_ft_pr(i)  # Input just the frame number you need (this is coded specifically to the run numbers used in this experiment)
    graph_output(i,1)  # Input 1s for graphs you want to see, and 0 for those you don't - see listing on top

fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
fig.update_xaxes(ticks="inside")
fig.update_yaxes(ticks="inside")
fig.update_xaxes(title="CL")
fig.update_yaxes(title="CM (about rod)")
fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                 tickcolor='black')
fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black', mirror=True, ticks='inside', tickwidth=2.4,
                 tickcolor='black')
fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))  # Set x-axis limits between -11 and 21

# Set the figure size (width, height) in inches
fig_width = 16  # Adjust as needed
fig_height = 12  # Adjust as needed
fig.update_layout(width=fig_width * 96, height=fig_height * 96)  # 1 inch = 96 pixels
fig.show()
pio.write_image(fig, f'*Insert pathname*/Lift graphs/CMCLAllframe.pdf', format='pdf')

#############


