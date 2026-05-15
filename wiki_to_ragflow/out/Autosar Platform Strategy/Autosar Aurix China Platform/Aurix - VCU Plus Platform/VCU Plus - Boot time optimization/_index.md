# VCU Plus - Boot time optimization

> Source: /spaces/CARSFW/pages/4933323744/VCU+Plus+-+Boot+time+optimization
> Last modified: 2024-10-30T09:39:58.000+01:00

---

## Overview

This page is to summarize the Boot time optimization in VCU Plus project

### Requirement

Customers want to integrate gateway into VCU plus product, due to which they have strict requirement that first CAN message shall be transmitted from the ECU within 70ms

The below measurement was done with Power on reset (PORST)

![](../../../../_images/VCU%20Plus%20-%20Boot%20time%20optimization/image-2024-10-29_14-11-48.png)

### Improvement area and measures

#### HSM:

HSM takes ~20ms to release App core after wakeup.

| Topic Area | Current Time | Tasks done in the time window | Solution | Time after solution | Owner and Status |
| --- | --- | --- | --- | --- | --- |
| HSM + BM | ~20ms | HSM has secure boot feature where it do verification of BM binary before releasing the Application After that it will do parallel secure boot of app Binary | Do parallel secure boot verification of BM binary i.e release App and then do secure boot verification of BM and APP |  | xu zhiyuan |
| Early Startup | ~4ms | The above measurement was done in PORST use case. In PORST, LBIST will be executed in firmware which will take ~2ms. | The requirement from Customer is on the Sleep/wakeup use case. Measure the timing in Sleep/wake up |  |  |
| NvM Read All | ~30ms | Reading all NVM blocks in a while loop ![warning](https://inside-docupedia.bosch.com/confluence/plugins/servlet/twitterEmojiRedirector?id=26a0) GM usually has many NVM blocks compared to Chery | ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) Check and configure the read all option for really needed Blocks. Other NVM blocks, Application has to read directly by using ReadBlock API - SWC dependency - Third Option ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) Asynchronous Read All: Make the NVM readAll from Sync to Async in the background task Use the Rte_Starttiming to activate the task that has dependency with NvM readAll. i.e Activate task of Application which has dependency with NVM after ReadAll is completed ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) Explicit synchronization and NvmCalcRamBlockCrc: Use Retention RAM for RAM mirror variables and enable CRC, with this NVm_Readll will skip the block if the value is not changed |  |  |
| Init task to Prerun | 22.5ms | We have a unused state called WAKUP INIT → WAKEUP → PRERUN (Initialize CAN stack) | ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) Remove the Unused State and make the state transition INIT → PRERUN ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) BswM_Mainfuncti0n runs at 10ms → change to 5ms. This will reduce the transition time |  |  |
| Com stack init to transmit message | 30ms | After CAN stack init, the time taken to transmit the message was 30ms | ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) COM stack are scheduled in 10ms → Change to 5ms which will make the transition of CANSM, CAN driver and CAN transceiver modules fastre ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) Arrange the Main function of COM stack properly, so that there is no delay in first can message transmission. If CANSM is below NM main function, then CANSM will change it state but only in next cycle, NM will start transmission |  |  |
