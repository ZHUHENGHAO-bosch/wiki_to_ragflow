# 1.0 SAIL SW Bringup - Features and Status

> Source: /spaces/CARSFW/pages/4704573818/1.0+SAIL+SW+Bringup+-+Features+and+Status
> Last modified: 2025-04-09T12:02:02.000+02:00

---

## Overview

This page is to discuss on the steps for SAIL bring up in QC8255/QAM8775

### Agenda:

By end of OCT we need a running SW in SAIL domain with DADDY and Flux Model Integrated

Module analysis - SAIL - Modules from QC - Analysis - XC-CT China - Docupedia (bosch.com)

Highlights:

HW ready by 22-11-2024 in Suzhou → delayed to December 10th

Important points: 19 Nov 2024

- QC no side loading hypervisor is not working with large size elf - LIU Dezhi (XC-CP/ESW2-CN) following up with QC
- Start the build environment creating for 3rd party - WU Mingen (XC-CP/ESW2-CN) and Jayaraj Praveen (BCSC/ENG1) - Will start
- NVM dependency - WU Jianqiang (XC-CP/ESW2-CN)
- QC change DTS for hypervisor - LIU Dezhi (XC-CP/ESW2-CN) currently issues, following up with QC
- Testing mailbox with MD

#### Blockers:

3.0 SAIL - Issue, fixes and lesson learnt - XC-CT China - Docupedia

28 Nov 2024 LI Minsheng (XC-CP/ESW2-CN) will go to Suzhou for CCU bring up

- Prepared a local SW for the bring up

### Important Notes:

- For now Flux generation is commented
- Cmake is enabled only for needed component - Make sure to check enable when you start bring up of specific module

| Module | Version | Comments |
| --- | --- | --- |
| RTA-OS |  |  |
| QC MCAL & CDD | ES6 0.0.008.1 | CCU 8775 follow VCU Pro， used ES06 vesion how to get the QC source code QC chipcode: https://chipcode.qti.qualcomm.com/robert-bosch-gmbh/snapdragon-auto-hqx-4-5-6-0_hlos_dev_autosar/tree/r00008.1 git config --global http.followRedirects true git clone https://qpm-git.qualcomm.com/home2/git/robert-bosch-gmbh/snapdragon-auto-hqx-4-5-6-0_hlos_dev_autosar.git Bosch Gerrit： https://rbcm-gerrit.de.bosch.com/plugins/gitiles/external/qualcomm/qnx/snapdragon-auto-hqx-4-5-6-0_hlos_dev_autosar/+/refs/heads/qcom_init_es06_r00008.1 git clone ssh://rbcm-gerrit.de.bosch.com:29418/external/qualcomm/qnx/snapdragon-auto-hqx-4-5-6-0_hlos_dev_autosar git checkout qcom_init_es06_r00008.1 |
| Cubas stack |  |  |

Tasks:

| Feature | Tasks | Responsible | Status | Comments |
| --- | --- | --- | --- | --- |
| Build Framework Setup | Create Folder structure in Wiki | Jayaraj Praveen (BCSC/ENG1) LIU Dezhi (XC-CP/ESW2-CN) | COMPLETED | Waiting for which direction we should go Taiji J6E Remove the T32 from repo - keep it in antifactory Prepare an environment for PATAC - we will give as single library and environment |
| Create manifest according to folder structure | Jayaraj Praveen (BCSC/ENG1) LIU Dezhi (XC-CP/ESW2-CN) | COMPLETED | repo init -u cm_gerrit:projects/taiji/manifests -b rb-ccufusion_main_dev -m rb-patac-ccufusion.xml -g sail |
| Analyze whether current Cmake system can support generation of .a and header file | Jayaraj Praveen (BCSC/ENG1) WU Mingen (XC-CP/ESW2-CN) | INPROGRESS | Started anlaysis Checked the GM build environment Taiji used Python to copy the lib |
| Prepare environment for Third party delivery |  | TOBESTARTED | When needed? before 20/Dec |
| Initial clean up and deliver to repo | Jayaraj Praveen (BCSC/ENG1) | INPROGRESS |  |
| Use same CMAKE architecture of J6E. btc_tools also support armclang compiler support. We just need to configure the setting properly Refer FSI settings in ARM-CLANG.R52.toolchain.cmake | WU Mingen (XC-CP/ESW2-CN) | COMPLETED | Find old J6E version which had only Flux environment WU Mingen (XC-CP/ESW2-CN) |
| Make a sample project with Flux demo and Arm compiler | WU Mingen (XC-CP/ESW2-CN) | COMPLETED |  |
| OS Bringup | Integrate RTA-OS into Build | Jayaraj Praveen (BCSC/ENG1) | COMPLETED |  |
| Make RTA-OS up for single core | Jayaraj Praveen (BCSC/ENG1) | COMPLETED |  |
| Make RTA-OS up for Multicore | Jayaraj Praveen (BCSC/ENG1) | COMPLETED | Contact with ETAS ongoing Dezhi has pushed QC, QC informed they are discussing internally Issue with SP on slave cores. Praveen integrating to latest repo and deliver after a small clean up Changes are delivered |
| make the timer setting properly | Jayaraj Praveen (BCSC/ENG1) | COMPLETED | Tested with Analyzer. OS timing is proper. SAIL - RTA-OS - XC-CT China - Docupedia (bosch.com) |
| MCAL and Startup code | Integrate startup code and scatter file | Jayaraj Praveen (BCSC/ENG1) | COMPLETED | Delivered into SAIL Bringup branch |
| Integrate necessary MCAL and its CDD modules | MCAL Owner Status Setup project .dpa LI Minsheng (XC-CP/ESW2-CN) COMPLETED Mcu LI Minsheng (XC-CP/ESW2-CN) WU Mingen (XC-CP/ESW2-CN) COMPLETED Port LI Minsheng (XC-CP/ESW2-CN) COMPLETED Dio LI Minsheng (XC-CP/ESW2-CN) COMPLETED Uart WU Mingen (XC-CP/ESW2-CN) COMPLETED Spi LI Minsheng (XC-CP/ESW2-CN) Sync - COMPLETED Async - PENDING Interrupt is not coming Wdg Gpt Jayaraj Praveen (BCSC/ENG1) INPROGRESS Pwm No MCAL available in QC - Case is raised LIU Dezhi (XC-CP/ESW2-CN) Jayaraj Praveen (BCSC/ENG1) Icu No MCAL available in QC - Case is raised Clock LI Minsheng (XC-CP/ESW2-CN) COMPLETED GPIO edge detect LI Minsheng (XC-CP/ESW2-CN) COMPLETED |  | MCAL | Owner | Status | Setup project .dpa | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED | Mcu | LI Minsheng (XC-CP/ESW2-CN) WU Mingen (XC-CP/ESW2-CN) | COMPLETED | Port | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED | Dio | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED | Uart | WU Mingen (XC-CP/ESW2-CN) | COMPLETED | Spi | LI Minsheng (XC-CP/ESW2-CN) | Sync - COMPLETED Async - PENDING Interrupt is not coming | Wdg |  |  | Gpt | Jayaraj Praveen (BCSC/ENG1) | INPROGRESS | Pwm | No MCAL available in QC - Case is raised LIU Dezhi (XC-CP/ESW2-CN) Jayaraj Praveen (BCSC/ENG1) |  | Icu | No MCAL available in QC - Case is raised |  | Clock | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED | GPIO edge detect | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED | MCU Port GPT Mailbox i2c Uart S1: Mingen to integrate OS into baremetal system and test in our HW S2:Minsheng to intergrate es6 version to our repo, configure MCAL in davinci and start testing one by one Tested and delivered Alive led which is configured in Port and Dio |
| MCAL | Owner | Status |
| Setup project .dpa | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED |
| Mcu | LI Minsheng (XC-CP/ESW2-CN) WU Mingen (XC-CP/ESW2-CN) | COMPLETED |
| Port | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED |
| Dio | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED |
| Uart | WU Mingen (XC-CP/ESW2-CN) | COMPLETED |
| Spi | LI Minsheng (XC-CP/ESW2-CN) | Sync - COMPLETED Async - PENDING Interrupt is not coming |
| Wdg |  |  |
| Gpt | Jayaraj Praveen (BCSC/ENG1) | INPROGRESS |
| Pwm | No MCAL available in QC - Case is raised LIU Dezhi (XC-CP/ESW2-CN) Jayaraj Praveen (BCSC/ENG1) |  |
| Icu | No MCAL available in QC - Case is raised |  |
| Clock | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED |
| GPIO edge detect | LI Minsheng (XC-CP/ESW2-CN) | COMPLETED |
| Integrate necessary QC CDD Modules | Feature Modules Owner Status Inter domain communication CDD_Ipcc CDD_Mailbox CDD_Isd WU Mingen (XC-CP/ESW2-CN) Jayaraj Praveen (BCSC/ENG1) IPCC communication document Code is pushed Test Mailbox with MD LIU Dezhi (XC-CP/ESW2-CN) WU Mingen (XC-CP/ESW2-CN) Test with MD user channel. Need ESW1 support I2C and PMIC CDD_I2c CDD_Pmic LI Minsheng (XC-CP/ESW2-CN) I2C - COMPLETED PMIC - COMPLETED Can read and write PMIC register Logging CDD_Uart CDD_DebugLog WU Mingen (XC-CP/ESW2-CN) COMPLETED SAIL-CDD_Uart & CDD_DebugLog - XC-CT China - Docupedia (bosch.com) Extensive boot loader CDD_Xbl CDD_Qfprom Jayaraj Praveen (BCSC/ENG1) INPROGRESS FuSa Error handler CDD_Fusa CDD_Ssm Dezhi Environment set up is completed FuSa Monitoring - phase 1 CDD_Monitor CDD_Acmu Dezhi FuSa - Monitoring - phase 2 CDD_Icb CDD_Psail Dezhi FuSa Volt and Temp monitoring CDD_Vsens CDD_Tsens Dezhi |  | Feature | Modules | Owner | Status | Inter domain communication | CDD_Ipcc CDD_Mailbox CDD_Isd | WU Mingen (XC-CP/ESW2-CN) Jayaraj Praveen (BCSC/ENG1) | IPCC communication document Code is pushed | Test Mailbox with MD |  | LIU Dezhi (XC-CP/ESW2-CN) WU Mingen (XC-CP/ESW2-CN) | Test with MD user channel. Need ESW1 support | I2C and PMIC | CDD_I2c CDD_Pmic | LI Minsheng (XC-CP/ESW2-CN) | I2C - COMPLETED PMIC - COMPLETED Can read and write PMIC register | Logging | CDD_Uart CDD_DebugLog | WU Mingen (XC-CP/ESW2-CN) | COMPLETED SAIL-CDD_Uart & CDD_DebugLog - XC-CT China - Docupedia (bosch.com) | Extensive boot loader | CDD_Xbl CDD_Qfprom | Jayaraj Praveen (BCSC/ENG1) | INPROGRESS | FuSa Error handler | CDD_Fusa CDD_Ssm | Dezhi | Environment set up is completed | FuSa Monitoring - phase 1 | CDD_Monitor CDD_Acmu | Dezhi |  | FuSa - Monitoring - phase 2 | CDD_Icb CDD_Psail | Dezhi |  | FuSa Volt and Temp monitoring | CDD_Vsens CDD_Tsens | Dezhi |  | CDD_Ipcc CDD_Mailbox CDD_Uart CDD_Pmic ?? May be other CDD needed when start testing and do integration SAIL - CDD_Ipcc - XC-CT China - Docupedia (bosch.com) SAIL - CDD_Mailbox - XC-CT China - Docupedia (bosch.com) SAIL - CDD_Isd - XC-CT China - Docupedia |
| Feature | Modules | Owner | Status |
| Inter domain communication | CDD_Ipcc CDD_Mailbox CDD_Isd | WU Mingen (XC-CP/ESW2-CN) Jayaraj Praveen (BCSC/ENG1) | IPCC communication document Code is pushed |
| Test Mailbox with MD |  | LIU Dezhi (XC-CP/ESW2-CN) WU Mingen (XC-CP/ESW2-CN) | Test with MD user channel. Need ESW1 support |
| I2C and PMIC | CDD_I2c CDD_Pmic | LI Minsheng (XC-CP/ESW2-CN) | I2C - COMPLETED PMIC - COMPLETED Can read and write PMIC register |
| Logging | CDD_Uart CDD_DebugLog | WU Mingen (XC-CP/ESW2-CN) | COMPLETED SAIL-CDD_Uart & CDD_DebugLog - XC-CT China - Docupedia (bosch.com) |
| Extensive boot loader | CDD_Xbl CDD_Qfprom | Jayaraj Praveen (BCSC/ENG1) | INPROGRESS |
| FuSa Error handler | CDD_Fusa CDD_Ssm | Dezhi | Environment set up is completed |
| FuSa Monitoring - phase 1 | CDD_Monitor CDD_Acmu | Dezhi |  |
| FuSa - Monitoring - phase 2 | CDD_Icb CDD_Psail | Dezhi |  |
| FuSa Volt and Temp monitoring | CDD_Vsens CDD_Tsens | Dezhi |  |
| Environment Setup | Debug the standalone SW with Lauterbach | Jayaraj Praveen (BCSC/ENG1) | COMPLETED |  |
| Create a signed elf with secure tools | GENG Zhongyang (BCSC/ENG1) | COMPLETED |  |
| Deliver the T32 to antifactory, delete the T32 from repo and update the wiki page | GENG Zhongyang (BCSC/ENG1) | COMPLETED | Discussed with toolbase team. seems t32 is already available in toolbase. Zhongyang will install the teool from toolbase, make sure the tool can work and change the batch file |
| Create a script which will launch T32 and run the cmm script and attach to CPU directly | GENG Zhongyang (BCSC/ENG1) | COMPLETED | Create a bat file which will open and attach with CPU and the load elf with Nocode option |
| Create a QC environment - where we can create an EL2 binary with DTC tools and configuration | LIU Dezhi (XC-CP/ESW2-CN) | COMPLETED | ( ES08 begin have autosar version sailhyp_nosym.elf https://chipcode.qti.qualcomm.com/robert-bosch-gmbh/snapdragon-auto-hqx-4-5-6-0_hlos_dev_autosar/tree/r00010.1 ) Wiki page for creating Hypervisor elf is completed 4.0 SAIL - DTS - XC-CT China - Docupedia (bosch.com) |
| Understand how to change contents.xml file which is used to decide which binary to flash and the size - PCAT flashing | LIU Dezhi (XC-CP/ESW2-CN) | INPROGRESS | Small queries - analyzing further |
| BSW Bringup | BSW stack integration Few API may not be compatible, we should understand and try to solve by writing a wrapper  module | Feature Owner Status Integrate the Cubas package. Create AEEE project setup Make Build complete in BCT with default config Jianqiang COMPLETED Integrate EcuM Create a simple Module Service.EcuModeManager - Just implement the callouts Main shall call EcuM_Init Move the MCAL init to Driverinitone EcuM shall start the OS Jianqiang COMPLETED BswM integration Create a Simple rule in config - Just called BswM_init and BswM_mainfunction Jianqiang COMPLETED Memory stack integration Integrate the Mem and Memacc → test the read/write with simple test function Integrate the NVM from Cubas and test the whole Mem stack module (WriteAll, ReadAll, read and write Block) Jianqiang COMPLETED Work only on 8775, not on 8225 SNOR memory size is different. Sector number is number NVM and FEE and test with Rte BLOCK Integrate Rte make Rte generation success with default configuration Config two SWCs, test C/S and S/R Jianqiang COMPLETE Rte code generation is success Rte is running ok Optimize the composition in AEEE Jianqiang INPROGRESS Wdg Stack integration Integrate Wdg driver from QC Integrate WdgM, WdgIf Wdg refresh shall work properly Wdg Alive supervision for Basic task Jianqiang INPROGRESS EcuM shutdown Jianqiang |  | Feature | Owner | Status | Integrate the Cubas package. Create AEEE project setup Make Build complete in BCT with default config | Jianqiang | COMPLETED | Integrate EcuM Create a simple Module Service.EcuModeManager - Just implement the callouts Main shall call EcuM_Init Move the MCAL init to Driverinitone EcuM shall start the OS | Jianqiang | COMPLETED | BswM integration Create a Simple rule in config - Just called BswM_init and BswM_mainfunction | Jianqiang | COMPLETED | Memory stack integration Integrate the Mem and Memacc → test the read/write with simple test function Integrate the NVM from Cubas and test the whole Mem stack module (WriteAll, ReadAll, read and write Block) | Jianqiang | COMPLETED Work only on 8775, not on 8225 SNOR memory size is different. Sector number is number NVM and FEE and test with Rte BLOCK | Integrate Rte make Rte generation success with default configuration Config two SWCs, test C/S and S/R | Jianqiang | COMPLETE Rte code generation is success Rte is running ok | Optimize the composition in AEEE | Jianqiang | INPROGRESS | Wdg Stack integration Integrate Wdg driver from QC Integrate WdgM, WdgIf Wdg refresh shall work properly Wdg Alive supervision for Basic task | Jianqiang | INPROGRESS | EcuM shutdown | Jianqiang |  | BSW package added in teh repo. All J6E used module can compile - delivered NVM Stack → MemAcc and Mem from QC is not complete. es8 package is not complete. LIU Dezhi (XC-CP/ESW2-CN) to follow up. No need any wrapper. Mem Generator also placed in project Will Start running the AR modules one by one. Starting with EcuM, BswM MemAcc lacks AR interface with NVM. Jianqiang informed Dezhi. DEzhi already created a QC Case. waiting for the update Seems ES08 has also no AR interfaces Mem/MemACC also can work on 8255, need updated the MCAL update for Mem,(SPI Nor size: for QC8255 : 32MB for QC8775 : 256MB Wiki page refer: How to configure SAIL NorFlash - XC-CT China - Docupedia (bosch.com) NVMstack intergration with uncomplete MemAcc/Mem module - XC-CT China - Docupedia Need add the WIKI for How to cfg RTE, pending |
| Feature | Owner | Status |
| Integrate the Cubas package. Create AEEE project setup Make Build complete in BCT with default config | Jianqiang | COMPLETED |
| Integrate EcuM Create a simple Module Service.EcuModeManager - Just implement the callouts Main shall call EcuM_Init Move the MCAL init to Driverinitone EcuM shall start the OS | Jianqiang | COMPLETED |
| BswM integration Create a Simple rule in config - Just called BswM_init and BswM_mainfunction | Jianqiang | COMPLETED |
| Memory stack integration Integrate the Mem and Memacc → test the read/write with simple test function Integrate the NVM from Cubas and test the whole Mem stack module (WriteAll, ReadAll, read and write Block) | Jianqiang | COMPLETED Work only on 8775, not on 8225 SNOR memory size is different. Sector number is number NVM and FEE and test with Rte BLOCK |
| Integrate Rte make Rte generation success with default configuration Config two SWCs, test C/S and S/R | Jianqiang | COMPLETE Rte code generation is success Rte is running ok |
| Optimize the composition in AEEE | Jianqiang | INPROGRESS |
| Wdg Stack integration Integrate Wdg driver from QC Integrate WdgM, WdgIf Wdg refresh shall work properly Wdg Alive supervision for Basic task | Jianqiang | INPROGRESS |
| EcuM shutdown | Jianqiang |  |
| CAN bring up - Analysis and Integration | Feature Owner Status Integrate CAN driver from QC and CAN transceiver from Qc/Cubas Test in Nessy board. send tx and Rx Qinpeng BLOCKER test code is delivered. One issue is CAN driver module. Need time to analyze and fix Controller state not moving from Stopped to Start Check the MCAL configuration whether Port is in sync with 8775 HW layout Port configuration is made for all CAN. Only touch CAN is TJA1152 - Stb pin Integrate COM stack - CANSM, COM, COMM COMPLETE We cannot test and make build and run in HW Import a arxml from VCU pro and configure the com relevant part. Test in HW. Make sure we can receive a com signal in com callback Used one click com - Solution 1 - COMPLETE Delivery has to be done again Solution 2- Java importer - INPROGRESS Tool is delivered Java importer has some issues → Need to check with ETAS about this issue - No update from ETAS team |  | Feature | Owner | Status | Integrate CAN driver from QC and CAN transceiver from Qc/Cubas Test in Nessy board. send tx and Rx | Qinpeng | BLOCKER test code is delivered. One issue is CAN driver module. Need time to analyze and fix Controller state not moving from Stopped to Start Check the MCAL configuration whether Port is in sync with 8775 HW layout Port configuration is made for all CAN. Only touch CAN is TJA1152 - Stb pin | Integrate COM stack - CANSM, COM, COMM |  | COMPLETE We cannot test and make build and run in HW | Import a arxml from VCU pro and configure the com relevant part. Test in HW. Make sure we can receive a com signal in com callback |  | Used one click com - Solution 1 - COMPLETE Delivery has to be done again Solution 2- Java importer - INPROGRESS Tool is delivered Java importer has some issues → Need to check with ETAS about this issue - No update from ETAS team | Can driver up - QC - configured in Vector Used a dummy configuration and can generate COM module in Sail repo Problem with CCU - GM SOLVED CCU has single arxml - we can not use one click so we need to convert Single arxml to dbc → Qinpeng used  canconvert.exe to convert arxml to dbc With this dbc - oneclick com is working properly Once Minsheng did MCAL configuration, testing will be started Nessy CAN transceiver details: TJA1153A, TLE9255WLC, TJA1153A, TJA1152AT ![(minus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/forbidden.svg) Nessy HW has issue, we can not use Nessy to test CAN, need to wait for our own sample |
| Feature | Owner | Status |
| Integrate CAN driver from QC and CAN transceiver from Qc/Cubas Test in Nessy board. send tx and Rx | Qinpeng | BLOCKER test code is delivered. One issue is CAN driver module. Need time to analyze and fix Controller state not moving from Stopped to Start Check the MCAL configuration whether Port is in sync with 8775 HW layout Port configuration is made for all CAN. Only touch CAN is TJA1152 - Stb pin |
| Integrate COM stack - CANSM, COM, COMM |  | COMPLETE We cannot test and make build and run in HW |
| Import a arxml from VCU pro and configure the com relevant part. Test in HW. Make sure we can receive a com signal in com callback |  | Used one click com - Solution 1 - COMPLETE Delivery has to be done again Solution 2- Java importer - INPROGRESS Tool is delivered Java importer has some issues → Need to check with ETAS about this issue - No update from ETAS team |
| Others |  |  |  |
| Middleware - Daddy | Merge the workable SW in to Build framework | WU Mingen (XC-CP/ESW2-CN) | TBD |  |
| Test the DADDY middleware for demo module |  | TBD | We will go with ETAS SUM Keep this in mind DBC - Use simple for bring up Will come from PATAC later We will use Rte from ETAS Check dependency with ETAS team Rte Dbc Sum |
| USS | USS relevant handling | user-054ef Jayaraj Praveen (BCSC/ENG1) | INPROGRESS | CCU - USS dependency with SAIL Analysis - XC-CT China - Docupedia |
| Others | Make sure MD is up with our SAIL | Jayaraj Praveen (BCSC/ENG1) LIU Dezhi (XC-CP/ESW2-CN) | COMPLETED | MD is working properly with EL SW check below link for more details Main domain not up with local SAIL EL1 SW - XC-CT China - Docupedia (bosch.com) |
| Time Sync - Stbm and CanTsync Integration and test of Time sync mechanism | YAN Eason (XC-AS/PJ-ET-ETW) | INPROGRESS | Start by integrating Stbm and CanTsync module to build and test in real board SW Arch meeting started - some OPL no HW module available to support time sync between MD and SAIL Gptp → protocol over Ethernet Lets start by integrate Stbm and other base |
| XCP - Not that urgent |  |  | Integrate and keep it ready |
| EINC - Integration | WU Mingen (XC-CP/ESW2-CN) - Compile and Run → Second phase | PENDING | Start from 18-11-2024 Seems EINC is not started |
| SAIL communication with SCC |  |  | Current UART is used for safety → can we use it for both FuSa and QM PATAC needs this for SWC signals and some information Simple protocol on top of UART liteINC - check for any existing solution |
| Diagram that explain peripherals connected to SAIL Like USS, CAN | Jayaraj Praveen (BCSC/ENG1) | COMPLETED | 1.0 CCU - System Overview - XC-CT China - Docupedia (bosch.com) |
| Draft Software architecture for CCU | Jayaraj Praveen (BCSC/ENG1) | COMPLETED |  |
| Get feature list and plan for SAIL (Which board - CCU, demo) | LIU Dezhi (XC-CP/ESW2-CN) | COMPLETED | 12.1 system run 12. 15  data path ok sensor (SPI, CAN) IPC(communication with A-core) EINC RTE ready with ASW Uart with TC387 12.20 time sync ok 1.15 XCP ok now status: CCU8775 Demo Schematic reviewing |
| Toggle Alive led for SAIL to make sure we can identify SAIL aliveness via debug board | Jayaraj Praveen (BCSC/ENG1) | COMPLETED |  |
| Create proper Memory layout in LD file | Jayaraj Praveen (BCSC/ENG1) |  | Memory layout SRAM is only 3 MB. Maybe we need to use DDR for application part. Raised a query to QC to check how to use DDR for application Should be possible with direct memory access - but with little performance |
|  | CCU HW layout review and understand the usage of Pins | Jayaraj Praveen (BCSC/ENG1) LIU Dezhi (XC-CP/ESW2-CN) LI Minsheng (XC-CP/ESW2-CN) | COMPLETED | CCU 8775 HW Block review - XC-CT China - Docupedia (bosch.com) |
|  | Boot Configuration | Jayaraj Praveen (BCSC/ENG1) | COMPLETED | 1.0 SAIL Boot Configuration - XC-CT China - Docupedia (bosch.com) |
|  | Buy two Lauterbach | LIU Dezhi (XC-CP/ESW2-CN) | COMPLETED | Dezhi got it |
|  | Add Arm  license | CAI Jiachao (XC-CP/ESW2-CN) | COMPLETED | Added 10 license till end of March |
|  | QC hypervisor without Lauterbach | LIU Dezhi (XC-CP/ESW2-CN) | COMPLETED | Working with QC workaround hypervisor for 8255 |
|  | Large size elf loading - issue analysis | Jayaraj Praveen (BCSC/ENG1) | COMPLETED | Works with delay workaround in hypervisor |
| 2025.04.09 |  |  |  |  |
|  | bugfix -Ssm_MailboxInitStatus was modified unexpected |  |  |  |
|  | Uart log need Asynchronous (now uart print is synchronous, Performance is affected) |  |  |  |
|  | need OS IOC (now  used CDD_Ssm_OSIoc.h ) |  |  |  |
|  |  |  |  |  |

12.02  Paused  the development of SAIL, This week, we put the code and documentation together and then pause for further information on the project

Todos:

1. RTE related documents and code – wujianqiang
2. porting ES09 to CCU Fusion repo – praveen
3. test if MD enter safe state or not with ES09 SAIL – Liu Dezhi
4. continue push QC to provide how to modify clock/ICU registers – Liu Dezhi
5. About jenkins(verify+1 Automatic), push Lu weihua finish – Liu Dezhi
6. 3th Party envirnoment need more time(not start now), no need finish
