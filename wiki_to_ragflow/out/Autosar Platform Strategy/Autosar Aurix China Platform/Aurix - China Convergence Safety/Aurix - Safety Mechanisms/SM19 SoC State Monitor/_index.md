# SM19 SoC State Monitor

> Source: /spaces/CARSFW/pages/2509826406/SM19+SoC+State+Monitor
> Last modified: 2023-02-22T03:08:50.000+01:00

---

## Overview

In local projects, SoC State monitor is part of SM52-Safe HMI Monitor as shown in below picture

SM52 Safe HMI Monitor - XC-CT China - Docupedia (bosch.com)

### Soc State Monitor Context view

![](../../../../../_images/SM19%20SoC%20State%20Monitor/SM19%20SoC%20State%20Monitor%20-%20Context%20Overview.bmp)

### SoC State Monitor States

In Local projects below are the states of Soc State Monitor

| State | Entry Condition |
| --- | --- |
| SSM_SoC_UNDEFINED | Initial State |
| SSM_SoC_PowerOFF | PS_HOLD and STR_MODE ((PS_HOLD == LOW && STR_MODE == LOW)) \|\| (PS_HOLD == HIGH && STR_MODE == HIGH)) |
| SSM_SoC_PowerON | PS_HOLD and STR_MODE ((PS_HOLD == HIGH) && (STR_MODE == LOW)) |
| SSM_SoC_PowerON_BootNormal | INC Message with status as SSM_BOOTMODEINDICATION_NORMAL |
| SSM_SoC_PowerON_BootRecovery | INC Message with status  asSSM_BOOTMODEINDICATION_RECOVERY |
| SSM_Fault | PMIC Fault Init timeout Boot mode message reception timeout Invalid Boot mode status in INC message |
