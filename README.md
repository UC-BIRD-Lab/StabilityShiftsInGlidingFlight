# Stability shifts in gliding flight: Hawks morph from an unstable to stable state when navigating a gap
This repository includes files for the processing of raw wind tunnel data with more detailed file descriptions at the top of each script

ERRORCALCULATION SCRIPTS - written specifically for this project but can be made general 

1) LiftErrorToCsV
     This script calculates the voltages and force reading mean, sd and df for each time point and       outputs them as a new csv.  This is based on RawDataErrorCalc
2) CoefficientLiftErrorToCsV
     This calculates the Lift and CL, CMcg etc mean and sd. This uses the outputs from                  LiftErrorToCSV so that we can account for TARE runs of wind tunnel apparatus when                  calculating LIFT. This is based on RawDataErrorCalc
3) TunnelDataClean
      Code to fix the errors documented in windtunnel data description that were due to incorrect        manual input. This should be run first if necessary

GRAPHING SCRIPTS

1) CLIFTerrorPlots
      This plots CMcga/CLa with appropriate error bars of all frames on same graph
2) MeanStaticMarginPlot
      This plots the mean static margin against configuration for a given reynolds mode
3) HarveyStaticMarginGraph
      This plots the maximum static margin range against other species from Harvey et al., 2022
      This requires manual creation of a spreadsheet to be read in with SM bounds. 
4) WingspanGapApproach *detailed in thesis work*
      This plots wingspan against distance to gap but requires data not generated here




TESTING SCRIPTS

1) RawDataErrorCalc
      Testing Code used to correct for autocorrelation and calculate standard deviation error from       RFT and RPR files

2) ForceTorquePlot
      Code used to plot Lift and Drag against angle of attack, CL and CD against angle of attack,        CL against angle of attack and finally CL/Cm

3) VoltageCheck
   Code used to check the voltages of the underlying pressure and force/torque data

5) CMCL_compare
   Code that plots CM against CL for all frames (medium reynolds)

6) SensitivityAnalysis
   This code calculates CMcg and subsequently CMcgalpha/CLalpha at every angle of attack to           compare the static margin change.
   This reuses code sections of ForceTorquePlot and CMCL_compare
