# TC4x - GTM Vs eGTM

> Source: /spaces/CARSFW/pages/6534374612/TC4x+-+GTM+Vs+eGTM
> Last modified: 2025-11-25T11:06:07.000+01:00

---

## Overview

TC4x introduced eGTM and many variants support only eGTM - 1.0 TC4x - variants and peripherals details - XC-CT China - Docupedia

### Difference between GTM and eGTM

GTM (Generic Timer Module) : The established, highly complex timer subsystem from previous AURIX generations (TC2xx, TC3xx)

eGTM (enhanced Generic Timer Module) : A completely redesigned, more flexible and scalable timer architecture in TC4xx

> **INFO: In a nutshell**
> The eGTM in TC4xx represents a fundamental redesign that addresses the complexity and limitations of the original GTM while maintaining backward compatibility at the functional level. It provides better performance, enhanced safety features, and significantly improved usability for complex automotive and industrial applications

#### Architecture difference

| GTM | eGTM |
| --- | --- |
| Fixed, monolithic architecture | Modular, scalable architecture |
| Pre-defined hardware resources | Configurable IP blocks |
| Complex routing with limited flexibility | Simplified, more flexible routing |

#### New in eGTM

- TBU (Timer Base Unit) : Provides time bases
- CCU (Channel Control Unit) : Contains configurable timer channels
- MON (Monitor Unit) : For safety monitoring

### eGTM Block diagram

![](../../../../_images/TC4x%20-%20GTM%20Vs%20eGTM/image-2025-11-25_18-3-3.png)
