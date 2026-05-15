# SMU Overview

> Source: /spaces/CARSFW/pages/2825338466/SMU+Overview
> Last modified: 2023-03-10T03:08:16.000+01:00

---

Safety Management Unit (SMU) in Aurix implements below important features

- Collects every alarm signal generated from safety mechanisms
- Alarm flags are stored in a diagnosis register that is only reset by the Power-on reset, to enable fault diagnosis and possible recovery
- Implements the access protection and Safety ENDINIT modes to protect configuration registers
- Implements a Fault Signaling Protocol (FSP) reporting internal faults to the external environment. The FSP can be configured using the following modes: – Bi-stable single pin output, also called ErrorPin (push-pull active low configuration using SMU_FSP0) – Timed dual rail coding using two inverted values on the ErrorPins (SMU_FSP0 and SMU_FSP1) – Single-bit timed protocol using the ErrorPin
- Each individual alarm can be configured to activate the fault signaling protocol
- Two SMU instance: one located in the core domain called SMU_core and another in the stand-by domain called SMU_stdby
- Alarms processed in SMU_core can be configured to activate one of the following internal actions: – generate an interrupt request to any of the CPUs, concurrent interrupts to several CPUs can be configured – generate a NMI request to the System Control Unit – generate a reset request to the System Control Unit – activate the Port Emergency Stop signal controlling the safe state of output pads – generate a CPU reset request
- After reset every alarm reaction, except for watchdog time-out alarm, is disabled
- Implements an internal watchdog called recovery timer to monitor the execution of critical software error handlers. The watchdog is started automatically by hardware according to configurable alarm events

![](../../../../../_images/SMU%20Overview/image2023-3-10_10-7-38.png)
