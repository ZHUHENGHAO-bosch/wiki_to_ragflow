# 4.0 Turn Signal Indicator

> Source: /spaces/CARSFW/pages/4593457305/4.0+Turn+Signal+Indicator
> Last modified: 2026-03-16T06:26:58.000+01:00

---

## Overview

This page is to summarize the requirement and analysis of Turn Signal indicator of VCU Plus

### Turn Indicator Sequence

- Whenever the Turn indicator CAN message arrived, a callback to Turn Telltale SWC is called from COM via RTE. In the callback we will set the timer for turn indicator
- In a cyclic runnable, we will check if the timer of any of the Turn telltale is ON, if yes then we will go further into checking conditions
- If the condition like Power mode, CAN message and others are met, the call to update FU class will be called to send message to HMI

![](../../../../../_images/4.0%20Turn%20Signal%20Indicator/TurnIndications.jpg)

![](../../../../../_images/4.0%20Turn%20Signal%20Indicator/image-2026-3-16_13-26-42.png)
