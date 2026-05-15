# 3.0 SAIL - Issue, fixes and lesson learnt

> Source: /spaces/CARSFW/pages/4862736891/3.0+SAIL+-+Issue+fixes+and+lesson+learnt
> Last modified: 2024-11-26T12:20:20.000+01:00

---

## Overview

This page is to make note of issues faced in SAIL bringup

PWM (clock) and ICU needed for USS but QC MCAL doesn't support. QC Case created and waiting for reply

Solution 2:

- Use Clock IP block to generate USS clock reference → QC gave Clock register details
- Use BSP code to detect GPIO edge and trigger interrupt

Sail no loading hypervisor doesn't work properly

- Issue1: Can not load big size hypervisor > 400 Kb

- Issue2: It can small size elf <400Kb and MD is up but SAIL software stuck in hypervisor
- This hypervisor has no issue with 8775 - Both issues are gone
- LIU Dezhi (XC-CP/ESW2-CN) Will ask QC any dependency of their released hypervisor with 8225 and 8775

Hyp with workaround for 8255: Both the above issue is gone when QC add 3s delay in hypervisor before loading El1SW. QC can not find root cause. We got this hypervisor with workaround to unblock the dependency
