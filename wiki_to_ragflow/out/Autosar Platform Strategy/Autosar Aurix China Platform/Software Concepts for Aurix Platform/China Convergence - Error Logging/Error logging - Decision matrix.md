# Error logging - Decision matrix

> Source: /spaces/CARSFW/pages/2394662360/Error+logging+-+Decision+matrix
> Last modified: 2023-06-30T08:32:42.000+02:00

---

|   |   |
| --- | --- |
| Status | COMPLETED |
| Author | Jayaraj Praveen (BCSC/ENG1) |
| Stakeholders | GAO Carven (XC-CP/ESW2-CN) NIU Newton (XC-CP/ESW2-CN) Senthil Rajan Arunachalam (MS/EMC1-SWC) user-14275 |
| Decision | EM has the advantage of storing more data in SoC. FEL stores SoC failure data in NVM which will not be lost even when the ECU is taken out of battery. And modules from CART, Hydra and Cerberus uses FEL. Decision is to use both EM and FEL in China Convergence Platform |
| Due Date | 23 Sep 2022 |
| Owner | user-1f19a |

## Introduction

We have two mechanisms to log error information into NVM memory

1. FatalErrorLogger(FEL) from CI2 Hydra Platform
2. ErrorMemory from CI1 Project (GM VCU)

We need to decide for China Convergence platform which mechanism to use (FEL or ErrorMemory or both)

For overview refer this link China Convergence - Error logging - XC-CI China - Docupedia (bosch.com)

> **INFO: Diagnostic Read**
> Chery project has Diagnostic via CAN. Diagnostic team agreed to share a DID for FEL

| Attribute | Attribute description | FatalErrorLogger (CI2 Solution) | ErrorMemory (CI1 solution) |
| --- | --- | --- | --- |
| Availability | Module available in existing project/platform | Available in Cerberus platform | Available in GMVCU and China convergence projects |
| Storage | Memory region where Error data will be stored | Stored in SCC NVM | Stored in SoC File system |
| Memory Size | Number of Error Data entries and error data that can be stored | Less (depends on DFLASH availability) TC37x DFlash size ‭384 ‬KB | More In MBs |
| Read Mechanism | Way to read error data | Diagnostics (Convergence projects use diagnostic via SoC ) | em_trace/EM file via USB |
| Early Startup | Startup before SoC is up | Since the memory used is SCC NVM, error data during early data will be stored directly to NVM | SCC ErrorMemory component stores the data into Retention RAM buffer and send the data to SoC via INC once SoC is up and running Retention RAM size is 1 |
| Late Shutdown | After SoC is shutdown | Same as above → Stored directly in SCC NVM | Same as above → Stored in SCC Retention RAM |
| Safety | Mechanism for Safety modules | FEL is safe (No need FEL to be Safe Since SSH handles SEM internally) | Service.SafeErrorMemory available for Safety module to log their error into Error Memory ((No need of Safe Error Memory Since SSH handles SEM internally)) |
| Multicore | Support for Multicore | Cerberus planned to implement for multicore. Need the information when it will be delivered FatalErrorLogger - support for multi-core - XC-CT Cerberus Platform - Docupedia (bosch.com) | Multicore is not supported |
| SoC Dead | SoC Dead or Continuous Reset | No impact - Since the data is stored in SCC NVM However, to read via diagnostic we need to make SoC up and running Few projects have diagnostic communication directly with SCC and most projects diagnostic is via SOC Also on continues Reset SCC will enter into BL Diagnostic Path in Geely EcarX and Zeekr - GEN4 generic - Docupedia (bosch.com) | Need to make SoC up. But at startup EM will read from RetRAM and send to SoC via INC |
| Parser | Script to Parse data | FEL Parser is available | Data is sent as a String to SoC - So no need of a parser Example, (void)snprintf(errmem_msg_buf, sizeof(errmem_msg_buf)," INC-TP/AR: initialization failed"); |
| CART Module Implementation | Modules from CART, Hydra and Cerberus | Uses FEL Note: But we can write FEL wrapper to handle this | EM is not used |
| ECU out of battery | Continous Reset | No impact - Since the data is stored in SCC NVM. We can make SCC SW up and can read. Is FEL supports DLT injection read option? | No Data is stored in NVM |

COMPLETED
