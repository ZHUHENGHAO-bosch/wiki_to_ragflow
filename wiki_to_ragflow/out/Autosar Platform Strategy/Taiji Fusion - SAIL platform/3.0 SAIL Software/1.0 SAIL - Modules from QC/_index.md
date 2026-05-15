# 1.0 SAIL - Modules from QC

> Source: /spaces/CARSFW/pages/4649425971/1.0+SAIL+-+Modules+from+QC
> Last modified: 2024-10-24T07:37:45.000+02:00

---

## Overview

This page is to analyze the modules from QC

## CDDs delivered by QC

| Module | Description | ASIL/QM |
| --- | --- | --- |
| CDD_Acmu | Automotive clock monitoring unit (ACMU) Driver for Clock monitoring Unit (On-chip clock monitors) ![](../../../../_images/1.0%20SAIL%20-%20Modules%20from%20QC/image-2024-8-27_18-53-48.png) | ASIL |
| CDD_BootLogger | Gives interface to store Boot message In cyclic task, send the boot message to VIP/SCC | ASIL |
| CDD_DebugLog | CDD module to send log message via UART | QM |
| CDD_Dispatcher | Receives UART message and call respective callback based on Command ID | QM |
| CDD_Fusa | Centralized module to handle the Main domain Fatal Sail Fatal Warning and Error It is similar to Ausm and SMU in Aurix | ASIL |
| CDD_I2c | I2C Device driver | QM |
| CDD_Icb | SAIL NOC error handling implementation | QM |
| CDD_Ipcc | Driver for IPCC (Interrupt Controller hardware) |  |
| CDD_Isd | Driver for Island State Detector. This driver supports isolating SAIL subsystem from the entire SoC whenever main domain fatal errors occurs | ASIL |
| CDD_Mailbox | Safety SW library for Mailbox communication | QM |
| CDD_Monitor | Module which start, stop and update different monitor modules | ASIL |
| CDD_Pmic | Driver for external ASIL-D PMIC for SAIL | ASIL |
| CDD_Psail | Driver for monitoring the Main Domain PMIC | ASIL |
| CDD_Ssm | SAIL safety monitor ![](../../../../_images/1.0%20SAIL%20-%20Modules%20from%20QC/image-2024-8-27_17-46-39.png) | ASIL |
| CDD_Uart | Driver for UART interface | QM |
| CDD_Vsens | Voltage monitoring driver | ASIL |
| CDD_CRC | CRC module | ASIL |
| CDD_Qfprom | This component takes care of SW fuses related SSRs (Qualcomm fuse-programmable read-only memory) | ASIL |
| CDD_Tsens | Temperature sensor driver | ASIL |
| CDD_Xbl | eXtensible bootloader |  |

## EcuAL by QC

| Module | Description | ASIL/QM |
| --- | --- | --- |
| CanTrcv_TCAN1044 | CAN transceiver driver for 1044 | QM |
| EthTrcv | Ethernet transceiver driver | QM |
| Mem | AR Memory driver | - |
| CanTrcv_184_Tcan1146 | CAN transceiver driver for 1146 | - |
| MemAcc |  |  |

## MCAL by QC

| Module | Description | ASIL/QM |
| --- | --- | --- |
| Can | Can driver | ASIL |
| Dio | Dio Driver | ASIL |
| Eth | Eth driver | QM |
| Gpt | GPT driver | ASIL |
| Spi | SPI driver | QM |
| Port | Port Driver | ASIL |
| Crypto | Crypto component handles all the crypto modules which are needed for security in SAIL. It also covers the requirements of HWKM in SAIL subsystem. | ASIL |
| Mcu | Mcu driver | ASIL |
| Wdg | wdg driver | ASIL |

## BSP list from QC

Not for Autosar release. Below module list is just for information

| Module | Description | ASIL/QM |
| --- | --- | --- |
| acmu |  |  |
| bist |  |  |
| can |  |  |
| can_trcv |  |  |
| chipinfo |  |  |
| clock |  |  |
| cpr |  |  |
| crashdbg |  |  |
| crc |  |  |
| dhrystone |  |  |
| dma_crc |  |  |
| el_entry |  |  |
| fdt |  |  |
| fusa |  |  |
| gpio |  |  |
| gpt |  |  |
| i2c |  |  |
| icb |  |  |
| interrupts |  |  |
| ipcc |  |  |
| isd |  |  |
| LogCode |  |  |
| mailboxExt |  |  |
| mailboxLib |  |  |
| monitor |  |  |
| pmic |  |  |
| pmu |  |  |
| psail |  |  |
| pvl |  |  |
| pwr_controller |  |  |
| qbfw |  |  |
| qfprom |  |  |
| sail_bootcfg |  |  |
| sail_diagnostics |  |  |
| sail_fs |  |  |
| sail_gpio_time_sync |  |  |
| sail_updater |  |  |
| sailheap |  |  |
| sailsafertos |  |  |
| security |  |  |
| slavesoc_monitor |  |  |
| sleep |  |  |
| spi |  |  |
| spinor |  |  |
| startup |  |  |
| time |  |  |
| tsens |  |  |
| uart |  |  |
| vsens |  |  |
| wdt |  |  |
| xbl |  |  |
