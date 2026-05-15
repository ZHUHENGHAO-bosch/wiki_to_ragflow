# Multicore Status - 11-2022

> Source: /spaces/CARSFW/pages/2491260876/Multicore+Status+-+11-2022
> Last modified: 2022-11-18T12:16:18.000+01:00

---

### Multi Core Enabler Zeekr Sync

### Participants: Shanhe, Minsheng, Praveen, Santhosh, Newton

### Date: 07 Nov 2022

### Meeting Minutes:

Smoke test results

| T.NO | Test Case | Test Case Steps | Result | Responsible |
| --- | --- | --- | --- | --- |
| 1 | EcuM Mode Management | Make Sure EcuM enters to GSSRUN | OK | Santhoshkumar C (MS/ENE-EE4-XC) |
| 2 | FR | FR Tx and Rx Msgs | OK | LI Minsheng (XC-CP/ESW2-CN) |
| 3 | CAN | CAN Tx and Rx Msgs | OK | LI Minsheng (XC-CP/ESW2-CN) |
| 4 | LIN | LIN Tx and Rx Msgs | OK | LI Minsheng (XC-CP/ESW2-CN) |
| 5 | LCM - Sleep and Wakeup | With IGN pin - Sleep and Wakeup | OK | TAN Shanhe (XC-CP/ESW2-CN) |
| 6 | General | No Resets | OK | Santhoshkumar C (MS/ENE-EE4-XC) |
|  |  |  |  |  |

#### Action points

Santhoshkumar C (MS/ENE-EE4-XC) to deliver the changes today including UCB - Try to not change the start address

user-1f19a

TAN Shanhe (XC-CP/ESW2-CN) to deliver the commit in CNCONVBASE

Topic build - Santhosh and Shanhe - COMPLETED

After Delivery:

LI Minsheng (XC-CP/ESW2-CN) - New repo Sync and Test communication once - All test passed OK

Santhoshkumar C (MS/ENE-EE4-XC) - Do it in ECT set up

Santosh to work on clean up

LCM_Aurix_Review.xlsx MC_Enable_Review.xlsx

### Participants: Praveen, Santhosh, Yogashri, Senthil

### Date: 08 Nov 2022

### Meeting Minutes:

Santhoshkumar C (MS/ENE-EE4-XC) to work on clean up 10 Nov 2022

1. [CNCONVPF][MC] Exception and OS Hook Handling
2. [CNCONVPF][MC] RTMO measurement
3. [CNCONVPF][MC]  Memmap Generator Adaption
4. [CNCONVPF][MC]  RAMROM Summary

Yogashri Selvakumar (MS/EBS3-SWC)

- RAMROM summary 10 Nov 2022
- Memmap adaption 09 Nov 2022

Priyanga Balakrishnan (MS/ENE-VD1-XC) 10 Nov 2022

- Exception and OS hook handling
- RTMO

### Participants: Praveen, Santhosh, Yogashri, Senthil

### Date: 09 Nov 2022

### Meeting Minutes:

Santhoshkumar C (MS/ENE-EE4-XC) to work on clean up 10 Nov 2022

1. [CNCONVPF][MC] Exception and OS Hook Handling
2. [CNCONVPF][MC] RTMO measurement
3. [CNCONVPF][MC]  Memmap Generator Adaption
4. [CNCONVPF][MC]  RAMROM Summary

Yogashri Selvakumar (MS/EBS3-SWC)

- RAMROM summary 09 Nov 2022 Simple test and make sure RAMROM summary is generated on each build and deliver today
- Memmap adaption 10 Nov 2022 - BootM - Go with dummy file, FEL → Fix is needed
- Exception handling → Start Creating Test applications 10 Nov 2022

Priyanga Balakrishnan (MS/ENE-VD1-XC) 10 Nov 2022

- Exception and OS hook handling
- RTMO
- Integration of RTMO and OS Hooks, exception handling is completed

> **INFO**
> IP Sprint will be used for understanding the concept and preparations for next sprint

### Participants: Praveen, Santhosh, Yogashri, Senthil

### Date: 10 Nov 2022

### Meeting Minutes:

Santhoshkumar C (MS/ENE-EE4-XC) to work on clean up 10 Nov 2022

- Create an feature for

Yogashri Selvakumar (MS/EBS3-SWC)

- RAMROM summary 09 Nov 2022 Simple test and make sure RAMROM summary is generated on each build and deliver today
- Memmap adaption 10 Nov 2022 - BootM - Go with dummy file, FEL → Fix is needed
- Exception handling → Start Creating Test applications 10 Nov 2022 - Dependency with SC3

Priyanga Balakrishnan (MS/ENE-VD1-XC) 10 Nov 2022

- Exception and OS hook handling
- RTMO

### Participants: Praveen, Santhosh, Yogashri, Senthil

### Date: 11 Nov 2022

### Meeting Minutes:

Santhoshkumar C (MS/ENE-EE4-XC) to work on clean up 10 Nov 2022

11 Nov 2022 Will be delivered today

Yogashri Selvakumar (MS/EBS3-SWC)

- RAMROM summary 09 Nov 2022 Simple test and make sure RAMROM summary is generated on each build and deliver today
- Memmap adaption 10 Nov 2022 - BootM - Go with dummy file, FEL → Fix is needed
- Exception handling → Start Creating Test applications 10 Nov 2022 - Dependency with SC3

Priyanga Balakrishnan (MS/ENE-VD1-XC) 10 Nov 2022

- Exception and OS hook handling
- RTMO - Part 1

### Participants: Praveen, Kumar, Yogashri, Priyanga

### Date: 14 Nov 2022

### Meeting Minutes:

Yogashri Selvakumar (MS/EBS3-SWC) , [CNCONVPF][MC] Error logging - FEL (1.7.0) - Multicore - Module status and plan - XC-CT China - Docupedia (bosch.com)

Priyanga Balakrishnan (MS/ENE-VD1-XC) , Refer 1.6.0 and understand the changes - [CNCONVPF][MC]  MCAL available in slave core

Multicore MCAL Distribution - XC-CT Cerberus Platform - Docupedia (bosch.com)

Test code to access MCAL in one slave core

### Participants: Praveen, Kumar, Yogashri, Priyanga

### Date: 15 Nov 2022

### Meeting Minutes:

Yogashri Selvakumar (MS/EBS3-SWC) , [CNCONVPF][MC] Error logging - FEL (1.7.0) - Multicore - Module status and plan - XC-CT China - Docupedia (bosch.com)

Priyanga Balakrishnan (MS/ENE-VD1-XC) ,RTMO →  Refer 1.6.0 and understand the changes - Many changes were done - Will start integration 15 Nov 2022

Santhoshkumar C (MS/ENE-EE4-XC) → Clean up - Changes are pushed - Delivery by 16 Nov 2022

### Participants: Praveen, Prabu, Yogashri, Priyanga

### Date: 16 Nov 2022

### Meeting Minutes:

Yogashri Selvakumar (MS/EBS3-SWC) , [CNCONVPF][MC] Error logging - FEL (1.7.0) - Multicore - Module status and plan - XC-CT China - Docupedia (bosch.com)

16 Nov 2022 Working on Memmap for Startup code

Priyanga Balakrishnan (MS/ENE-VD1-XC) ,RTMO →  Refer 1.6.0 and understand the changes - Many changes were done - Will start integration 15 Nov 2022

16 Nov 2022 Need to take latest build framework due to Cerberus Cmake dependency; build is done and testing in progress

Santhoshkumar C (MS/ENE-EE4-XC) → Clean up - Changes are pushed - Delivery by 16 Nov 2022

[CNCONVPF][MC] Memory Stack Handling - NVM for IP Sprint

### Participants: Praveen, Santhosh, Yogashri, Priyanga

### Date: 17 Nov 2022

### Meeting Minutes:

Yogashri Selvakumar (MS/EBS3-SWC) , [CNCONVPF][MC] Error logging - FEL (1.7.0) - Multicore - Module status and plan - XC-CT China - Docupedia (bosch.com)

- FEL - Working
- Integration
- Testing

16 Nov 2022 Working on Memmap for Startup code. Delivery : 17 Nov 2022

Priyanga Balakrishnan (MS/ENE-VD1-XC) ,RTMO →  Refer 1.6.0 and understand the changes - Many changes were done - Will start integration 15 Nov 2022

16 Nov 2022 Need to take latest build framework due to Cerberus Cmake dependency; build is done and testing in progress

Testing 17 Nov 2022 , report to be shared and then delivery

Santhoshkumar C (MS/ENE-EE4-XC) → Clean up - Changes are pushed - Delivery by 16 Nov 2022 COMPLETED

[CNCONVPF][MC] Memory Stack Handling - NVM for IP Sprint

### Participants: Praveen, Santhosh, Yogashri, Priyanga

### Date: 18 Nov 2022

### Meeting Minutes:

Yogashri Selvakumar (MS/EBS3-SWC) , [CNCONVPF][MC] Error logging - FEL (1.7.0) - Multicore - Module status and plan - XC-CT China - Docupedia (bosch.com)

- FEL - Working
- Integration
- Testing

Overview of FEL in MC by Yogarshri

Questions

1. They used common ring buffer or individual ring buffer in each core? Single ring buffer used with access to all cores
2. which use case they went → FEL in master core → all core will call FEL_reportError and FEL_Mainfunction will be running in Core 0
3. Guards → How they used

16 Nov 2022 Working on Memmap for Startup code. Delivery : 17 Nov 2022 COMPLETED

Priyanga Balakrishnan (MS/ENE-VD1-XC) ,RTMO →  Refer 1.6.0 and understand the changes - Many changes were done - Will start integration 15 Nov 2022 COMPLETED

Need to check why load is not coming in Core 1 and Core 2 → For next week

RTMO_Cerb_20221117_1231.…
