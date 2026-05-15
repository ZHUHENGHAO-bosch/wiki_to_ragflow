# Aurix - PMS (Power Management System)

> Source: /spaces/CARSFW/pages/2377378063/Aurix+-+PMS+Power+Management+System
> Last modified: 2022-08-05T11:03:38.000+02:00

---

## Introduction

Aurix has an On-chip linear and switch mode voltage regulators are implemented.

The Embedded Voltage Regulators (EVR33 & EVRC) in turn generate the VDDP3 and VDD supply voltages required internally for the core, flash and port domains. EVRC regulator is implemented as a SMPS regulator and generates core supply either from 5 V or 3.3 V external supply. EVR33 regulator is implemented always as a LDO regulator and is required only in case of 5 V external supply

![](../../../../_images/Aurix%20-%20PMS%20%28Power%20Management%20System%29/image2022-8-5_14-32-17.png)

Each color region and module in the figure above represent the different power domains in AURIX™ TC3x:  Blue : 5V / 3.3V VEXT Pad domain, 5V / 3.3V VFLEX, VEBU independent and isolated Pad domains: − All Pads / Ports, Shared pads − OSC, HSCT  Orange : 5V / 3.3V VDDM ADC domain − EVADC, DSADC, ADC pads  Yellow : 3.3V VDDP3 Flash domain − Flash Programming  Green : 1.25V VDD domain, 1.25V VDDSB (ED devices, EMEM) − Core domain (CPUs for example) − Flash Read Sense  Purple and red : 5V / 3.3V VEVRSB Standby Domain − VDDPD Standby Domain (Regulator components, PMS components including safety modules, SCR) − Standby Pads (P33 including PINB, P34) − CPU0 and CPU1 dLMU Standby RAM
