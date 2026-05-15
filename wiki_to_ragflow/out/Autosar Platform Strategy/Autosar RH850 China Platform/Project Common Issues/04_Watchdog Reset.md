# 04_Watchdog Reset

> Source: /spaces/CARSFW/pages/2412005807/04_Watchdog+Reset
> Last modified: 2023-04-13T08:49:49.000+02:00

---

Issue 1 - Watchdog Reset during start up due to Secure boot Information Analysis Solution Fix Status

## Issue 1 - Watchdog Reset during start up due to Secure boot

### Information

| Found in Project | GWM V3.5 | RTC Ticket |  |
| --- | --- | --- | --- |

### Analysis

When secure boot is enabled, the ICUM core will calculate the CMAC for Application Hex during startup.

When SecOC is enabled, the application(HOST core) will requset the CMAC calculation from ICUM core, and the calculation is a synchronized call.

There is a possibility, HOST core requested SecOC CMAC calculation when the ICUM is still calculation the CMAC for Application Hex.  This operation will

lead the HOST core pending in waiting for the CMAC calculation result , finally watchdog timeout will happen.

### Solution

Relax the watchdog supervision during startup phase.

### Fix Status

| Affected Project | Fix Status | linkage |
| --- | --- | --- |
| GWM V3.5 | COMPLETED | https://rbcm-gerrit.de.bosch.com/q/topic:sop9_wdg_fix |
