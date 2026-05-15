# Aurix - PMS Supply Mode Selection

> Source: /spaces/CARSFW/pages/2377378327/Aurix+-+PMS+Supply+Mode+Selection
> Last modified: 2022-08-05T11:06:40.000+02:00

---

## Overview

The choice of the supply scheme at startup is based on the latched status of HWCFG[2:1] pins before cold PORST release and is indicated by PMSWSTAT.HWCFGEVR status flags

- Single source 5 V supply level (VEXT = 5 V) is supported in following topologies. – EVRC in SMPS mode with external switches and EVR33 in LDO mode with internal pass devices.
- Single source 3.3 V supply level (VEXT = VDDP3 = 3.3 V) is supported in following topologies. – EVRC in SMPS mode with external switches and EVR33 is inactive.

![](../../../../_images/Aurix%20-%20PMS%20Supply%20Mode%20Selection/image2022-8-5_14-36-33.png)
