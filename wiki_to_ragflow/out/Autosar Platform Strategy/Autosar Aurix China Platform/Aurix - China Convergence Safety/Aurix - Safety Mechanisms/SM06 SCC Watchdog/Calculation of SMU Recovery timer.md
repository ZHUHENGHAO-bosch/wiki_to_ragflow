# Calculation of SMU Recovery timer

> Source: /spaces/CARSFW/pages/3409161982/Calculation+of+SMU+Recovery+timer
> Last modified: 2023-09-04T11:37:10.000+02:00

---

## Overview

Below wiki page explains the recovery timer relation with SCU Watch dogs

SMU Recovery Timer - XC-CT China - Docupedia (bosch.com)

This wiki page explains how the timeout value is calculated for recovery timer

### Default value of Recovery timer registers

![](../../../../../_images/Calculation%20of%20SMU%20Recovery%20timer/image-2023-9-4_16-35-46.png)

### Calculation of recovery timer

Recovery time duration = RTC.RTD * FSMU_FS tick time

FSMU_FS tick time =1/FSMU_FS Clock

FSMU_FS Clock= fBACK/FSP.PRE1

fBACK=100MHZ ( internal clock )

### Initial clock value after reset

![](../../../../../_images/Calculation%20of%20SMU%20Recovery%20timer/image-2023-9-4_17-0-3.png)

### Recovery timer value after Reset

Recovery timer initial duration = (0x3FFF * 2)/100 MHz = 32,766/100 MHz = 0.3 ms

### Recovery timer configuration for 20ms

o get the recovery time as 20ms the value to be configured is:

RTC.RTD=Recovery time duration / FSMU_FS tick time

=20ms/ (1/(100MHz/2))

=20ms * (100MHz/2)

=0.02 * 50000000

=1000000  = F4240
