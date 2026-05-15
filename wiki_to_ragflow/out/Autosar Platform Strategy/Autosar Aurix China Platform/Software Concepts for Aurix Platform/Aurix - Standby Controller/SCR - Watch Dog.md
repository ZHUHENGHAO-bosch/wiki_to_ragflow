# SCR - Watch Dog

> Source: /spaces/CARSFW/pages/2356658925/SCR+-+Watch+Dog
> Last modified: 2022-08-05T08:53:03.000+02:00

---

## Overview:

Since we depend on SCR to wake the system from Standby mode, it is important to make sure the SCR code is properly running in XC800 CPU

### Features of SCR WDT:

- 16 bit WDT Timer
- Programmable Window boundary
- Can run in 70 kHz Clock

The Watchdog Timer maintains a counter which must be refreshed or cleared periodically. Otherwise, the counter will overflow and the watchdog reset will be asserted

> **INFO**
> The assertion of the reset could be disabled by setting bit RSTCON.WDTRSTEN. The occurrence of a WDT reset is indicated by the bit WDTRST in RSTST register

In the SCR, it is possible to wake-up the main controller from standby mode when the WDT overflow event happened by setting bit STDBYWKP.WDTWKSEL to 1 .

### NMI

Before SCR WDT triggers the Reset, NMI will be triggered where we can log some critical information to Error Memory

![](../../../../_images/SCR%20-%20Watch%20Dog/image2022-8-5_12-7-6.png)

### SCR WDT Block Diagram

![](../../../../_images/SCR%20-%20Watch%20Dog/image2022-8-5_12-7-37.png)

### Programmable window boundary

The WDT has a “programmable window boundary”, which disallows any refresh during the WDT’s count-up. A refresh during this window-boundary constitutes an invalid access to the WDT and causes the WDT to activate WDTRST

This feature can be enabled by WINBEN bit in Watchdog Timer Control Register

![](../../../../_images/SCR%20-%20Watch%20Dog/image2022-8-5_12-12-5.png)

### Calculation of WDT timeout value

![](../../../../_images/SCR%20-%20Watch%20Dog/image2022-8-5_12-10-58.png)

Example,

![](../../../../_images/SCR%20-%20Watch%20Dog/image2022-8-5_12-11-19.png)
