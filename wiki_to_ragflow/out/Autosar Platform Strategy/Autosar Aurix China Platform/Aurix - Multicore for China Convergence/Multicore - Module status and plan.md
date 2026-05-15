# Multicore - Module status and plan

> Source: /spaces/CARSFW/pages/2499261360/Multicore+-+Module+status+and+plan
> Last modified: 2023-04-12T12:37:10.000+02:00

---

### Multicore Use case Status

| Feature | Design Status | Implementation Status | Open points |
| --- | --- | --- | --- |
| Multicore Enabler - POC in CNCONVPF | COMPLETED | COMPLETED |  |
| Multicore Enabler - in Zeekr | COMPLETED | COMPLETED |  |
| Multicore RAMROM Summary | NOSCOPE | COMPLETED |  |
| Multicore Memmap Generator | NOSCOPE | COMPLETED | Latest 1.7.0 version is integrated |
| Multicore Os Hooks and Exception Handling | NOSCOPE | COMPLETED | Few test cases were not tested since OS SC1 is used. These test cases will be tested onc SC3 is enabled in PI23.1 |
| Multicore RTMO | NOSCOPE | COMPLETED | In IP Sprint RTMO part 2 completed |
| INC - Multicore | COMPLETED | COMPLETED |  |
| INC - Multicore Optimization | COMPLETED | TOBESTARTED | Bug fix and Spinlock optimization |
| LCM - Startup | COMPLETED | INPROGRESS | Need callouts implementation for Driver Init zero and One in slave cores |
| LCM - Synchronized Shutdown (Sleep) | COMPLETED | TOBESTARTED |  |
| LCM - Synchronized Shutdown (Reset) | COMPLETED | TOBESTARTED |  |
| LCM - Mode Handling | COMPLETED | COMPLETED | Only Core 1 and Core 2 states have to be implemented for local modules . Ex: FR, CAN |
| LCM - Pullback | TOBESTARTED | TOBESTARTED |  |
| FEL - Multicore | NOSCOPE | COMPLETED |  |
| NvRamAbstraction | NOSCOPE | INPROGRESS |  |
| MCU access for all cores | NOSCOPE | COMPLETED |  |
| PoC for NVM access in Slave Core | TOBESTARTED | TOBESTARTED |  |
| MCAL Multicore Analysis | COMPLETED | COMPLETED |  |
| FR to slave Core 1 | COMPLETED | INPROGRESS | Step by Step process FR is moved to Core 1 |
| COM to Core 1 | INPROGRESS | INPROGRESS |  |
| DLT logging in Slave cores | COMPLETED | INPROGRESS |  |
| DLT injection in Slave cores | NOSCOPE | NOSCOPE | Less Priority |
| Boot Time Framework | TOBESTARTED | TOBESTARTED |  |
| Error Memory or FEL | TOBESTARTED | TOBESTARTED |  |
| Guidelines and HowTos | INPROGRESS | TOBESTARTED |  |
| DET handling | TOBESTARTED | TOBESTARTED |  |
| MCAL - ADC Multicore | NOSCOPE | NOSCOPE | Not needed now |
| Variant Handler | NOSCOPE | NOSCOPE | Not needed now |

![](../../../_images/Multicore%20-%20Module%20status%20and%20plan/Multicore_UseCase.jpg)

### Cerberus Dependency

|   |   |   |   |
| --- | --- | --- | --- |
| Module | Status - Cerberus | Version available | Comments |
| LCM - Multicore Synchronized Shutdown Mode Synchronization across cores | Partially Done – In progress | 1.4.0 | Synchronized Startup/Shutdown is available. Mode synchronization is available for SWCs As ECUM functionality is accessed across RTE to Core0. Further Mode synchronization development is pending. |
| RTMO - Multicore | Done | 1.6.0 | Can you please share the version considered for integration? |
| FEL - Multicore | Done | 1.7.0 | Bleeding edge shall be taken from 11.11.22 if latest is needed. |
| System timer in all cores | Done | 1.4.0 |  |
| Debug trace - Multi core | Done | 1.6.0 | Latest release shall be used as some fixes are included that complete the feature |
| NVRAM abstraction - Multicore | Done | 1.6.0 |  |
| Startup code for BL, BM and HSM | In progress | None | Not planned until January, may not be feasible for Zeekr. |
