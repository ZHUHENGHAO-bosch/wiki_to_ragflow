# Aurix - Safety Mechanism - Status

> Source: /spaces/CARSFW/pages/2403659720/Aurix+-+Safety+Mechanism+-+Status
> Last modified: 2023-05-12T12:00:29.000+02:00

---

Zeekr Timeline details - Zeekr Safety Timeline - GEN4 generic - Docupedia (bosch.com)

|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S No | System Safety Mechanism | Safety Goal | Modules | Comments | Dependencies | Status on CART | Status on CN Conv PF | Zeekr TSR Status |
|  | Main Safety Mechanisms |  |  |  |  |  |  |  |
| SM52 | Safe HMI Monitoring | SG1: Safe Telltale (ASIL B) |  | SM52: Monitoring of SW Tell-Tales - CT/ESC Software Home - Docupedia (bosch.com) |  | NA |  | Ready for review on 5/5 |
| SM56 | Safe Digital Output (LIN/CAN -> Flexray) | SG2: Safe signal output (ASIL B) |  | Framework may be from PF But signals are completely project specific | Final version of FSHLR FIT Manager | NA | PI 23.1 | Obsolete |
| SM57 | Safe Touch Monitor | SG3: Safe Touch (ASIL B) |  | Safe Touch - GEN4 generic - Docupedia (bosch.com) |  | NA |  | Not developed |
|  | Safety Mechanisms on Aurix |  |  |  |  |  |  |  |
| SM53 | Safe Tell-tale Handler |  |  | Tell-tale, Gear, Notifications, Touch signals | Final version of FSHLR FIT Manager(UTF/Diagnostics) | NA | PI 23.1 | Ready for review on 5/5 |
| SM01 | RAM Memory Monitoring on SCC |  |  | SM1: RAM Memory Monitoring on VCPU - CT/ESC Software Home - Docupedia (bosch.com) | FIT Manager(UTF/Diagnostics) | Nov-CW48 | PI 23.1 | Ready  for review 5/12/2023 |
| SM02 | ROM Memory Monitor on SCC |  |  | SM2: ROM Memory Monitoring on VCPU - CT/ESC Software Home - Docupedia (bosch.com) |  | Jan-CW05 | 24/2/2023 | Ready  for review 5/12/2023 |
| SM03 | Safe OS and BSP on SCC |  | Safe OS Hooks Exception handling Safe MCAL Rte Analyzer | SM3: Safe OS and BSP on VCPU - CT/ESC Software Home - Docupedia (bosch.com) |  |  |  | Ready  for review 5/12/2023 |
| SM04 | Memory Protection on SCC |  | Safe Startup BUS MPU CPU MPU Context Switcher Register Protection | SM18: Memory Protection on VCPU - CT/ESC Software Home - Docupedia (bosch.com) |  | Jan-CW05 | PI 23.2 | Ready  for review 5/12/2023 |
| SM05 | CAN/LIN/Flexray signal protection on SCC |  | E2E Protection | SM5: CAN/Ethernet Signal Protection - CT/ESC Software Home - Docupedia (bosch.com) |  | NA |  | Ready for review on 5/5 |
| SM06 | Watchdog on SCC |  | Internal WDG (Safety + CPU WDG) External WDG | Include internal and external watchdog. Recommend MAX20479A as external watchdog, since we have existing ASIL B driver (Yet to be confirmed) SM7: SW/HW Watchdog on VCPU - CT/ESC Software Home - Docupedia (bosch.com) |  | Feb-CW09 | PI 23.2/PI 23.3 (External wdg yet to be confirmed) | Ready  for review 5/12/2023 |
| SM08 | Program Flow Monitor on VCPU (Not an seperate SM - it will be covered by SM06) |  |  | SM8: Program Flow Monitoring on VCPU - CT/ESC Software Home - Docupedia (bosch.com) |  | Feb-CW09 | PI 23.2/PI 23.3 | Ready  for review 5/12/2023 |
| SM09 | Register Monitor on SCC |  |  | SM9: Register Monitoring on VCPU - CT/ESC Software Home - Docupedia (bosch.com) |  | Jan-CW05 | PI 23.2 | Ready  for review 5/12/2023 |
| SM12 | Internal Voltage Monitor |  | Aurix voltage monitor - PMS | SM10: Power/Voltage Monitoring - CT/ESC Software Home - Docupedia (bosch.com) | FIT Manager(UTF/Diagnostics) | Nov-CW48 Feb-CW09 (External) | PI 23.1/ PI 23.2 | Ready for review on 5/5 |
| SM14 | Selftest on SCC |  |  | SM17: Built-in Self-Test on VCPU - CT/ESC Software Home - Docupedia (bosch.com) |  | Jan-CW05 | PI 23.2 | Ready  for review 5/12/2023 |
| SM16 | Safe Configuration |  |  | SM12: Safe Configuration - CT/ESC Software Home - Docupedia (bosch.com) |  | TBD |  | Ready for review on 5/5 |
| SM18 | Clock supervision on SCC |  |  | SM13: Clock Supervision on VCPU - CT/ESC Software Home - Docupedia (bosch.com) | FIT Manager(UTF/Diagnostics) | Nov-CW48 | PI 23.1 | Ready  for review 5/12/2023 |
| SM19 | SoC State Monitor |  |  | We have both QM and ASIL modules monitoring SoC QM: - SOH (State of Health) - SystemM (HW line monitoring) Need a clear synchronization between QM and ASIL module on this supervision SM19: SoC State Supervision - CT/ESC Software Home - Docupedia (bosch.com) |  | Feb-CW09 | PI 23.2/PI 23.3 | Ready for review on 5/5 |
| SM20 | Safe State Handler |  | Safe Error Memory Aurix Safety Manager | SM20: Safe State Handler - CT/ESC Software Home - Docupedia (bosch.com) |  | Jan-CW05 | PI 23.2 | Ready  for review 5/12/2023 |
| SM13 | SCC Temperature Supervision |  | Aurix temperature monitor System temperature monitor | SM16: VCPU Critical Temperature Monitoring - CT/ESC Software Home - Docupedia (bosch.com) |  | Dec-CW51 Feb-CW09 | PI 23.1 | Ready  for review 5/12/2023 |
| SM23 | Safe ADC Calibration and Plausibility Check |  | Safe ADC Compensation Safe IoHwAb |  |  | Dec-CW51 |  | Ready  for review 5/12/2023 |
| SM21 | VCPU Voltage HW Diagnostic May be not needed For TI → No need for an Diagnostic mechanism AC43 CSD and Touch Controller Diagnostic Follow safety requirements provided by CSD supplier. To be Added Monitor | Diagnostic |  |  | May be not needed For TI → No need for an Diagnostic mechanism |  |  |  | AC43 | CSD and Touch Controller Diagnostic |  |  | Follow safety requirements provided by CSD supplier. |  |  |  | To be Added |  |  |  |  |  |  |  |  |  |  |  |  | PI 23.1 (IVM) PI 23.3 (EVM) | Ready  for review 5/12/2023 |
| Diagnostic |  |  | May be not needed For TI → No need for an Diagnostic mechanism |  |  |  |
| AC43 | CSD and Touch Controller Diagnostic |  |  | Follow safety requirements provided by CSD supplier. |  |  |  |
| To be Added |  |  |  |  |  |  |  |
| SM15 | Safe DLT logging |  |  | Using Vector DLT |  | Feb-CW09 | PI 23.3 | Ready  for review 5/12/2023 |
|  | Safety Mechanisms on SoC |  |  |  |  |  |  |  |
| AC39 | Obsolete PMIC Supervision |  |  |  |  |  |  | NA |
| AC41 | Obsolete SoC DPU Configuration and Verification |  |  |  |  |  |  | NA |
| AC42 | SoC Serialize Diagnostic |  |  |  |  |  |  | Ready for review on 5/5 |
| AC43 | SoC SW Watchdog |  |  |  |  |  |  | Ready for review on 5/5 |
|  |  |  |  |  |  |  |  |  |
