# Cyclic Monitoring of AG2i_STDBY Registers

> Source: /spaces/CARSFW/pages/2916353702/Cyclic+Monitoring+of+AG2i_STDBY+Registers
> Last modified: 2023-04-04T04:45:40.000+02:00

---

### Introduction

We can see Clock monitor cyclically checks AG2i_STDBY registers and in case of any failure it will trigger a SMU SW alarm ALM10[0]

##### Why is this needed?

IFX recommends to cyclically monitor AG_STANBY registers.

SM[HW]:CLOCK:ALIVE_MONITOR

Monitor the activity of the following clocks

![](../../../../../_images/Cyclic%20Monitoring%20of%20AG2i_STDBY%20Registers/image-2023-4-4_10-42-47.png)

![](../../../../../_images/Cyclic%20Monitoring%20of%20AG2i_STDBY%20Registers/image-2023-4-4_10-44-11.png)
