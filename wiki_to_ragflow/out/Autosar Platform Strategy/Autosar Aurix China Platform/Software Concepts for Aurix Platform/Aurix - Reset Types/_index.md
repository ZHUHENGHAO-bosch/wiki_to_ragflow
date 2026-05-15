# Aurix - Reset Types

> Source: /spaces/CARSFW/pages/2379247242/Aurix+-+Reset+Types
> Last modified: 2022-08-08T06:55:49.000+02:00

---

## Overview

Aurix supports five types of Reset

- COLD POWER-ON RESET
- WARM POWER-ON RESET
- SYSTEM RESET
- APPLICATION RESET
- MODULE RESET

![](../../../../_images/Aurix%20-%20Reset%20Types/image2022-8-8_10-24-16.png)

COLD POWER-ON RESET

A Cold Power-on Reset is a reset which is triggered for the first time during a system power-up or in response to a temporary power failure. The pins and internal states are placed immediately into their default state when the trigger is asserted

The system is placed in a defined state, and all registers keep their reset values as long as the reset is asserted

DSPR , PSPR and LMU are re-initialized only after a cold-power on reset. In all other reset types, their content and redundancy are not affected

WARM POWER-ON RESET

A warm reset is triggered while the system is already operational, and the supplies remain stable. It is used to return the system to a known state

On a warm reset request, port pins are immediately placed in default state, all internal peripherals and CPU are re-initialized. PORST assertion keeps the MCU in warm power-on reset type

SYSTEM RESET

As for Warm Power-on Reset, this reset leads to an initialization into a defined state of the complete system. This type of reset can be triggered intentionally by the Application SW by configuring SFR

APPLICATION RESET

This reset leads to an initialization into a defined state of the complete application system of all peripherals, all CPU, all pins and part of the SCU . As for system reset, the trigger sources can be configured by Application SW

MODULE RESET

Individual reset commands can be sent by authorized masters to a single module without any impact on the rest of the system

### Effect of Reset on Device Functions

![](../../../../_images/Aurix%20-%20Reset%20Types/image2022-8-8_10-24-50.png)

### Effect of Reset on Static RAMs

![](../../../../_images/Aurix%20-%20Reset%20Types/image2022-8-8_10-25-39.png)
