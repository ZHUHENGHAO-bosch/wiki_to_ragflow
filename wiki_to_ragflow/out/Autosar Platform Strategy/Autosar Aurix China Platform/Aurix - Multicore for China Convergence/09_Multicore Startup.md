# 09_Multicore Startup

> Source: /spaces/CARSFW/pages/2396097886/09_Multicore+Startup
> Last modified: 2024-01-29T07:53:24.000+01:00

---

## Overview

- Startup code needs to be executed before calling main
- In Multicore architecture, all cores has to execute startup code
- Only Master Core starts automatically on power up, Slave cores has to be started by the OS in master core

![](../../../_images/09_Multicore%20Startup/EcuM_StartPhase.jpg)

### Init Task Synchronization

![](../../../_images/09_Multicore%20Startup/MultiCore_StartupPhase_InitTaskSynchronization.bmp)
