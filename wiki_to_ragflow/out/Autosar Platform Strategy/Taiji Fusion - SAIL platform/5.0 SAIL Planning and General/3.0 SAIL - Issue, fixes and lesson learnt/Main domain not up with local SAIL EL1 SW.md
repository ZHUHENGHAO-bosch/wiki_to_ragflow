# Main domain not up with local SAIL EL1 SW

> Source: /spaces/CARSFW/pages/4916784506/Main+domain+not+up+with+local+SAIL+EL1+SW
> Last modified: 2024-10-29T02:28:43.000+01:00

---

## Overview

When we use the local built SAIL El1 SW, the MD is not working fine with version

But when we use the elf generated with QC bare metal code, MD is up and running

### Failure logs with Local built SW:

Errors will come in UART like below and after this the UART in MD is non responsive

![](../../../../_images/Main%20domain%20not%20up%20with%20local%20SAIL%20EL1%20SW/image-2024-10-25_10-37-43.png)

### Boot Process and dependency with SAIL

3.0 SAIL Boot sequence - XC-CT China - Docupedia (bosch.com)

Only SAIL Hypervisor has dependency with MD, EL1 SW has no dependency

### Test with Multicore Autosar hypervisor and SoC

SoC version tested: rb-vcupro_main_dev_2024.42.5_userdebug.

With the above SoC and SAIL El1 SW built in local with QC multicore hypervisor → MD runs properly with no reset, UART is responsive and displays are up

![](../../../../_images/Main%20domain%20not%20up%20with%20local%20SAIL%20EL1%20SW/image-2024-10-25_10-48-14.png)

![](../../../../_images/Main%20domain%20not%20up%20with%20local%20SAIL%20EL1%20SW/image-2024-10-25_10-48-28.png)
