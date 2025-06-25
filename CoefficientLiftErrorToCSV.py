import pandas as pd
import plotly.express as px
import sys
import csv
import numpy as np
import plotly.graph_objects as go
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import acf
import numpy as np
from collections import defaultdict
import numpy as np
from tqdm import tqdm

# This script is a modified version of RawDataErrorCalc to obtain CLift as csv file.
    # This is a 2nd part of LiftErrortoCSV

# This is a modified version of professor Harvey's functions and data processing R scripts
# Adapted now to work for python, as well as containing more details about why steps are taken


# Recommended reading
# Effective sample size: https://mc-stan.org/docs/2_21/reference-manual/effective-sample-size-section.html
# Theory of autocorrelation and correction: https://andrewcharlesjones.github.io/journal/21-effective-sample-size.html
# ACF R function: https://www.statology.org/autocorrelation-in-r/
# More theoretical background: https://scholarworks.boisestate.edu/cgi/viewcontent.cgi?article=1031&context=td
# Tau hat information: https://mc-stan.org/docs/2_21/reference-manual/effective-sample-size-section.html
# Discussion of correction factor: https://stats.stackexchange.com/questions/584219/standard-deviation-in-generated-data-with-specified-autocorrelation-correction
# Beran, Jan. Statistics for long-memory processes. Routledge, 2017 : https://click.endnote.com/viewer?doi=10.1201%2F9780203738481&token=WzM0OTE0MTQsIjEwLjEyMDEvOTc4MDIwMzczODQ4MSJd.-aKAgRlGDLshxOeeHJU5LIYBVvQ


def read_data_mod(trialID, frame, reynolds, summary):
    reynolds = str(reynolds)
    summary = str(summary)
    
    data = pd.read_csv(
        fr'*Insert pathname*/{summary}/TRIALID{trialID}FRAMEID{frame}_{reynolds}_{summary}.csv',
        dtype={'RunID': str},
    )

    return data

def findLSA(frame):
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
    return LSA


def SMcalc(lift_name):
    lift_name['CLdiffmean'] = np.insert(np.diff(lift_name['CLIFTmean'], axis=0), 0,
                                        np.nan)  # This calculates a column of the differences between each adjacent CLIFT value (so adding them together gives deltaY of gradient)
    lift_name['CLdiffsd'] = np.nan  # Initialize the column with NaN
    lift_name['CLdiffsd'] = sd_add_sub(lift_name['CLIFTsd'], lift_name['CLIFTsd'].shift(1))

    lift_name['CMOMdiffmean'] = np.insert(np.diff(lift_name['CMOMmean'], axis=0), 0, np.nan)
    lift_name['CMOMdiffsd'] = np.nan  # Initialize the column with NaN
    lift_name['CMOMdiffsd'] = sd_add_sub(lift_name['CMOMsd'], lift_name['CMOMsd'].shift(1))

    lift_name['CMOMcgdiffmean'] = np.insert(np.diff(lift_name['CMOMcgmean'], axis=0), 0, np.nan)
    lift_name['CMOMcgdiffsd'] = np.nan  # Initialize the column with NaN
    lift_name['CMOMcgdiffsd'] = sd_add_sub(lift_name['CMOMcgsd'], lift_name['CMOMcgsd'].shift(1))

    # Add in a column for the gradient of CL about each point (calculated between the point itself and 2 adjacent points on either side).
    lift_name['CLgradmean'] = np.nan  # Initialize the column with NaN
    lift_name['CLgradsd'] = np.nan  # Initialize the column with NaN

    lift_name['CMOMgradmean'] = np.nan  # Initialize the column with NaN
    lift_name['CMOMgradsd'] = np.nan  # Initialize the column with NaN

    lift_name['CMOMcggradmean'] = np.nan  # Initialize the column with NaN
    lift_name['CMOMcggradsd'] = np.nan  # Initialize the column with NaN

    # Make masks of certain conditions

    # Need 2 masks as we have a direction in our dataset, where from RunID 1 to 21 and 61 to 81
    # we are increasing our AOA incrementally (so adding the np.diff for the value before and after
    # gives delta Y over an AOA change of +2) But between RunID 21 and 61 we have to make -1 multiplied by
    # our delta Y as it is over an AOA change of -2

    mask_1 = ((lift_name['RunID'].between(1, 21)) | (lift_name['RunID'].between(61, 81))) & (~(
            (lift_name['RunID'].isin([1, 21, 61, 81])) | (lift_name['AOA'].isin([20,
                                                                                 -20]))))  # This mask prevents calculation on the points which are RUNID 1 and 81 (so where they lack one of the adjacent points) as well as when
    mask_2 = (lift_name['RunID'].between(21, 61)) & (
        ~((lift_name['RunID'].isin([21, 61])) | (lift_name['AOA'].isin([20, -20]))))

    # So first want to calculate CL grad as deltaCL/deltaAOA (which is just 2)

    lift_name.loc[mask_1, 'CLgradmean'] = (lift_name['CLdiffmean'] + lift_name['CLdiffmean'].shift(
        -1)) / 2  # N.B. shift -1 takes the row below (so the next runID)
    lift_name.loc[mask_2, 'CLgradmean'] = -(lift_name['CLdiffmean'] + lift_name['CLdiffmean'].shift(-1)) / 2

    lift_name.loc[mask_1, 'CLgradsd'] = (sd_add_sub(lift_name['CLdiffsd'], lift_name['CLdiffsd'].shift(
        -1))) / 2  # N.B. shift -1 takes the row below (so the next runID)
    lift_name.loc[mask_2, 'CLgradsd'] = (sd_add_sub(lift_name['CLdiffsd'], lift_name['CLdiffsd'].shift(-1))) / 2

    # Then same for CMOMcg

    lift_name.loc[mask_1, 'CMOMgradmean'] = (lift_name['CMOMdiffmean'] + lift_name['CMOMdiffmean'].shift(-1)) / 2
    lift_name.loc[mask_2, 'CMOMgradmean'] = -(lift_name['CMOMdiffmean'] + lift_name['CMOMdiffmean'].shift(-1)) / 2

    lift_name.loc[mask_1, 'CMOMgradsd'] = (sd_add_sub(lift_name['CMOMdiffsd'], lift_name['CMOMdiffsd'].shift(
        -1))) / 2  # N.B. shift -1 takes the row below (so the next runID)
    lift_name.loc[mask_2, 'CMOMgradsd'] = (sd_add_sub(lift_name['CMOMdiffsd'], lift_name['CMOMdiffsd'].shift(-1))) / 2

    lift_name.loc[mask_1, 'CMOMcggradmean'] = (lift_name['CMOMcgdiffmean'] + lift_name['CMOMcgdiffmean'].shift(-1)) / 2
    lift_name.loc[mask_2, 'CMOMcggradmean'] = -(lift_name['CMOMcgdiffmean'] + lift_name['CMOMcgdiffmean'].shift(-1)) / 2

    lift_name.loc[mask_1, 'CMOMcggradsd'] = (sd_add_sub(lift_name['CMOMcgdiffsd'], lift_name['CMOMcgdiffsd'].shift(
        -1))) / 2  # N.B. shift -1 takes the row below (so the next runID)
    lift_name.loc[mask_2, 'CMOMcggradsd'] = (sd_add_sub(lift_name['CMOMcgdiffsd'],
                                                        lift_name['CMOMcgdiffsd'].shift(-1))) / 2

    # Then calculate -static margin

    lift_name['CMcgα/CLαmean'] = lift_name['CMOMcggradmean'] / (
        lift_name['CLgradmean'])  # This includes CMOM calculated about the centre of gravity to give -static margin
    lift_name['CMcgα/CLαsd'] = sd_mult_div(lift_name['CMOMcggradmean'], lift_name['CMOMcggradsd'],
                                           lift_name['CLgradmean'], lift_name['CLgradsd'], lift_name[
                                               'CMcgα/CLαmean'])  # This includes CMOM calculated about the centre of gravity to give -static margin

    lift_name['NPmean'] = -(lift_name['CMOMgradmean'] / lift_name['CLgradmean']) + Rod  # This calculates static margin
    lift_name['NPsd'] = sd_mult_div(lift_name['CMOMgradmean'], lift_name['CMOMgradsd'], lift_name['CLgradmean'],
                                    lift_name['CLgradsd'], lift_name['NPmean'])  # This calculates static margin
    lift_name['SMmean'] = lift_name['NPmean'] - CG  # This calculates static margin
    lift_name['SMsd'] = lift_name['NPsd']  # This calculates static margin

    return lift_name

def remove_tare(dataframe,frame):
    Total_TAForce_Data = dataframe.copy()
    Total_TAForce_Data = Total_TAForce_Data.drop(columns=Total_TAForce_Data.filter(like='df').columns)
    Total_TAForce_Data.iloc[:, 1:] = Total_TAForce_Data.iloc[:, 1:].apply(pd.to_numeric)
    Total_TAForce_Data.reset_index(drop=True, inplace=True)

    TARETotal_Force_Data = Total_TAForce_Data.iloc[-1]
    TARETotal_Force_Data_mean = TARETotal_Force_Data.filter(like='mean')
    TARETotal_Force_Data_sd = TARETotal_Force_Data.filter(like='sd')

    # Iterate through columns of Total_TAForce_Data
    for column in Total_TAForce_Data.columns:
        # Check if the column ends with 'sd'
        if column.endswith('RunID'):
            continue
        if column.endswith('AOA'):
            continue
        elif column.endswith('sd'):
            # Perform custom operation for columns ending with 'sd'
            Total_TAForce_Data[column] = sd_add_sub(Total_TAForce_Data[column], TARETotal_Force_Data_sd[column])
        else:
            # Perform simple subtraction for other columns
            if frame == 401:
                Total_TAForce_Data[column] = Total_TAForce_Data[column] + TARETotal_Force_Data_mean[column] # As 401 acts in opposite direction, actually need to add the TARE to affect the forces
            else:
                Total_TAForce_Data[column] = Total_TAForce_Data[column] - TARETotal_Force_Data_mean[column]

    # Print the modified dataframe
    Total_TAForce_Data = Total_TAForce_Data.drop(index=Total_TAForce_Data.index[-1])
    Total_TAForce_Data.iloc[:, :] = Total_TAForce_Data.iloc[:, :].apply(pd.to_numeric)

    return Total_TAForce_Data


################## ERROR PROPAGATION
### For notes on error propagation see
### https://www.geol.lsu.edu/jlorenzo/geophysics/uncertainties/Uncertaintiespart2.html
### https://www.isobudgets.com/propagation-of-uncertainty-rules/
def sd_add_sub(error1, error2):
    adderror = (error1 ** 2 + error2 ** 2) ** 0.5
    return adderror


def sd_mult_div(meanterm1, error1, meanterm2, error2, meanZ):
    multerror = (((error1 / meanterm1) ** 2 + (error2 / meanterm2) ** 2) ** 0.5) * meanZ
    return multerror


def sd_sin(error1, mean1):
    sinerror = abs(error1) * np.cos(np.radians(mean1))
    sinerrortest = abs(np.cos(np.radians(mean1 + error1)) + np.cos(np.radians(mean1 - error1))) / 2
    return [sinerror, sinerrortest]


def sd_cos(error1, mean1):
    coserror = abs(error1) * -np.sin(np.radians(mean1))
    coserrortest = abs(-np.sin(np.radians(mean1 + error1)) + np.sin(np.radians(mean1 - error1))) / 2
    return [coserror, coserrortest]


##################################################################################
##################################################################################
##################################################################################
##################################################################################
##################################################################################
##################################################################################

# Writing voltage, force and lift to .csv


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
        elif trialID == second:
            reynolds = 'High'
            TareID = 7
        elif trialID == third:
            reynolds = 'Low'
            TareID = 8

        CG = 0.512242294
        Rod = 0.3913
        dist = Rod - CG  # Need to check this is the right calculation
        chord = 0.1679
        
        # Load Data
        ForceData = read_data_mod(trialID,frame,reynolds,'ForceSummary')
        ForceData = remove_tare(ForceData,frame)
        LiftData = read_data_mod(trialID,frame,reynolds,'LiftSummary')
        
        #Load Tare data
        ForceTare = read_data_mod(TareID,'Tare',reynolds,'ForceSummary')
        LiftTare = read_data_mod(TareID,'Tare',reynolds,'LiftSummary')
        
        CLIFTData = LiftData.copy()
        CLIFTData['RunID'] = CLIFTData['RunID'].astype(float)
        ######## HAVE TO STOP HERE SO THAT YOU CAN MINUS THE LIFT MEASURED IN TARE APPARATUS RUNS
        
        CLIFTData['LIFTmean'] = CLIFTData['LIFTmean'] - LiftTare['LIFTmean']
        CLIFTData['LIFTsd'] = sd_add_sub(CLIFTData['LIFTsd'], LiftTare['LIFTsd'])
        
        #### Adding columns from ForceSummary into the new CLIFT dataframe
        
        CLIFTData['Airspeed(m/s)mean'] = ForceData['Airspeed(m/s)mean']  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        CLIFTData['Airspeed(m/s)sd'] = ForceData['Airspeed(m/s)sd']  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        CLIFTData['coefficientmean'] = ForceData['coefficientmean']  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        CLIFTData['coefficientsd'] = ForceData['coefficientsd']  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        
        ############
        
        
        CLIFTData['CLIFTmean'] = CLIFTData['LIFTmean']/ CLIFTData['coefficientmean']  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
        CLIFTData['CLIFTsd'] = sd_mult_div(CLIFTData['LIFTmean'],CLIFTData['LIFTsd'],CLIFTData['coefficientmean'],CLIFTData['coefficientsd'],CLIFTData['CLIFTmean'])

        if frame == 401:
            CLIFTData['CMOMmean'] = -ForceData['Tzmean']/ (CLIFTData['coefficientmean']*chord) # Equation involves dividing by chord length as well
            CLIFTData['CMOMsd'] = sd_mult_div(ForceData['Tzmean'],ForceData['Tzsd'], (CLIFTData['coefficientmean']*chord),(CLIFTData['coefficientsd']*chord), CLIFTData['CMOMmean']) # Equation involves dividing by chord length as well
        else:
            CLIFTData['CMOMmean'] = ForceData['Tzmean'] / (
                        CLIFTData['coefficientmean'] * chord)  # Equation involves dividing by chord length as well
            CLIFTData['CMOMsd'] = sd_mult_div(ForceData['Tzmean'], ForceData['Tzsd'],
                                              (CLIFTData['coefficientmean'] * chord),
                                              (CLIFTData['coefficientsd'] * chord), CLIFTData[
                                                  'CMOMmean'])  # Equation involves dividing by chord length as well

        CLIFTData['CMOMcgmean'] = CLIFTData['CMOMmean'] - (CLIFTData['CLIFTmean']*dist)
        CLIFTData['CMOMcgsd'] = sd_add_sub(CLIFTData['CMOMsd'],(CLIFTData['CLIFTsd']*dist))
        
        ####### SM calc
        
        CLIFTsummary = SMcalc(CLIFTData)
        print('CLIFTsumarry',trialID, frame, reynolds)
        CLIFTsummary.to_csv(f'CLIFTSummary/TRIALID{trialID}FRAMEID{frame}_{reynolds}_CLIFTSummary.csv',
                                        index=False)

print('end')


