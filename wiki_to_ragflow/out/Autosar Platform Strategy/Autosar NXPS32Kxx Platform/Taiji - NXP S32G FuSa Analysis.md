# Taiji - NXP S32G FuSa Analysis

> Source: /spaces/CARSFW/pages/6430099685/Taiji+-+NXP+S32G+FuSa+Analysis
> Last modified: 2025-10-31T10:02:32.000+01:00

---

## Overview

This page is to analyze the Safety mechanisms needed for S32G analysis

variant: NXP S32G 399A

| Safety mechanisms | Description |  |
| --- | --- | --- |
| PMIC BIST | PMIC self test - MCU has to check LBIST and ABIST values of PMIC |  |
| PMIC monitoring | VR5510 |  |
| PMIC Voltage monitor | VR5510 Need to configure VR5510 to monitor voltage rails in software and also configure Under and Over voltage thresholds |  |
| PMIC Temperature monitoring | VR5510 device has an independent thermal monitor sensor for each regulator. Each of them can be programmed to respond to either shutdown only the regulator or shutdown the regulator and transition the device into Deep Fail Safe state when the thermal shutdown threshold is exceeded. There’s also a thermal sensor at the center of the die which is used to generate interrupts for the MCU whenever the temperature exceeds the certain threshold |  |
| PMIC Clock monitoring | Mostly HW SM via PMIC But application need to set some register value and also some monitoring |  |
| PMIC Safe I2C communication | I2C safe communication between PMIC and MCU ( protected by an 8-bit CRC ) |  |
| PMIC register monitoring |  |  |
| External Watchdog monitoring | VR5510 as external Watchdog |  |
| BIST | Using SSA - Analyzes the results provided by LBIST and MBIST HW and initiates their execution ![](../../_images/Taiji%20-%20NXP%20S32G%20FuSa%20Analysis/image-2025-10-31_16-29-41.png) |  |
| SoC temperature monitor |  |  |
| SoC Clock monitor - Frequency check |  |  |
| Lockstep |  |  |
| External Voltage monitoring |  |  |
| Memory protection MPU |  |  |
| Memory protection MMU |  |  |
| ECC Monitoring |  |  |
| Safe State handler |  |  |
| squareCheck | A SW component used for latent fault detection • Detects faults in the hardware safety mechanisms • Provides start-up, runtime and shut-down APIs • Provides required Diagnostic Coverage as per ISO 26262 up to ASIL D ![](../../_images/Taiji%20-%20NXP%20S32G%20FuSa%20Analysis/image-2025-10-31_16-35-33.png) |  |
| Inter-platform communication framework | Need to check this further |  |
| A53 watchdog handling |  |  |
| Error Handler |  |  |
| FCCU NCF handling | Need to check this further |  |
| Program flow monitoring and OS interrupt monitor |  |  |
| Safety Boot (sBoot) | S32 Safety Software Framework (ModeSelector module) • A SW component checking whether the device booted to a safe configuration • Executed at the beginning of the application execution before the safety context is established • Verifies that the device configuration meets the hardware safety manual (SM) assumptions |  |
| Register monitor | Need to read back and compare at least once per FHTI |  |

### SSA (Safety Software Framework)

The S32 Safety Software Framework provides the software modules from Hardware and Service safety layers

BIST Manager - Built in Self-Test Manager covering both LBIST (Logic BIST) and MBIST (Memory BIST)

eMCEM – extended Microcontroller Error Manager

Mode Selector – Mode Selector (including Safety Config)

sBoot – Safety Boot

SquareCheck – Square Check (Check the Checkers)

SW Recovery – Software Recovery

#### eMCEM – extended Microcontroller Error Manager (like AuSm)

Fault management of the microcontroller • Configuration of fault reactions (reset, alarm IRQ, NMI, no reaction) • Sophisticated error handling mechanism • Allows to register an individual alarm handler for each FCCU fault • Redirection of fault reaction if the respective safety mechanism is tested by SquareCheck • Fault status reporting and fault clearing • Error injection • Memory error reporting

![](../../_images/Taiji%20-%20NXP%20S32G%20FuSa%20Analysis/image-2025-10-31_16-31-28.png)

#### ModeSelector (Mode Selector)

• A SW component used for selecting the application normal mode or degraded mode • Degraded modes increase device availability by enabling a usage of the device under the presence of non-critical permanent faults • The selection is based on FCCU results, SquareCheck results, optionally MBIST/LBIST results, and diagnostic information stored by SW Recovery. • There is also a possibility to call SW Recovery followed by Functional Reset in the cases of no operating mode can be selected • Executed during the boot (startup) phase when the system is in a safe state • Configuration of HW resource regions and association to the fault sources needed for the selectable modes

![](../../_images/Taiji%20-%20NXP%20S32G%20FuSa%20Analysis/image-2025-10-31_16-33-29.png)

#### sBoot (safe Boot)

• A SW component checking whether the device booted to a safe configuration • Executed at the beginning of the application execution before the safety context is established • Verifies that the device configuration meets the hardware safety manual (SM) assumptions

#### SquareCheck

A SW component used for latent fault detection • Detects faults in the hardware safety mechanisms • Provides start-up, runtime and shut-down APIs • Provides required Diagnostic Coverage as per ISO 26262 up to ASIL D

![](../../_images/Taiji%20-%20NXP%20S32G%20FuSa%20Analysis/image-2025-10-31_16-35-33.png)

#### SW Recovery (Software Recovery)

• A SW component used for global recovery • Called either in the case the MCU needs to recover from a fault that could not be handled by a local recovery or in the case Mode Selector can’t select any operational mode • Store diagnostic information for Mode Selector • Executed when MCU is in a safe state

![](../../_images/Taiji%20-%20NXP%20S32G%20FuSa%20Analysis/image-2025-10-31_14-49-31.png)
