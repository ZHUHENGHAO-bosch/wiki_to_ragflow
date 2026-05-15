# 1.0 VCU Plus SUM_SUSD

> Source: /spaces/CARSFW/pages/4593454612/1.0+VCU+Plus+SUM_SUSD
> Last modified: 2024-08-12T07:33:19.000+02:00

---

## Overview

SUSD - Startup and Shutdown consists for 5 atomic components

- ASM - Application State Manager
- ASS - Application SWC Start/Shutdown
- BVM - Battery Voltage Monitor
- VP - Vehicle Power Mode
- RCP - Run Crank

SUM SUSD is responsible of managing start and shutdown application layer, which includes all the SUMs and other SW-Cs. SUSD also notifies BSW layer to transition to Shutdown state based on notification from project specific SW-Cs

### Applicability of SUM_SUSD

We can see in VCU we will use only ASM, ASS and BVM

![](../../../../../_images/1.0%20VCU%20Plus%20SUM_SUSD/image-2024-8-12_13-31-59.png)

## SUSD Context View

![](../../../../../_images/1.0%20VCU%20Plus%20SUM_SUSD/image-2024-8-12_11-25-54.png)

## Summary of SUSD Sub module Functionalities

| Submodule | Functionality |
| --- | --- |
| Application State Manager | Coordinate the ECUs operational state with BswM (which controls EcuM) Monitor the Power Mode Client Perform the logic to determine when to request a change to the ECU's operational state to BswM (from Run to Sleep, Reset, or Off) Request BswM to shut down (to the shutdown target) when all SW-Cs have enabled shutdown Request BswM to remain in "run" when at least one SW-C has not enabled shutdown |
| Battery Voltage Monitor | Process Battery Voltage Input Monitor Battery Voltage State of Charge serial data signal Provide Notification to SW-C of standardized voltage ranges: Normal, Overvoltage, Undervoltage Provide an actual battery voltage value |
| Application Start / Shutdown | Maintaining list of active ECU initiated system wakeups Mapping of SW-Cs to ECU wakeups Polling of EcuM for wakeup request on behalf of SW-C Coordinator of all SW-C startup notifications Coordinator of all SW-C shutdown notifications Disable / Enable future Wakeups based on the ECU's needs (based on vehicle modes or functional needs) Fault handling mechanism for wakeups, and disable future wakeup source for subsequent cycles Provide Notification to other SW-C to Disable DTCs for <DisableDTCBatteryWakeupPeriod> following wakeup from Battery event |
| Run Crank Functionality | Monitor Run Crank input from local I/O RunCrank Status Calculation based on I/O and Power Moding Inputs Fault Handling with regards to Run Crank detection |
| Power Mode Client | Processing of Signals from Power Mode Master and Backup Power Mode Master Handles Error notification for fault handling of Power Mode Signal Usage PropulsionStatus Notification Calculation of ECU specific power moding state based on internal and external inputs Support Vehicle Power Moded Notification for Application, DIDs etc |
