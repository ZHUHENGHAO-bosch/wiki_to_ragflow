# 01. QAM 8255 Overview

> Source: /spaces/CARSFW/pages/3625360381/01.+QAM+8255+Overview
> Last modified: 2023-12-28T08:23:14.000+01:00

---

### Overview of QAM 8255

| Feature | QAM 8255 | Comments |
| --- | --- | --- |
| Application Processor | Kryo Gen 6 CPU subsystem - two identical quad-core clusters Quad Kryo Gold Prime cores with 512 KB L2 cache per core, targeting up to 2.35 GHz | - |
| Digital signal processing | Hexagon Tensor Processor is integrated with Qualcomm Hexagon DSP, targeting up to 1.5 GHz, quad Hexagon Vector eXtensions (quad-HVX), and dual Hexagon Matrix eXtensions (HMX) co-processors Audio Hexagon DSP dedicated to audio subsystem, targeting up to 1.344 GHz and with a 2 MB L2/TCM Two general purpose Hexagon DSPs (GPDSP) targeting up to 1.708 GHz and with a 1 MB L2 cache for advanced audio processing and other use cases | - |
| Safety Island (SAIL) Subsystem | A subsystem integrated with quad cortex-R52 CPU Each cortex-R52 CPU is targeting up to 1.85 GHz Collects functional safety errors and alarms from other subsystems and communicates to external system controller Controls logic/memory BIST engines Independent booting capability through OSPI/QSPI interface Safety monitor of main and SAIL domains | Task 1: Find OS for this processor |
| Always-on subsystem | Always-on subsystem with always-on processor Hardware-based resource and power management (RPMh) with hardware accelerators for voltage control and regulation, clock management, and resource communication |  |
| Memory Overview |  |  |
| System memory via EBI | Six-channel high-speed memory – 3200 MHz LPDDR5 SDRAM (6 × 16- bit) 3 MB system cache |  |
| Other internal memory | 256 KB IMEM 1.5 MB GMEM for graphics 1 MB L2 cache and 8 MB Vector-TCM (vTCM) for Hexagon Tensor Processor |  |
| Others |  |  |
| Qualcomm universal peripheral (QUP) serial engines | 21 main domain (MD) GPIO-based QUP SEs: 7 bits for QUP3_SE_0, 5 bits for QUP2_SE_2 and 4 bits for each of the other 19 QUP SEs; multiplexed serial interface functions Five SAIL domain GPIO-based QUP SEs: 5 bits for QUP0_SE_4 and 4 bits for each of the other four QUP SEs; multiplexed serial interface functions |  |
| I2C master (Up to 1 MHz) | I2C interface available on all MD and SAIL domains QUP SEs, dedicated controller for each port |  |
| SPI master (Up to 50 MHz) | SPI master interfaces available on all MD and SAIL domains QUP SEs, except for MD QUP1_SE_6 |  |
| CAN-FD | Eight CAN-FD interfaces located in SAIL domain, each of them supports up to 12 Mbps |  |
| Number of main domain GPIO ports | 149– GPIO_0 to GPIO_148 |  |
| Number of SAIL domain GPIO ports | 78– SAIL_IO_0 to SAIL_IO_78 (SAIL_IO_63 is not routed from SA8255P to QAM8255P BGA) |  |
| System architecture for each PMM8650AU device |  |  |
| Main domain | Power management General housekeeping GPIOs Clock generation and output (PMIC_A only) Power on/off control |  |
| Safety Island (SAIL) domain | Safety monitoring BIST control Fault detection and fault aggregator Data storage and event logging |  |
| RGMII | One SAIL domain RGMII interface with MDIO for Ethernet with AVB |  |
| UART (Up to 4 MHz) | UART (64 B FIFO) interface available on all MD and SAIL domains QUP SEs, except MD QUP0_SE_2/3, QUP1_SE_2/3, QUP2_SE_2/3 and SAIL QUP0_SE_2/3, which also support HS-UART (128 B FIFO) |  |
|  |  |  |
