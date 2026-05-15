# Aurix - Need for External Watchdog

> Source: /spaces/CARSFW/pages/2365867175/Aurix+-+Need+for+External+Watchdog
> Last modified: 2022-08-25T10:46:20.000+02:00

---

### Overview

Aurix has two internal watchdogs

- CPU Watchdog
- Safety Watchdog

But they share the clock reference from CCU (Clock Control Unit), So in case of failures like when MCU not active due to issue in Power Management system, it is not possible to detect these errors with internal watch dogs

Hence we need an external watchdog with separate reference clock which supervises Aurix as shown below (To reduce the Common mode Failure)

#### Decision: Whether to use external Watchdog for China convergence projects ? and if yes which ASIC to use as an external watchdog ??

Confirmed we need ASIL qualified external Watchdog for China convergence projects based on Aurix

> **INFO**
> Note: In CI2 projects, it is confirmed we need to use External Watchdog to achieve safety at system level ( MAX20479 will be the one used in future in CI2 projects)

Create an SM to handle it is decided to use an external Watchdog

![](../../../../../_images/Aurix%20-%20Need%20for%20External%20Watchdog/image2022-7-26_12-25-19.png)

![](../../../../../_images/Aurix%20-%20Need%20for%20External%20Watchdog/image2022-7-26_12-25-34.png)

### Clock reference of internal Watchdog from CCU

![](../../../../../_images/Aurix%20-%20Need%20for%20External%20Watchdog/image2022-7-26_12-26-7.png)
