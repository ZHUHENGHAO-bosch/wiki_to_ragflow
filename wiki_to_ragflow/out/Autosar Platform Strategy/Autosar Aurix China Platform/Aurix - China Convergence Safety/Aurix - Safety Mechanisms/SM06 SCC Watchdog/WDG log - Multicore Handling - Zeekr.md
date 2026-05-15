# WDG log - Multicore Handling - Zeekr

> Source: /spaces/CARSFW/pages/3435213310/WDG+log+-+Multicore+Handling+-+Zeekr
> Last modified: 2023-09-11T04:57:13.000+02:00

---

### Overview - Problem statement

In current design, all WDG alarms are mapped to CPU0 NMI alarm in SMU. But the PCXI of slave core cannot be read by master core.

Due to this we cannot store the call stack information of WDG errors in Core 1 and Core 2

### Solution

Below diagram explains the solution to above problem statement where we use SMU interrupts instead of NMI for Core 1 and Core 2 CPU WDGs

![](../../../../../_images/WDG%20log%20-%20Multicore%20Handling%20-%20Zeekr/InternalWDGHandling.bmp)
