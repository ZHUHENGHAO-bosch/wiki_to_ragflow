# 03_Autosar - Multicore OS

> Source: /spaces/CARSFW/pages/2383058131/03_Autosar+-+Multicore+OS
> Last modified: 2024-09-25T16:09:28.000+02:00

---

## Overview

To support Multicore, OS has the below features

- The OS has a kernel on each Core
- OS is based on Asymmetric Multi-Processing (AMP)
- Scheduling on all cores is independent

## Startup

The way cores are started depends heavily on the hardware. Typically the hardware only starts one core, referred as the master core, while the other cores (slaves) remain in halt state until they are activated by the software. - Aurix Startup is done as per this statement

In Multi-Core configurations, each slave core that is used by AUTOSAR must be activated before StartOS is entered on the core

### Startup Synchronization

![](../../../_images/03_Autosar%20-%20Multicore%20OS/image2022-8-10_16-58-1.png)

StartOS synchronizes all cores twice. The first synchronization point is located before the StartupHooks are executed, the second after the OS-Application specific StartupHooks have finished and before the scheduler is started

### Shutdown Synchronization

AUTOSAR supports two shutdown concepts

- the synchronized shutdown.
- the individual shutdown concept

The synchronized shutdown is triggered by the new API function ShutdownAllCores() , the individual shutdown is invoked by the existing API function ShutdownOS() .

![](../../../_images/03_Autosar%20-%20Multicore%20OS/image2022-8-10_16-59-15.png)

`

> **INFO**
> Individual shutdown is not supported in AUTOSAR R4.x
