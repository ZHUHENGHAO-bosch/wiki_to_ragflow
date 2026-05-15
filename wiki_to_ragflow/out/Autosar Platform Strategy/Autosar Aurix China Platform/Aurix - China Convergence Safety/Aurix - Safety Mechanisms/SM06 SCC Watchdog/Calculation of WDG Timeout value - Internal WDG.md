# Calculation of WDG Timeout value - Internal WDG

> Source: /spaces/CARSFW/pages/3409159425/Calculation+of+WDG+Timeout+value+-+Internal+WDG
> Last modified: 2023-09-04T11:41:41.000+02:00

---

## Overview

CPU WDG will start automatically during Power ON or wakeup. Recovery timer will also start along with CPU watchdog and default Reset for SMU Recovery timer will be Application Reset

### Calculation of WDG Timeout with reload value

Formula for WDG timeout is.

WDG Period = ((2^16- Reload Value ) *divider)/ fSPB

Divider value can be 64, 256, 16384

fSPB - System Peripheral Bus clock value

For example, If the reload value is 0xFE00 with clock configuration of fSPB as 100 MHz and divider value as 16384

![](../../../../../_images/Calculation%20of%20WDG%20Timeout%20value%20-%20Internal%20WDG/image-2023-9-4_15-43-45.png)

The WDG timeout value is

WDG timeout = (( 0x10000 - 0xFE00) * 16384)/100 MHz = 8388608/100000000 = 0.08388 seconds = 83ms = ~80 ms

### WDG default timeout after Reset

WDG Period = ((2^16- Reload Value ) *divider)/ fSPB

= ((0x10000 - 0xFFFC) * 16384)/50 MHz = 0.0013 seconds = 1.3 ms
