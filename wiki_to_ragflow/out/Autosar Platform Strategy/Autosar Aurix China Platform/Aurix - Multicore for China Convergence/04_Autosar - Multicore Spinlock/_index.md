# 04_Autosar - Multicore Spinlock

> Source: /spaces/CARSFW/pages/2384995023/04_Autosar+-+Multicore+Spinlock
> Last modified: 2023-04-05T05:10:58.000+02:00

---

## Overview

With the Multi-Core concept, a new mechanism is needed to support mutual exclusion for TASKS on different cores. This new mechanism shall not be used between TASKs on the same core because it makes no sense. In such cases the AUTOSAR Operating System returns an error

A spinlock is a busy waiting mechanism that polls a (lock) variable until it becomes available

Once a lock variable is occupied by a TASK/ISR2, other TASKs/ISR2s on other cores shall be unable to occupy the lock variable

### Spinlocks to Synchronize Cores

![](../../../../_images/04_Autosar%20-%20Multicore%20Spinlock/image2022-8-10_17-5-37.png)
