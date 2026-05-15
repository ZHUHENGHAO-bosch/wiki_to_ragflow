# Aurix - Boot time framework

> Source: /spaces/CARSFW/pages/2453410376/Aurix+-+Boot+time+framework
> Last modified: 2022-10-10T08:05:58.000+02:00

---

## Overview

Since we have the requirement of sending first CAN message within 100ms after wakeup and SoC should be powered up within 250ms in China Convergence projects, there is a need for a framework which help us to measure boot time at each stage in startup sequence

> **INFO**
> Most projects have CAN boot time requirement as 100ms and SoC Power up time as 250ms but in some project we can get a waiver to a practically possible one after the discussion with Customer

![](../../../../_images/Aurix%20-%20Boot%20time%20framework/Boottime%20measurement.png)

- HSM, BM and application startup code should have a provision to measure the boot time via Port pin
- Ecu Mode Manager shall support a provision to get the time taken for each state transition
