# LCM Status Meeting - 02 2023

> Source: /spaces/CARSFW/pages/2708468862/LCM+Status+Meeting+-+02+2023
> Last modified: 2023-02-23T09:10:58.000+01:00

---

### Date : 23 Feb 2023

### Participants: Shanhe, Joanna, Jolin , Can

### Meeting Minutes:

Zeekr activity

1. LCM related log saving in Retention RAM
2. Diagnostic reset porting from BYD project
3. Code clean about IoHwAb & Dio in LCM
4. Discussion the root cause of debug reset issue and I2C fatalerror issue with ECT team
5. Multicore Startup Sync
6. Multi core sync shutdown and reset
7. LCM related memmap files generating

BYD activity

1. Memmap for PSC and LCMC.
2. More handling for multicore.
3. STR (wait for SOC side) - Waiting for SoC
4. Adapt LCM EA to real implementation.
5. Intergrate the ECUM supervision to zeekr project.
6. Review LCM config in new project
7. Still in end of the line (   UT and Coverity and test spec  )

Zeekr-Other

1. Thermal
2. SoC State Monitor - FuSa

Chery

1. LCM adaption for Chery
2. Test LCM use cases in Chery
3. Voltage
4. SCR is delivered - Tested with ACC

Any changes in Zeekr shall be delivered to Chery

General - Few are the project specific configuration are in PF, we need to move to project config repo. @Joanna - to come back on list

### Open points:

- Cyclic Reset Handling - Will be on hold till we find the Startup code responsible team
- Wdg Monitoring for LCM components - Low priority
- STR
- SCR
- HW monitoring - Very low priority
- SWRS
- Multicore
- Aurix - Need to focus
- LCM Dispatcher

### Date : 09 Feb 2023

### Participants: Shanhe, Joanna, Jolin , Can

### Meeting Minutes:

Zeekr activity

1. Customer requirement achievement: Wakeup logic coding, Voltage management
2. LCM related log saving in Retention RAM
3. Zeekr SWRS filling in Doors
4. Diagnostic reset porting from BYD project
5. Code clean about IoHwAb&Dio in LCM
6. SCR pin adapter in A1 board
7. Discussion the root cause of debug reset issue and I2C fatalerror issue with ECT team
8. Multicore Startup Sync
9. Multi core sync shutdown and reset
10. LCM related memmap files generating
11. Comparing the A2 HW changed with A0
12. External WDG Testing
13. A2 board bring up

BYD activity

1. BYD Customer real car issue analysis (for now there are two issue).
2. Diag team function implementation.
3. Memmap for PSC and LCMC.
4. More handling for multicore.
5. STR (wait for SOC side) - Waiting for SoC
6. Adapt LCM EA to real implementation.
7. Intergrate the ECUM supervision to zeekr project.
8. Review LCM config in new project
9. Still in end of the line (   UT and Coverity and test spec  )

Zeekr-Other

1. Thermal
2. SoC State Monitor - FuSa

Chery

1. LCM adaption for Chery
2. Test LCM use cases in Chery
3. Voltage

Any changes in Zeekr shall be delivered to Chery

General - Few are the project specific configuration are in PF, we need to move to project config repo. @Joanna - to come back on list

### Open points:

- Cyclic Reset Handling - Will be on hold till we find the Startup code responsible team
- Wdg Monitoring for LCM components - Low priority
- STR
- SCR
- HW monitoring - Very low priority
- SWRS
- Multicore
- Aurix - Need to focus
- LCM Dispatcher

### Date : 03 Feb 2023

### Participants: Shanhe, Joanna, John, Can

### Meeting Minutes:

Zeekr activity

1. Customer requirement achievement: Wakeup logic coding, Voltage management
2. LCM related log saving in Retention RAM
3. Zeekr SWRS filling in Doors
4. Diagnostic reset porting from BYD project
5. Code clean about IoHwAb&Dio in LCM
6. SCR pin adapter in A1 board
7. Discussion the root cause of debug reset issue and I2C fatalerror issue with ECT team
8. Multicore Startup Sync
9. Multi core sync shutdown and reset
10. LCM related memmap files generating
11. Comparing the A2 HW changed with A0
12. External WDG Testing

BYD activity

1. BYD Customer real car issue analysis (for now there are two issue).
2. Diag team function implementation.
3. Memmap for PSC and LCMC.
4. More handling for multicore.
5. STR (wait for SOC side) - Waiting for SoC
6. Adapt LCM EA to real implementation.
7. Intergrate the ECUM supervision to zeekr project.
8. Review LCM config in new project
9. Still in end of the line (   UT and Coverity and test spec  )

Zeekr-Other

1. Thermal
2. SoC State Monitor - FuSa

General - Few are the project specific configuration are in PF, we need to move to project config repo. @Joanna - to come back on list

### Open points:

- Cyclic Reset Handling - Will be on hold till we find the Startup code responsible team
- Wdg Monitoring for LCM components - Low priority
- STR
- SCR
- HW monitoring - Very low prioirity
- SWRS
- Multicore
- Aurix - Need to focus
- LCM Dispatcher
