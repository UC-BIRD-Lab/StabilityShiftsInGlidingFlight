# Stability shifts in gliding flight: Hawks morph from an unstable to stable state when navigating a gap
**Journal of the Royal Society Interface**, 2026 — [Paper](https://doi.org/xxxx)

Kiran Weston<sup>1</sup>, Huanglun Adam Zhu<sup>2</sup>, Graham Keith Taylor<sup>1</sup>, Christina Harvey<sup>2*</sup>

<sup>1</sup>*University of Oxford*, <sup>2</sup>*University of California, Davis*  
<sup>*</sup>Corresponding author

<img width="1000" alt="image" src="https://github.com/user-attachments/assets/1df003e9-3b66-48fe-a2a4-a736336b5c32" />
A Harris’s hawk (a) was fitted with retroreflective markers at relevant physiological locations to provide a wing and tail outline. The subject was recorded flying between two perches placed 14 m apart down the length of the Oxford Flight lab flight hall.

---

## Abstract
Birds control their flight by morphing their wing and tail configurations as they shift between steady glides and agile manoeuvres. Cadaveric studies have shown that birds have the capacity to adopt both stable and unstable configurations, but it remains unknown how birds exploit this ability in flight. Here, we fill this gap by studying the progression of wing and tail configurations of a free-gliding Harris’s hawk (*Parabuteo unicinctus*) during a wing-tucking manoeuvre. Wind tunnel experiments on three-dimensional-printed models revealed that tucked configurations were statically stable, while spread configurations displayed a nonlinear relationship between pitching moment and lift. This nonlinearity allows configurations to be either stable or unstable depending on the lift state, affording a previously under-explored source of flight performance flexibility. Furthermore, we found that the hawk transitioned from an unstable, spread configuration to a stable, tucked configuration as it traversed the gap, shifting the effective static margin from −25% to 19% of the reference chord. This notable stability shift suggests that adaptive flight control allows transition between flight modes and offers insight into flight conditions where shifting stability states may be relevant. This outcome will advance novel bio-inspired, fixed-wing uncrewed aerial vehicle designs capable of rapid transitions.

## Citation
```bibtex
@article{weston-2026,
  title   = {Stability shifts in gliding flight: Hawks morph from an unstable to stable state when navigating a gap},
  author  = {Weston, K. and Zhu, H. and Taylor, G.K. and Harvey, C.},
  journal = {Journal of the Royal Society Interface},
  year    = {2026},
  doi     = {10.1098/rsif.2025.0868}
}
```

## Environment reproduction
Clone the repository:
```
git clone git@github.com:UC-BIRD-Lab/StabilityShiftsInGlidingFlight.git
cd StabilityShiftsInGlidingFlight
```
Create a python virtual environment using `pip` from the supplied `requirements.txt` file:
```
pip install -r requirements.txt
```

## Code Summary

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

This repository includes files for the processing of raw wind tunnel data with more detailed file descriptions at the top of each script
