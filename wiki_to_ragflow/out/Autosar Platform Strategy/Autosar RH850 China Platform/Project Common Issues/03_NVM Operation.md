# 03_NVM Operation

> Source: /spaces/CARSFW/pages/2413429575/03_NVM+Operation
> Last modified: 2022-10-27T09:39:33.000+02:00

---

- 1. Issue 1 - NVM Write operation took too long time during sleep

## 1. Issue 1 - NVM Write operation took too long time during sleep

### 1.1. Information

- When clear DTC or write some configuration words,  if you power off , the critical data probability cannot be successfully written to NVM.
- When MCU executes sleep process, it takes about 7s.  Most of the time spent on NVM_ WriteAll();
- When write 4 byte NVM data

### 1.2. Analysis

NVM_WriteAll()/NVM_WriteBlock() only erase and programming data flash, but According to the manual of RH850，The erase/programming one block(64 byte) can be completed within 10ms. Therefore, we suspect that the problem lies in the Vector NVM operation process

![](../../../_images/03_NVM%20Operation/image2022-9-15_11-9-1.png)

### 1.3. Solution

move the main function of Fee and vMem from the 5ms task to the IDLE Task to increase the scheduling frequency and make the NVM state machine update quickly

Fee_30_SmallSector_MainFunction(); Fls_30_vMemAccM_MainFunction(); vMemAccM_MainFunction(); vMem_30_Rh850Faci01_MainFunction();

### 1.4. Fix Status

|   |   |   |
| --- | --- | --- |
| Affected Project | Fix Status | Gerrit/RTC linkage |
| GAC A58/A88 | COMPLETED |  |
| GEELY | COMPLETED | Story 1522208 |

### 1.5. Reference:

Synchronous/Asynchronous of API
