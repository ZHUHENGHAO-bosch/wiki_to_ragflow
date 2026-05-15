# 09_bootloader array overflow

> Source: /spaces/CARSFW/pages/3024540626/09_bootloader+array+overflow
> Last modified: 2024-11-15T09:47:55.000+01:00

---

| Version | Detail | Date | Author | comment |
| --- | --- | --- | --- | --- |
| V0.1 | first version | 2023.05.31 | user-2cdd2 |  |
|  |  |  |  |  |
|  |  |  |  |  |

## Issue 1 - DLT buffer flow

| Found in Project | ECARX FX11 | RTC Ticket | NA |
| --- | --- | --- | --- |

### Analysis

In the bootloader code, the print function "fbl_tracestring", use teset_data1 buffer to receive the string that will be printed. But the teset_data1 size =1, this array will overflow.

### Solution

Expand the teset_data1 size to 80 bytes.

| Affected Project | Fix Status | Gerrit/RTC linkage |
| --- | --- | --- |
| ECARX FX11 | COMPLETE | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/619669 |
| BYD DX | COMPLETE | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/vector/vector-fbl/+/537095 |
| GWM | LIU Jiqing (ETAS-ECM/XSF-CN) | [GWM][Fbl] fbl trace modify (I4cccde84) · Gerrit Code Review (bosch.com) |
| GAC | GONG Guan (XC-CP/ESW2-CN) | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/vector/vector-fbl/+/688429 |
| ZEEKR CX1E | COMPLETE | https://rbcm-gerrit.de.bosch.com/c/projects/cnconv/Zeekr/Bootloader/Services/ComPlatform/+/613289 |
| CHERY T1J | COMPLETE | Use geely the latest code as base code. |

## Issue 2 - LCM inc request data copy caused array overflow

### Information

| Found in Project | ECARX FX11 | RTC Ticket | RTC1-1766734 |
| --- | --- | --- | --- |

### Analysis

LCM INC request data copy caused array overflow.

There is a chance to decode INC message failed, not run LCM request.

Lcm buffer overflow analysis.pptx

### Solution

Increase length of receive buffer. Recommend to change buffer size to 256 bytes, because max payload is 255 bytes for every INC channel. In Geely, I change size to 40 bytes, it is ok for current case.

| Affected Project | Fix Status | Gerrit/RTC linkage |
| --- | --- | --- |
| ECARX FX11 | COMPLETE | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/bosch/bootloader-services/+/612546 |
| BYD DX | COMPLETE | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/bosch/bootloader-services/+/612840 |
| GWM | LIU Jiqing (ETAS-ECM/XSF-CN) | [GWM][Fbl] fbl trace modify (I4cccde84) · Gerrit Code Review (bosch.com) |
| GAC | GONG Guan (XC-CP/ESW2-CN) | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/bosch/bootloader-services/+/688452 |
| ZEEKR CX1E | WU Qi (XC-CP/ESW2-CN) |  |
| CHERY T1J | LIU Hao (BCSC/ENG1) |  |

## Issue 3 FBL QM Log

| Found in Project | ECARX FX11 | RTC Ticket | RTC1-1767327 |
| --- | --- | --- | --- |

### Analysis

When copying QMErrorlog, the array testQmBuffer exceeded the bounds and the isEnteredProgSession boolean variable was changed to true, resulting in inability to enter the programming session and erase flash failure

### Solution

1. expand testQmBuffer array size to 80 bytes.
2. add array index value check. If the index value exceed the bound value, not copy data.

### Fix Status

| Affected Project | Fix Status | Gerrit/RTC linkage |
| --- | --- | --- |
| BYD DX | COMPLETE | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/vector/vector-fbl/+/612836 |
