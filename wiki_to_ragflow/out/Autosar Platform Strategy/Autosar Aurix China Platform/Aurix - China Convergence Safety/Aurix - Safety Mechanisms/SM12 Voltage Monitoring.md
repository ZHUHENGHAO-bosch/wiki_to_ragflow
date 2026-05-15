# SM12 Voltage Monitoring

> Source: /spaces/CARSFW/pages/2411019829/SM12+Voltage+Monitoring
> Last modified: 2023-05-15T10:05:38.000+02:00

---

## Overview

We need to monitor the supply of the devices which comes in the safety path.

- Internal voltage monitoring
- External voltage monitoring

> **INFO**
> Need to check whether on the item level we can decompose the voltage monitoring as QM - based on System safety analysis of each project For example, if we have a safe SW telltale as safety goal and if we have Display ECU as ASIL B then we can decompose like ASIL-B UBAT_SNS = ASIL-B Display-ECU CAN monitoring + QM(B) UBAT_SNS Monitoring

### Internal voltage monitoring

Aurix has primary and secondary monitors to meet safety requirements

Refer this wiki for more details on Aurix Power Management System - Aurix - PMS (Power Management System) - XC-CI China - Docupedia (bosch.com)

Refer this wiki for more details on voltage monitoring mechanism - Voltage Monitoring - Aurix's internal voltage monitoring research - XC-CT Cerberus Platform - Docupedia (bosch.com)

![](../../../../_images/SM12%20Voltage%20Monitoring/SM10%20PowerVoltage%20Monitoring.bmp)

### External Voltage monitoring

Which ADC signals to be monitored has to come from System Safety Analysis

Need to have SafeVoltageMonitor as an framework module  and ADC signal to monitor shall be in scope of project configuration

PGOOD comparator itself is QM HW complaint - so we don't need to monitor PGOOD in Safe Context but LCM will monitor PGOOD signals in QM context

ADC-based monitor takes precedence over power-good evaluation because the power-good thresholds alone are too relaxed, for some of these voltage rails

Do we need to monitor U33R_CPU (SCC_U33R_CPU_FAULT_B_3V3) → Not needed

We need

- a safety path at System level
- HW Power rail
- System Safety Analysis

We may kick out most of the monitoring based on the analysis

Safe External voltage monitor shall check the SoC State and shall do a reset only is SoC State is not SOC_POWER_OFF (Because QM LCM shall power down SoC and enters SCC-Only mode in case UV/OV conditions). If this fails then Safety Can do a Safe Reset.

Need to make sure the threshold values for debounce time shall match QM LCM time to enter SCC-Only mode

> **INFO: Zeekr requirement**
> Zeekr System requirement is to monitor the below voltage rail U33P - UBAT_SNS -

![](../../../../_images/SM12%20Voltage%20Monitoring/SM12%20External%20Voltage%20Monitor.bmp)
