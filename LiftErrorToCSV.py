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


# This script is a modified version of RawDataErrorCalc to obtain Lift as csv file.
# This requires "TunnelDataClean.py" to have been run to obtain suitable data

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


# Adam's matrix multiplication function.

# Define a function to calculate the matrix multiplication, matrix1 is the 6x6 one, matrix2 is the 6x1 one (our gauge voltages)
# N.B. All of the files that reference how to do this are found in the WindTunnel Box, of particular note;
# Pg 15 and 16 of Sigrest_Michigan2x2WT_StandardOperatingProcedure.docx to see which numbers to use and why
# Pg 18 of ATI_FT_DAQ_9620-05-DAQ.pdf shows the way to compute the forces from the voltages


# Creating Runtime Matrix from the FT45373.Cal file
raw_runtime_matrix = np.array([
    [0.33540, -0.29225, 1.83084, 33.03722, -1.59372, -30.83877],
    [-2.25473, -38.50986, 1.47089, 18.57416, 0.59621, 18.26460],
    [18.67027, -0.32321, 18.30217, -0.21484, 18.15501, -0.57202],
    [-0.36825, -0.30340, 31.25938, 0.15263, -31.78365, 0.67638],
    [-37.77196, 0.08005, 18.05492, -0.20622, 18.20508, -0.03741],
    [-1.08480, -19.37539, -1.07799, -19.24379, -0.87859, -18.15185]
])

useraxis_runtime_matrix = np.array([
    [0.12855, -0.11201, 0.70170, 12.66216, -0.61082, -11.81956],
    [-0.86417, -14.75965, 0.56375, 7.11891, 0.22851, 7.00026],
    [21.06874, -0.36473, 20.65335, -0.24244, 20.48729, -0.64551],
    [-0.00802, -0.08189, 0.29044, 0.03956, -0.29101, 0.04374],
    [-0.34799, 0.00134, 0.16225, -0.06976, 0.17066, 0.06300],
    [-0.00997, -0.17803, -0.00990, -0.17682, -0.00807, -0.16678]
])


def matrix_multiply(matrix1, matrix2):
    if len(matrix1[0]) != len(matrix2):
        raise ValueError("Matrix1 columns must match Matrix2 rows for multiplication.")

    result = [[0.0 for _ in range(len(matrix2[0]))] for _ in range(len(matrix1))]

    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix2)):
                result[i][j] += matrix1[i][k] * matrix2[k][j]

    return result


def read_data(trialID, frame, reynolds, type):
    reynolds = str(reynolds)
    if frame == 401 or frame == 'Tare':
        if type == 'PR':
            data = pd.read_csv(
                fr'*Insert pathname*/{frame}/TRIALID{trialID}_RPR_FRAMEID{frame}_{reynolds}.csv',
                dtype={'Time': str, 'RunID': str},
                )  # load data
        elif type == 'FT':
            data = pd.read_csv(
                fr'*Insert pathname*/Cleaned_data/{frame}/TRIALID{trialID}_RFT_FRAMEID{frame}_{reynolds}.csv',
                dtype={'Time': str, 'RunID': str},
                )
    else:
        if type == 'PR':
            data = pd.read_csv(
                fr'*Insert pathname*/{frame}/TRIALID{trialID}_RPR_FRAMEID{frame}_{reynolds}.csv',
                dtype={'Time': str, 'RunID': str},
                )  # load data
        elif type == 'FT':
            data = pd.read_csv(
                fr'*Insert pathname*/{frame}/TRIALID{trialID}_RFT_FRAMEID{frame}_{reynolds}.csv',
                dtype={'Time': str, 'RunID': str},
                )

    return data


# For notes on timeseriesstd function http://www.metrology.pg.gda.pl/full/2010/M&MS_2010_003.pdf
# # # Effective sample size calculation

# To calculate the effective sample size we can use the equation listed in Theory of autocorrelation and correction
# To detect autocorrelation we find the correlation (Pearson's coefficient ρ) between the data, and itself time shifted to different times
# i.e. compare t against t+1. We do this for every time lag possible (so up to n-1 lags).
# We start by comparing t against t, which will give ρ = 1 as they are the same thing they are correlated
# Then we iterate to calculate the ρ for t against every other timestep (t+n) and sum all of them together

def timeseries_std(timeseries, no_samples):  # input voltage data and number of samples per reading
    data_std_sample = np.std(timeseries)  # finds standard deviation of the whole voltage data
    no_lags = no_samples - 1  # Defining all the possible time lag comparisons
    autocor = pd.Series(sm.tsa.acf(timeseries, nlags=no_samples))

    sum_1 = 0  # This creates a variable called sum_1 is tau hat. This is the sum portion of predicted time
    sum_2 = 0  # This creates a variable called sum_2 which is essentially just the variance

    for j in range(0, no_lags):  # want to iterate over all 39,999 comparisons
        sum_1 = sum_1 + (autocor[j] * ((
                                                   no_samples - j) / no_samples))  # So this sums up all the ρ values, and weights them by their degrees of freedom (given by index) to essentially give N (which is sample size including degrees of freedom).
        sum_2 = sum_2 + (autocor[
                             j] ** 2)  # This is essentially just summing up the variance for each correlation. But this is a bit weird. Why is it not just variance squared? This is squaring each variance and then adding them all up, which is different.

    no_indsample = no_samples / (1 + (
                2 * sum_1))  # EQN 12.This is the equation listed in notes to calculate effective sample size, but N.B. sum_1 has already accounted for degrees of freedom
    no_dof = (no_samples / (1 + (2 * sum_2))) - 1  # DOF are the number of independent samples-1

    # https://stats.stackexchange.com/questions/584219/standard-deviation-in-generated-data-with-specified-autocorrelation-correction
    correction = no_indsample * (no_samples - 1) / (
                no_samples * (no_indsample - 1))  # Adding a correction term (but not sure what this represents)
    data_std_true = np.sqrt(
        correction * data_std_sample ** 2)  # multiply variance by correction factor then square root to get to true standard deviation.

    results = {
        'data_std_true': data_std_true,
        'no_dof': no_dof
    }
    return results


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


def densitycalc(p_atm, t_atm):
    q = p_atm * 3386.39 / (286.9 * (t_atm + 273.15))
    # 1 inHg. = 3386.39 Pa
    # R = 286.9 J/kgK, Gas Constant
    return q


def PressureTransducerfunc(voltage):
    pressure = ((voltage - 0.2) * (1244.2 + 1244.2) / (5.2 - 0.2) - 1244.2)
    return pressure


def getAirspeedfunc(Pressure,
                    rho):  # N.B. this used to include K_constant as just = 1, but Christina said was misleading.
    # differential_static_pressure = P_L - P_S
    V_j = np.sqrt(2 * (Pressure) / (rho))  # Airspeed_msValue at station J (where model mounts in test section)

    return V_j


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

#Writing voltage, force and lift to .csv


for frame in (378,384,391,395,401,'Tare'):
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
    if frame == 'Tare':
        first = 6
        second = 7
        third = 8

    for trialID in (first,second,third):
        if trialID == first:
            reynolds = 'Medium'
            RawFT = read_data(trialID, frame, reynolds, 'FT')
            RawPR = read_data(trialID, frame, reynolds, 'PR')
        elif trialID == second:
            reynolds = 'High'
            RawFT = read_data(trialID, frame, reynolds, 'FT')
            RawPR = read_data(trialID, frame, reynolds, 'PR')
        elif trialID == third:
            reynolds = 'Low'
            RawFT = read_data(trialID, frame, reynolds, 'FT')
            RawPR = read_data(trialID, frame, reynolds, 'PR')

        RawFT = RawFT.drop('Time', axis=1)
        RawPR = RawPR.drop('Time', axis=1)
        RawPR['RunID'] = RawPR['RunID'].astype(str)  # Some IDs are as INT and some as STR so just make all strings
        RawPR['Dev1/ai0'] = RawPR['Dev1/ai0'].astype(
            float)  # Some IDs are as INT and some as STR so just make all strings
        RawPR['Dev1/ai1'] = RawPR['Dev1/ai1'].astype(
            float)  # Some IDs are as INT and some as STR so just make all strings

        # print(RawFT.loc[RawFT['RunID'] == str(1)].iloc[0])
        print(frame, trialID)

################ VOLTAGE_INFO

# This collates the mean and sd of the voltage data - this is useful just to have

        # Create an empty DataFrame
        voltage_summary = pd.DataFrame()

        for j in range(0,int(len(RawFT['RunID'])/40000)): # This is the max run ID number. Looping through each of these to add the summary stats to dataset.
        # for j in range(0,3): # testing purposes
            print(j, "VoltageRunID/81")
            channel_summary = []  # Creating a list to save all the values into

            if j == 0: #Because we don't have RUNID 0, instead we want to look at Tare
                condition = RawFT['RunID'] == 'Tare' #Few issues with using Tare, as the FTfile doesn't have values for the tare of the pressure - NEED TO FIX THIS
                channel_summary.append(str('Tare'))
            else:
                condition = RawFT['RunID'] == str(j)
                channel_summary.append(str(j))

            selectedrows = RawFT.loc[condition]  # Obtain only rows relating to one run
            selectedrowsPRTare = RawPR.loc[condition] # Obtain the tare pressure values from pressure spreadsheet

            #FT Voltage STD and DOF

            for i in range(6): #Iterating over each of the channels in Daq2 (Force), always want these
                # print(i, "Channel/6")
                column_name = f'Dev2/ai{i}'
                mean1 = np.mean(selectedrows[column_name])
                info = timeseries_std(selectedrows[column_name], 39999) #Running the function on the specific channel
                std = info['data_std_true'] #Pulling out just the standard deviation value
                dof = info['no_dof']  # Pulling out just the degrees of freedom value
                channel_summary.extend([mean1,std,dof]) #saving mean

                #also doing for pressure voltage channels included in FT sheet
            if j == 0: #Need to specify if we are looking at Tare row, then we need to take the values from PRR
                PRcolumn_name = 'Dev1/ai1'
                mean2 = np.mean(selectedrowsPRTare[PRcolumn_name])
                PRinfo = timeseries_std(selectedrowsPRTare[PRcolumn_name], 39999)
                PRstd = PRinfo['data_std_true']  # Pulling out just the standard deviation value
                PRdof = PRinfo['no_dof']  # Pulling out just the degrees of freedom value
                channel_summary.extend([mean2, PRstd, PRdof])  # saving mean

            else: # For all other values we can take pressure reading from raw force spreadsheet
                PRcolumn_name = 'Dev1/ai1'
                mean2 = np.mean(selectedrows[PRcolumn_name])
                PRinfo = timeseries_std(selectedrows[PRcolumn_name], 39999)
                PRstd = PRinfo['data_std_true']  # Pulling out just the standard deviation value
                PRdof = PRinfo['no_dof']  # Pulling out just the degrees of freedom value
                channel_summary.extend([mean2,PRstd,PRdof]) #saving mean

            # print(channel_summary)

            columns = [
                'RunID',
                'Dev2/ai0mean', 'Dev2/ai0sd', 'Dev2/ai0df',
                'Dev2/ai1mean', 'Dev2/ai1sd', 'Dev2/ai1df',
                'Dev2/ai2mean', 'Dev2/ai2sd', 'Dev2/ai2df',
                'Dev2/ai3mean', 'Dev2/ai3sd', 'Dev2/ai3df',
                'Dev2/ai4mean', 'Dev2/ai4sd', 'Dev2/ai4df',
                'Dev2/ai5mean', 'Dev2/ai5sd', 'Dev2/ai5df',
                'Dev1/ai1mean', 'Dev1/ai1sd', 'Dev1/ai1df'
            ]
            channel_summary = np.array(channel_summary).reshape(1, -1)
            Data = pd.DataFrame(channel_summary, columns=columns)
            voltage_summary = pd.concat([Data, voltage_summary], axis=0)

        # Save voltage_summary as CSV
        print('voltagesummary',trialID,frame,reynolds)
        voltage_summary.to_csv(f'VoltageSummary/TRIALID{trialID}FRAMEID{frame}_{reynolds}_VoltageSummary.csv', index=False)

################ FORCE INFO

# This collates the mean and sd of FORCE data
# This creates the 6 gage output voltages, converts them to the matrix to get forces.
# I do this with all 40,000 of the values from RawFT to get 40,000 Force of each Fx,Fy etc
# Then from this we can get the mean, sd and df
        
        Tare_apparatus_Force_Data = pd.DataFrame()
        Total_Force_Data = pd.DataFrame()
        
#
#       AIRSPEED STD TEST = 0.1 ish std
# for j in range(1,82):  # This is the max run ID number. Looping through each of these to add the summary stats to dataset.
#     TarePR = RawPR378.loc[RawPR378['RunID'] == 'Tare']['Dev1/ai1']  # Obtain only rows relating to one run
#     condition = RawFT378['RunID'] == str(j)
#
#     FT = RawFT378.loc[condition]
#
#     b_j = TarePR
#     q_j = FT['Dev1/ai1']  # Obtain only rows relating to one run
#
#     # Apply PressureTransducerfunc to each element of b_j and q_j
#     b_j_transformed = PressureTransducerfunc(b_j)
#     q_j_transformed = PressureTransducerfunc(q_j)
#
#     # Replace NaN values with 0 (or any other value you prefer)
#     b_j_transformed = np.nan_to_num(b_j_transformed)
#     q_j_transformed = np.nan_to_num(q_j_transformed)
#
#     # Subtract transformed b_j from transformed q_j
#     Pressure = q_j_transformed - b_j_transformed
#     Temperature = FT['Temperature'].iloc[0]
#     RoomPressure = FT['Room Pressure(inHg)'].iloc[0]
#     Density = densitycalc(FT['Room Pressure(inHg)'].iloc[0],
#                           FT['Temperature'].iloc[0])
#
#     Airspeed_msValue = getAirspeedfunc(Pressure, Density)
#     print(timeseries_std(Airspeed_msValue, 39999)['data_std_true'], j)  # Pulling out just the standard deviation value
        
        for k in range(0,int(len(RawFT['RunID'])/40000)): # This is the max run ID number. Looping through each of these to add the summary stats to dataset.
        # for k in range(0,2):  # testing purposes
            print(k, "Force/TorqueRunID")
            TarePR = RawPR.loc[RawPR['RunID'] == 'Tare']['Dev1/ai1']  # Obtain only rows relating to one run
            Force_info = []
        
            Force_summary = pd.DataFrame(columns=[
                'RunID',
                'Fx', 'Fy', 'Fz',
                'Tx', 'Ty', 'Tz'
            ])
        
            if k == 0:  # RunID 0 is Tare, so we need to take a reading to subtract from everything else to get the final
                # Can't compare 40,000 tares against voltage readings as they aren't excatly pairs made at the same time
                condition = RawFT['RunID'] == str('Tare')
                Force_info.append(str('Tare'))
                Force_info.append(0)
        
            else:
                condition = RawFT['RunID'] == str(k)
                Force_info.append(str(k))
                FT = RawFT.loc[condition]
                Force_info.append(FT.loc[FT.index[0], 'AOA'])
        
            FT = RawFT.loc[condition]
        
            True_ST_G0 = pd.DataFrame(
                {'Dev2/ai0': (FT['Dev2/ai0'].values)})  # This is the gage voltage reading minus the tare value
            True_ST_G1 = pd.DataFrame(
                {'Dev2/ai1': (FT['Dev2/ai1'].values)})  # This is the gage voltage reading minus the tare value
            True_ST_G2 = pd.DataFrame(
                {'Dev2/ai2': (FT['Dev2/ai2'].values)})  # This is the gage voltage reading minus the tare value
            True_ST_G3 = pd.DataFrame(
                {'Dev2/ai3': (FT['Dev2/ai3'].values)})  # This is the gage voltage reading minus the tare value
            True_ST_G4 = pd.DataFrame(
                {'Dev2/ai4': (FT['Dev2/ai4'].values)})  # This is the gage voltage reading minus the tare value
            True_ST_G5 = pd.DataFrame(
                {'Dev2/ai5': (FT['Dev2/ai5'].values)})  # This is the gage voltage reading minus the tare value
        
            for i in range(0, 40000):
                print(i, "= Repeat/40000", "AOA =", FT['AOA'].iloc[0])
        
                true_ST_matrix = np.array([
                    [True_ST_G0.iloc[i]],
                    [True_ST_G1.iloc[i]],
                    [True_ST_G2.iloc[i]],
                    [True_ST_G3.iloc[i]],
                    [True_ST_G4.iloc[i]],
                    [True_ST_G5.iloc[i]]
                ])
        
                FT_matrix = matrix_multiply(useraxis_runtime_matrix, true_ST_matrix)
                # FT_matrix_Fx = FT_matrix[0][0]  # The first 0 does FT_matrix[0] to get Fx values in a list, then the next [0] pulls from the list to get Fx as an array
                # FT_matrix_Fx_1 = FT_matrix_Fx[0]  # This final [0] gets the first value of the Fx
                # print(FT_matrix_Fx)
        
                Force_summary.loc[i] = [i, FT_matrix[0][0][0], FT_matrix[1][0][0], FT_matrix[2][0][0], FT_matrix[3][0][0],
                                        FT_matrix[4][0][0],
                                        FT_matrix[5][0][0]]
        
            ###### AIRSPEED
            ###### N.B. Jackie performed calculation by taking mean of b_j and q_j before converting to airspeed
            # As such calculation is different to taking difference from 40,000 pairs and then taking the mean
            # See excel spreadsheet to illustrate difference.
            # Taking the mean of b_j and q_j is probably the most fair as cannot be certain they actually
            # truly are pairs.
        
            b_jmean = np.mean(TarePR)
            b_jstd = timeseries_std(TarePR, 39999)['data_std_true']  # Pulling out just the standard deviation value
            q_jmean = np.mean(FT['Dev1/ai1'])  # Obtain only rows relating to one run
            q_jstd = timeseries_std(FT['Dev1/ai1'], 39999)['data_std_true']  # Pulling out just the standard deviation value
        
            Pressuremean = PressureTransducerfunc(q_jmean) - PressureTransducerfunc(b_jmean)  # Functionally minusing the
            Pressuretransb_jstd = b_jstd * 497.68  # This is just a simplified version of the factor you multiply by in the PressureCalc function
            Pressuretransq_jstd = q_jstd * 497.68
            Pressurestd = sd_add_sub(Pressuretransq_jstd, Pressuretransb_jstd)
        
            Temperature = FT['Temperature'].iloc[0]
            Temperaturesd = 0.025  # Need to make sure to convert to Celsius
            RoomPressure = FT['Room Pressure(inHg)'].iloc[0]
            RoomPressuresd = 0.005
        
            Density = densitycalc(FT['Room Pressure(inHg)'].iloc[0],
                                  FT['Temperature'].iloc[0])  # q = p_atm*3386.39/(286.9*(t_atm+273.15))
            # tempDensitymean1 = (3386.39/(286.9*(Temperature+273.15)))
            Densitysd = sd_mult_div(RoomPressure * 3386.39, RoomPressuresd * 3386.39, 286.9 * (Temperature + 273.15),
                                    286.9 * Temperaturesd, Density)

            Airspeed_msValuemean = getAirspeedfunc(Pressuremean, Density)
            intermediatespeedsd = sd_mult_div(2 * Pressuremean, 2 * Pressurestd, Density, Densitysd, (
                        2 * Pressuremean / Density))  # Have to take an intermediate sd (i.e. before square rooting)
            Airspeed_msValuesd = np.sqrt((0.5 * intermediatespeedsd / (2 * Pressuremean / Density)) ** 2) * Airspeed_msValuemean
            # e.g. b) in https://www.geol.lsu.edu/jlorenzo/geophysics/uncertainties/Uncertaintiespart2.html
        
            dynamicpressuremean = Density * Airspeed_msValuemean * Airspeed_msValuemean / 2
            Airspeedsquaredsd1 = np.sqrt((2 * Airspeed_msValuesd / Airspeed_msValuemean) ** 2) * (
                        Airspeed_msValuemean ** 2)  # Doing in two steps - first just calculating the sd of the airspeed squared bit
            dynamicpressuresd = sd_mult_div(Airspeed_msValuemean ** 2, Airspeedsquaredsd1, Density / 2, Densitysd / 2,
                                            dynamicpressuremean)  # Then propagating the error with density/2 which is the other component

            if frame == 'Tare':
                coefficientmean = 0
                coefficientstd = 0

            else:
                coefficientmean = dynamicpressuremean * findLSA(
                    frame)  # Just made a variable called setframe for testing, but ideally would be cycling through all of them
                coefficientstd = dynamicpressuresd * findLSA(frame)  # just the error bar gets multiplied by the factor

            # print(Force_summary)
        
            for i in range(6):  # Iterating over each of the channels in Daq2 (Force), always want these
                if i == 0:
                    column_name = 'Fx'
                elif i == 1:
                    column_name = 'Fy'
                elif i == 2:
                    column_name = 'Fz'
                elif i == 3:
                    column_name = 'Tx'
                elif i == 4:
                    column_name = 'Ty'
                elif i == 5:
                    column_name = 'Tz'
        
                mean = np.mean(Force_summary[column_name])
                info = timeseries_std(Force_summary[column_name], 39999)  # Running the function on the specific channel
                std = info['data_std_true']  # Pulling out just the standard deviation value
                dof = info['no_dof']  # Pulling out just the degrees of freedom value
                Force_info.extend([mean, std, dof])  # saving mean
        
            if k == 0:
                Force_info.extend([0, 0, 0])  # making sure the columns of airspeed are blank
                Force_info.extend([0, 0, 0])  # making sure columns of coefficient are blank
            else:
                Force_info.extend([Airspeed_msValuemean, Airspeed_msValuesd, 0])  # saving mean
                Force_info.extend([coefficientmean, coefficientstd, 0])  # saving mean
        
            columns = [
                'RunID', 'AOA',
                'Fxmean', 'Fxsd', 'Fxdf',
                'Fymean', 'Fysd', 'Fydf',
                'Fzmean', 'Fzsd', 'Fzdf',
                'Txmean', 'Txsd', 'Txdf',
                'Tymean', 'Tysd', 'Tydf',
                'Tzmean', 'Tzsd', 'Tzdf',
                'Airspeed(m/s)mean', 'Airspeed(m/s)sd', 'Airspeed(m/s)df',
                'coefficientmean', 'coefficientsd', 'coefficientdf',
            ]
        
            Force_info = np.array(Force_info).reshape(1, -1)
            Data = pd.DataFrame(Force_info, columns=columns)
            Total_Force_Data = pd.concat([Data, Total_Force_Data], axis=0)
            # Calculate the forces & torque by multiply those 2 true_ST_matrix and useraxis_runtime_matrix
            # Note: Using the first "Axis Matrix" in the .CAL file as the runtime matrix, which is raw_runtime_matrix in this case.
        
        # print(Total_Force_Data)
        # Save Force_summary as CSV
        print('forcesummary',trialID, frame, reynolds)
        Total_Force_Data.to_csv(f'ForceSummary/TRIALID{trialID}FRAMEID{frame}_{reynolds}_ForceSummary.csv',
                               index=False)

        # print(FT_matrix)
        
        ################ LIFT_INFO
        
        # This collates the mean and sd of LIFT, using the Total_Force_Data dataset to get there
        
        Total_TAForce_Data = Total_Force_Data.copy()
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
                Total_TAForce_Data[column] = Total_TAForce_Data[column] - TARETotal_Force_Data_mean[column]
        
        # Print the modified dataframe
        Total_TAForce_Data = Total_TAForce_Data.drop(index=Total_TAForce_Data.index[-1])
        Total_TAForce_Data.iloc[:, :] = Total_TAForce_Data.iloc[:, :].apply(pd.to_numeric)
        
        # print(Total_TAForce_Data)
        # print(Total_TAForce_Data.columns)
        
        Lift_summary = pd.DataFrame(columns=[
            'RunID', 'AOA',
            'LIFTmean', 'LIFTsd'])
        #     'CLIFTmean', 'CLIFTsd',
        #     'CMOMmean', 'CMOMsd',
        #     'CMOMcgmean', 'CMOMcgsd'
        # ])
        # CG Location
        CG = 0.512242294 + 0.2
        Rod = 0.3913
        dist = Rod - CG  # Need to check this is the right calculation
        
        for i in range(0, len(Total_TAForce_Data)):
            # print(i)
            # print(Total_TAForce_Data.loc[i,'Fxmean'])
            # print(Total_TAForce_Data.loc[i,'AOA'])
            if frame == 401: # Because this is left hand wing, lift acts in positive Y, and drag in positive X.
                LIFTvalmean = (Total_TAForce_Data.loc[i, 'Fymean'] * np.cos(np.radians(Total_TAForce_Data.loc[i, 'AOA']))) - (
                            Total_TAForce_Data.loc[i, 'Fxmean'] * np.sin(np.radians(Total_TAForce_Data.loc[
                                                                                        i, 'AOA'])))  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
                LIFTvalsd = sd_add_sub(Total_TAForce_Data.loc[i, 'Fysd'] * np.cos(np.radians(Total_TAForce_Data.loc[i, 'AOA'])),
                                       Total_TAForce_Data.loc[i, 'Fxsd'] * np.sin(np.radians(Total_TAForce_Data.loc[
                                                                                                 i, 'AOA'])))  # Can't really quantify the amount of error on the AOA
            else:
                LIFTvalmean = (-Total_TAForce_Data.loc[i, 'Fymean'] * np.cos(
                    np.radians(Total_TAForce_Data.loc[i, 'AOA']))) - (
                                      Total_TAForce_Data.loc[i, 'Fxmean'] * np.sin(np.radians(Total_TAForce_Data.loc[
                                                                                                  i, 'AOA'])))  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
                LIFTvalsd = sd_add_sub(
                    Total_TAForce_Data.loc[i, 'Fysd'] * np.cos(np.radians(Total_TAForce_Data.loc[i, 'AOA'])),
                    Total_TAForce_Data.loc[i, 'Fxsd'] * np.sin(np.radians(Total_TAForce_Data.loc[
                                                                              i, 'AOA'])))  # Can't really quantify the amount of error on the AOA
            # Might be worth getting dummy data and seeing how sensitive to the AOA uncertainty we have our findings actually are

        ######### HAVE TO STOP HERE SO THAT YOU CAN MINUS THE LIFT MEASURED IN TARE APPARATUS RUNS

            # CLIFTvalmean = LIFTvalmean / Total_TAForce_Data.loc[
            #     i, 'coefficientmean']  # Equation to calculate lift. N.B. lift acts in -Y direction, and drag acts in +X direction
            # CLIFTvalsd = sd_mult_div(LIFTvalmean, LIFTvalsd, Total_TAForce_Data.loc[i, 'coefficientmean'],
            #                          Total_TAForce_Data.loc[i, 'coefficientsd'], CLIFTvalmean)
            #
            # CMOMvalmean = Total_TAForce_Data.loc[i, 'Tzmean'] / (Total_TAForce_Data.loc[
            #                                                          i, 'coefficientmean'] * 0.1679)  # Equation involves dividing by chord length as well
            # CMOMvalsd = sd_mult_div(Total_TAForce_Data.loc[i, 'Tzmean'], Total_TAForce_Data.loc[i, 'Tzsd'],
            #                         (Total_TAForce_Data.loc[i, 'coefficientmean'] * 0.1679),
            #                         (Total_TAForce_Data.loc[i, 'coefficientsd'] * 0.1679), CMOMvalmean)
            #
            # CMOMcgvalmean = CMOMvalmean - (CLIFTvalmean * (dist))
            # CMOMcgvalsd = sd_add_sub(CMOMvalsd, CLIFTvalsd * (dist))
        
            Lift_summary.loc[i] = (Total_TAForce_Data.loc[i, 'RunID'], Total_TAForce_Data.loc[i, 'AOA'],
                                   LIFTvalmean, LIFTvalsd)
            #CLIFTvalmean, CLIFTvalsd,CMOMvalmean, CMOMvalsd, CMOMcgvalmean, CMOMcgvalsd)
        
        # print(Lift_summary)
        print('liftsummary',trialID, frame, reynolds)
        Lift_summary.to_csv(f'LiftSummary/TRIALID{trialID}FRAMEID{frame}_{reynolds}_LiftSummary.csv',
                                index=False)


Lift_summary = SMcalc(Lift_summary)
print(Lift_summary)
####### SM calc


print('end')
