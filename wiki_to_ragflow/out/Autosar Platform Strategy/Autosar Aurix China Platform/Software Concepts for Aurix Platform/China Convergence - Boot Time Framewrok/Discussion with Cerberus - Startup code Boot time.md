# Discussion with Cerberus - Startup code Boot time

> Source: /spaces/CARSFW/pages/2849119548/Discussion+with+Cerberus+-+Startup+code+Boot+time
> Last modified: 2023-03-17T02:31:13.000+01:00

---

### Date: 17 Mar 2023

### Participants :  Petar, Marin, Newton, Praveen

### Meeting minutes:

Details of ~ approximate startup time

- IFX firmware -  3.5ms
- BM < 3ms (Just jump to application without Reset)
- APP startup code
- Total time to enter APP main would be ~ 20ms

> **INFO: LBIST execution**
> Currently LBIST is executed in APP startup code. But better to do this in IFX Firmware itself which will reduce startup code timing by few ms (~ 3-4 ms)

First CAN message in EVAL board

- Cerberus able to send first message in ~40ms after main

Slave Core start timing

- Master - Slave synchronization will not have a big delay because slave core startup time is <2ms

Boot time framework in Startup code

- Cerberus Startup doesn't support this framework. Project team needs to measure on their own with debug environment.

Callout from Startup code

- There is a project callout for each core when startup code is started in Application (Startup_Core0_Callout, Startup_Core1_Callout, Startup_Core2_Callout)
- Project can use this callout for any measurement

:
