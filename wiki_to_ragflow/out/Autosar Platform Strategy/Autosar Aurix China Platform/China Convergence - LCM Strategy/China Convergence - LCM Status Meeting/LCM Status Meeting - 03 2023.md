# LCM Status Meeting - 03 2023

> Source: /spaces/CARSFW/pages/2800534834/LCM+Status+Meeting+-+03+2023
> Last modified: 2023-03-30T10:24:39.000+02:00

---

### Date : 30 Mar 2023

### Participants: Shanhe, Joanna, Can, Jolin, Praveen, John

### Meeting Minutes:

- Memmap COMPLETED

- Basic Test Spec INPROGRESS
- Logging in verbose mode
- Logging in Non-verbose mode China Convergence Logging - Architectural Guideline - XC-CT China - Docupedia (bosch.com)

@Jolin,

Create a wiki page for How to non-verbose in Chery How to DLT in Chery - GEN4 generic - Docupedia (bosch.com) JIN John (XC-CP/ESW2-CN) to do a basic review

Working on voltage monitor INPROGRESS Planned to push 30 Mar 2023

@Shanhe - Start STR with high priority. Reading the Wakeup_STR (HW latch) (Check pin status before LBIST) Deadline: 31/03/2023 INPROGRESS

Ask SoC team when STR will be ready? Deadline for whole feature is 01 May 2023

Start Pull back

MC Startup and Shutdown

@Joanna - BswM Configuration in Chery INPROGRESS 03 Apr 2023

INC Dispatcher optimization

Framework for Muticore mode handling 07 Apr 2023

@Huang Can - SoC State Monitor - Sequence diagram - will be completed today, review on 31 Mar 2023 INPROGRESS

Geely customer requirement

SWRS - Software requirement - rework and resend in collaborator. Jayaraj Praveen (BCSC/ENG1) to review

|   |   |   |
| --- | --- | --- |
| Owner | Primary Feature | Secondary Tasks |
| @TAN Shanhe (XC-CT/ESW2-CN) | LCM Multicore Startup LCM Multicore Shutdown LCM Pullback STR in Aurix SCR Check CC2 and compare with us asr/StandbyController - basesoftware/autosar/rbi_aurix_dev - Gitiles (bosch.com) Cerberus - WD | EcumModeManager Memmap Generation Code Clean up in Config repo Test Spec QAC - Till level 5 QAC Zeekr Steps and Generation - XC-CT China Convergence - Docupedia (bosch.com) |
| @HUANG Can (XC-CT/ESW2-CN) | SoC State Monitor Safe Module, Clean up in both SCC and SoC Side CPU_PWR_OFF and CPU_HMI_RUN whether we need to check this part Design by 23-03-2023 SCC Only Reset - Aurix | PowerM Memmap Generation Making Power sequence optimized for all projects Voltage Management Code Clean up Test Spec QAC |
| @ZHAO Joanna (XC-CT/ESW2-CN) | LCM Multicore Mode Handling using BswM Delivery by end of this week - first version LCM INC optimization Cyclic Reset Handling | PSC, SystemM, LCM INC Dispatcher Memmap Clean up and Optimization for PSC, SystemM, LcmInc  - Zeekr,Chery (basic clean) SWRS Test Spec QAC |
| @Jolin @HUANG Can (XC-CT/ESW2-CN) | Thermal module PF implementation with SWRS Huang Can to help Jolin Chery specific requirements |  |
| Other General Topics, Any deliveries in Zeekr shall be delivered in both Zeekr and Chery Project Bug handling @TAN Shanhe (XC-CT/ESW2-CN) – Zeekr @ZHAO Joanna (XC-CT/ESW2-CN) – BYD @HUANG Can (XC-CT/ESW2-CN) -  Geely @Jolin Chery | QM Voltage Monitoring - next feature |  |

### Date : 23 Mar 2023

### Participants: Shanhe, Joanna, Can, Jolin, Praveen

### Meeting Minutes:

- Memmap - next week (Thursday)
- Testspec
- Logging in Non-verbose mode
- Basic Coding guidelines
- Peer review within team in Gerrit

TAN Shanhe (XC-CP/ESW2-CN)

- A2 Sub board bring up, Bugs with HW team
- Sleep current analysis - Bug with A2 board, will be measuring in A3 board
- To start SCR in Chery

user-53e00

- SoC State Monitor - Zeekr

ZHAO Joanna (XC-CP/ESW2-CN)

- Mode Handling using BswM - PoC
- BYD - new requirement and Bug fix

ZHANG Jolin (XC-CP/ESW2-CN)

- Thermal code delivered

### Actual Plan:

22-03-2023

Chery is first SOP. We need to deliver in Zeekr and Chery together. But concentrate more on Chery.

Make sure Chery LCM is working in all use cases

Deadline for the following modules:

1. Thermal: March 24,  (SOC: JIANG Sophia) - Almost done. Temperature is passed to SoC. lWorking on FAN control -> @Jolin -> Huang Can to support
2. Voltage monitor: March 31 (SOC: HU Fei) - Do we have requirements from Requirements team? Yes we have.  -> @Joanna, Shane to support
3. STR: April 06 (SOC: HU Fei) @Shanhe to start
4. Sleep & wakeup: April 06 @Jolin

@Jolin, Chery has STR ? Deadline of SoC STR so that we can plan STR functionality

@Shanhe - Start STR with high priority. Reading the Wakeup_STR (HW latch) (Check pin status before LBIST)

Pull back

MC Startup and Shuntdown

@Joanna - Mode handling (first version is completed) - delivery is pending, Mode Handling Framework to be updated

@Huang Can - SoC State Monitor - EA diagram - review today afternoon

SWRS - Software requirement - done (not reviewed) - Collaborator review

@Jolin -  PF Thermal - code clean is almost done (Next week since Jolin busy with Chery) @Huang Can - Review

### Date : 16 Mar 2023

### Participants: Shanhe, Joanna, Can, Jolin, Praveen

### Meeting Minutes:

Memmap generation: Next step

Ram dump Mode: user-53e00 To send mail (RamDump mode)

EDL - boot mode 1/o to enter SoC to fast boot mode

TAN Shanhe (XC-CP/ESW2-CN)

- Working on A2 bring up and ADC testing and SCR. Deadline:
- Voltage management as a second task in Zeekr

user-53e00

- STR bug for Geely. Will take long time
- Thermal for Zeekr - Primary delivery - Need to add 3 ADC Sensors
- SoC State Monitor - Zeekr

ZHAO Joanna (XC-CP/ESW2-CN)

- Mode Handling using BswM - PoC
- BYD - new requirement and Bug fix

ZHANG Jolin (XC-CP/ESW2-CN)

- Thermal module PF implementation with SWRS
- Test the following test cases in latest 09 Mar 2023 SW - Chery HW

### Date : 09 Mar 2023

### Participants: Shanhe, Joanna, Can, Jolin

### Meeting Minutes:

TAN Shanhe (XC-CP/ESW2-CN)

- Working on A2 bring up and ADC testing and SCR. Deadline:
- Voltage management as a second task in Zeekr

user-53e00

- STR bug for Geely. Will take long time
- Thermal for Zeekr - Primary delivery - Need to add 3 ADC Sensors
- SoC State Monitor - Zeekr

ZHAO Joanna (XC-CP/ESW2-CN)

- Mode Handling using BswM - PoC
- BYD - new requirement and Bug fix

ZHANG Jolin (XC-CP/ESW2-CN)

- Thermal module PF implementation with SWRS
- Test the following test cases in latest 09 Mar 2023 SW - Chery HW

### Date : 02 Mar 2023

### Participants: Shanhe, Joanna, Jolin , Can

### Meeting Minutes:

Any changes in Zeekr shall be delivered to Chery

TAN Shanhe (XC-CP/ESW2-CN)

- Working on A2 bring up and ADC testing and SCR. Deadline: 02 Mar 2023
- Voltage management as a second task in Zeekr

user-53e00

- STR bug for Geely. Will take long time
- Thermal for Zeekr - Primary delivery - Need to add 3 ADC Sensors

ZHAO Joanna (XC-CP/ESW2-CN)

- Mode Handling using BswM
- BYD - new requirement and Bug fix

ZHANG Jolin (XC-CP/ESW2-CN)

- Thermal module PF implementation with SWRS

|   |   |   |
| --- | --- | --- |
| Owner | Primary Feature | Secondary Tasks |
| @TAN Shanhe (XC-CT/ESW2-CN) | LCM Multicore Startup LCM Multicore Shutdown LCM Pullback STR in Aurix Reset Root cause to DLT SCR PF | EcumModeManager Memmap Generation Code Clean up in Config repo PowerM Memmap Generation Making Power sequence optimized for all projects Voltage Management Code Clean up |
| @HUANG Can (XC-CT/ESW2-CN) | SoC State Monitor Safe Module, Clean up in both SCC and SoC Side | PowerM Memmap Generation Making Power sequence optimized for all projects Voltage Management Code Clean up Test Spec |
| @ZHAO Joanna (XC-CT/ESW2-CN) | LCM Multicore Mode Handling using BswM Cyclic Reset Handling | PSC, SystemM, LCM INC Dispatcher Memmap Clean up and Optimization SWRS Test Spec QAC |
| @ZHANG Jolin (XC-CT/ESW2-CN) @HUANG Can (XC-CT/ESW2-CN) will help | Thermal module PF implementation with SWRS | Chery Project Requirements |
| Other General Topics, Any deliveries in Zeekr shall be delivered in both Zeekr and Chery Project Bug handling @TAN Shanhe (XC-CT/ESW2-CN) – Zeekr @ZHAO Joanna (XC-CT/ESW2-CN) – BYD @HUANG Can (XC-CT/ESW2-CN) -  Geely @ZHANG Jolin (XC-CT/ESW2-CN) - Chery |  |  |
