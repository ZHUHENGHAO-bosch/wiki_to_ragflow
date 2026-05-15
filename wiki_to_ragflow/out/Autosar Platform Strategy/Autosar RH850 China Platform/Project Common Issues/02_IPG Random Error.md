# 02_IPG Random Error

> Source: /spaces/CARSFW/pages/2412005815/02_IPG+Random+Error
> Last modified: 2023-04-03T10:46:36.000+02:00

---

### Information

IPG, Internal Peripheral Guard, is part of Slave guard from Fusa. IPG is used for protecting the registers of peripherals in RH850 against invaild accesses. More details about IPG, refer to 3BC.2.3.2 in RH850 Hardware User's Manual.

When IPG permission configuration is violated in runtime, SYSERR will be raised and then reset.

The IPG Random Error occurred in VCU and GWM project.

### Analysis

The root cause is RH850 HW bug, More details can be found in IPG Issue Investigated In VCU Project .

### Solution

Since the IPG can also detect speculative instrution fetches which are causing unforeseen issues. The execution violation detection is deactivated. However the MPU still coveres the execution violation detection on the P-BUS.

### Fix Status

| Affected Project | FixStatus | RTC/Gerrit Linkage |
| --- | --- | --- |
| GWM V3.5 | COMPLETED | https://rbcm-gerrit.de.bosch.com/plugins/gitiles/projects/gwm/v35/autosar/autosar/bosch/+/1a2d83b7d0589458df95baf0a1edf732bfb788c5 |
| GEELY | COMPLETED |  |
| GAC | COMPLETED |  |
| BYD |  |  |
