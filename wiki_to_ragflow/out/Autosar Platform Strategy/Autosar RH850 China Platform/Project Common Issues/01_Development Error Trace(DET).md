# 01_Development Error Trace(DET)

> Source: /spaces/CARSFW/pages/2411995751/01_Development+Error+Trace+DET
> Last modified: 2023-04-03T09:20:10.000+02:00

---

Issue 1 - Watchdog Reset in application Information Analysis Solution Fix Status Issue 2 - Stuck in Bootloader Information Analysis Solution Fix Status

DET means Development Error Tracer in Autosar 4.0 and is renamed to Default Error Tracer in Autosar 4.2.

DET provides functionality to support error detection and tracing of errors during the development of Software Components and other Basic Software Modules. For this purpose DET receives and evaluates error messages from these components and modules. DET is able to provide information need for tracing source and kind of error.

## Issue 1 - Watchdog Reset in application

### Information

| Found in Project | GWM V3.5 | RTC Ticket |  |
| --- | --- | --- | --- |

### Analysis

During development,  once anerror is reported via Det_ReportError interface, the system will enter to endless loop via Det_EndlessLoop interface.

After that, the software can not trigger watchdog and this will result watchdog timeout, finally the system will reset by the HW watchdog.

### Solution

Normally, the DET functionality shall be disabled after SOP, which means the system will not enter to endless loop.

But with this change, some important error information will be lost.

After checked with Vector, it is possible to remove Det_EndlessLoop when issue happened, and it is also possible to store the error information in Det_callouts.

More detail information can be found in slides.

### Fix Status

| Affected Project | Fix Status | RTC/Gerrit linkage |
| --- | --- | --- |
| GWM V3.5 | COMPLETED |  |
| ECARX FX11 | COMPLETED | https://rbcm-gerrit.de.bosch.com/q/topic:%22Det_ReportError%22+(status:open%20OR%20status:merged) |
| GAC A58/A88/A02 | COMPLETED | https://rbcm-gerrit.de.bosch.com/q/topic:%22Det_ReportError%22+(status:open%20OR%20status:merged) |
| BYD DHU | OPEN |  |

## Issue 2 - Stuck in Bootloader

### Information

| Found in Project | ECARX FX11 | RTC Ticket | Story 1530119 |
| --- | --- | --- | --- |

### Analysis

CAN/LIN routing function is enabled in bootloader. And the DET is still enabled in bootloader.

There is a chance to enter to Det_EndlessLoop due to errors in the network.

### Solution

Disable DET functionality in bootloader

TODO： Scenarios in the past:

SharePoint linkage：

### Fix Status

| Affected Project | Fix Status | Gerrit/RTC linkage |
| --- | --- | --- |
| ECARX FX11 | COMPLETED | https://rbcm-gerrit.de.bosch.com/q/topic:%22boot_can-rb-ecarx-dhu_hqx121c1-pcs01_sop2_release%22+(status:open%20OR%20status:merged) |
