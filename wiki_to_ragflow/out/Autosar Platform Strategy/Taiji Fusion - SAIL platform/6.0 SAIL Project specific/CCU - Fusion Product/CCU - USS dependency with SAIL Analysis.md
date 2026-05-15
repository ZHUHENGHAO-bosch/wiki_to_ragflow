# CCU - USS dependency with SAIL Analysis

> Source: /spaces/CARSFW/pages/4994778156/CCU+-+USS+dependency+with+SAIL+Analysis
> Last modified: 2024-11-19T11:09:23.000+01:00

---

## Overview

This page is to analyze the USS dependencies with SIAL domain BSW software

### Hardware connection

In CCU Fusion project, USS is connected to SAIL domain like shown below

![](../../../../_images/CCU%20-%20USS%20dependency%20with%20SAIL%20Analysis/image-2024-11-19_14-2-30.png)

We will have two Elmos devices connected to SAIL and these two ELMOS have two channel each and each channel connects to 12 USS sensors

- 2 Elmos x 2 channels x 3 sensors = 12 USS sensors

SAIL connection with elmos

| Name | Description |
| --- | --- |
| INTB | Interrupt from Elmos to SAIL in indicate |
|  |  |
|  |  |

![](../../../../_images/CCU%20-%20USS%20dependency%20with%20SAIL%20Analysis/image-2024-11-19_15-29-47.png)

The dependency of USS for SAIL is

| Pin number | Description | Details | SAIL modules required for this |
| --- | --- | --- | --- |
| SAIL_IO_55 | USS_INTB-CPU_SAIL_USS_CTRL_1V8 |  |  |
| SAIL_IO_56 | CPU_SAIL_USS_PHTM_EN_1V8 |  |  |
| SAIL_IO_56 | USS_RESB-CPU_SAIL_USS_E1_CTRL_1V8 |  |  |
| SAIL_IO_52 | USS_DCR2B-CPU_SAIL_USS_E1_CTRL_1V8 |  |  |
| SAIL_IO_53 | USS_DCR1B-CPU_SAIL_USS_E2_CTRL_1V8 |  |  |
| SAIL_IO_49 | USS_RFC-CPU_SAIL_USS_E2_CTRL_1V8 |  |  |
| SAIL_IO_59 | USS_CLKREF-CPU_SAIL_USS_CTRL_1V8 |  |  |
| SAIL_IO_50 | USS_DCR1B-CPU_SAIL_USS_E1_CTRL_1V8 |  |  |
| SAIL_IO_60 | USS_DCR2B-CPU_SAIL_USS_E2_CTRL_1V8 |  |  |
| SAIL_IO_ | USS_RFC-CPU_SAIL_USS_E1_CTRL_1V8 |  |  |
| SAIL_IO_56 | USS_CSB_A-CPU_SAIL_USS_CTRL_1V8 | SPI communication with Elmos |  |
| SAIL_IO_56 | USS_CSB_B-CPU_SAIL_USS_CTRL_1V8 |  |
| SAIL_IO_56 | USS_MISO-CPU_SAIL_USS_CTRL_1V8 |  |
| SAIL_IO_56 | USS_MOSI-CPU_SAIL_USS_CTRL_1V8 |  |
| SAIL_IO_56 | USS_SCK-CPU_SAIL_USS_CTRL_1V8 |  |
| SAIL_IO_56 | USS_RESB |  |  |
| SAIL_IO_56 | SDA-CPU_SAIL_USS_I2C_1V8 |  |  |
| SAIL_IO_56 | SCL-CPU_SAIL_USS_I2C_1V8 |  |  |
