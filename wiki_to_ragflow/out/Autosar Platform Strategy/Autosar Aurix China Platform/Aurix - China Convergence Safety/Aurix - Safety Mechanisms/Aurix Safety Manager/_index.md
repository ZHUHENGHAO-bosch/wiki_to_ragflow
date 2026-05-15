# Aurix Safety Manager

> Source: /spaces/CARSFW/pages/2379247306/Aurix+Safety+Manager
> Last modified: 2023-01-17T10:37:50.000+01:00

---

## Overview

The SMU (Safety Management Unit) is a central component of the safety architecture providing a generic interface to manage the behavior of the microcontroller under the presence of faults.

The SMU centralizes all the alarm signals related to the different hardware and software-based safety mechanisms. Each alarm can be individually configured to trigger internal actions and/or notify externally the presence of faults via a fault signaling protocol.

### Need for Aurix Safety Manager

All the Safety mechanism report faults to SMU and SMU decides the actions for these faults.

We can configure SMU to do any one of the below action on receiving specific fault

- No Action
- Interrupt request (smu_int0 - smu_int2)
- NMI Trap Request
- Reset Request to SCU
- CPU Reset Request

> **INFO: FSP**
> We can use P33.8 (FSP0) and P33.10(FSP10) for fault signal protocol → Configured in SMU

Usually we will configure SMU reaction as Interrupt request for all alarms, so that we can log all important information in FEL/Error Memory (Also useful to log reset reason in DLT on next power up)

SMU supports three interrupts and an NMI. Mapping of SMU alarm to interrupt is done in SMU configuration in MCAL. The selection of interrupt for an alarm has to be aligned with Aurix.SafetyManager configuration

![](../../../../../_images/Aurix%20Safety%20Manager/Auirx.SafetyManager_Overview.bmp)

### SMU Failure Management

![](../../../../../_images/Aurix%20Safety%20Manager/image2022-8-17_11-8-34.png)
