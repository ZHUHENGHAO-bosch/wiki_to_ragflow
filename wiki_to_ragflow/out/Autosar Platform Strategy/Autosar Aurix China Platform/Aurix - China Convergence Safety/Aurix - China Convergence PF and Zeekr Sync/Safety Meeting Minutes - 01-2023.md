# Safety Meeting Minutes - 01-2023

> Source: /spaces/CARSFW/pages/2620933875/Safety+Meeting+Minutes+-+01-2023
> Last modified: 2023-01-31T10:30:36.000+01:00

---

### Date: 31 Jan 2023

### Participants: Easwar, Praveen, Yanqiang, Prabu, Kefeng, Carven

### Meeting Minutes:

### Action Items:

1. Dependencies with CART - Easwaran Mahalingam Devaraj (MS/ECT-XC)
2. Integration of external WDG for next sample Easwaran Mahalingam Devaraj (MS/ECT-XC plan accordingly
3. HSI delivery plan
4. TSR draft version - Priority 1
5. Aurix - Safety Mechanism Status - XC-CI China - Docupedia (bosch.com) - Easwaran Mahalingam Devaraj (MS/ECT-XC) to update
6. Follow up with CART - SCC Safe Startup - XC-CT China - Docupedia (bosch.com) - Easwaran Mahalingam Devaraj (MS/ECT-XC)
7. SSR1a is on end of Feb - Priority 2
8. E2E not protected signal
9. Watchdog monitoring
10. Safe State Handling - SM20 Safe State Handling - XC-CT China - Docupedia (bosch.com) SSH can handle SS10 - still in discussion on how to handle Safety Shutdown path How to handle this SS10 - whether via SSH
11. Safe Error Memory - We dont need as an seperate SM. Now it is a part of SSH Jayaraj Praveen (BCSC-EPA4) to check with System team
12. Program flow monitoring - no need of an new Sm, Can we combine with SM7 Jayaraj Praveen (BCSC-EPA4) to check with System team
13. Safe ADC

### Date: 17 Jan 2023

### Participants: Easwar, Praveen, Yanqiang, Kefeng

### Meeting Minutes:

Safe State Handling - SM20 Safe State Handling - XC-CT China - Docupedia (bosch.com)

SSH can handle SS10 - still in discussion on how to handle Safety Shutdown path

How to handle this SS10 - whether via SSH

Voltage Monitoring - SM10 Voltage Monitoring - XC-CT China - Docupedia (bosch.com)

Wdg Handling - SM7 SCC Watchdog - XC-CT China - Docupedia (bosch.com)

### Action Items:

1. Links to TSR from SWRS , new attribute shall be created user-14275 COMPLETED
2. Dependencies with CART - user-14275
3. Integration of external WDG for next sample Easwaran Mahalingam Devaraj (MS/ECT-XC plan accordingly
4. HSI delivery plan - WANG Wei (XC/ESS3-CN)
5. TSR draft version - Priority 1
6. Aurix - Safety Mechanism Status - XC-CI China - Docupedia (bosch.com) - user-14275 to update
7. Follow up with CART - SCC Safe Startup - XC-CT China - Docupedia (bosch.com) - user-14275
8. SSR1a is on end of Feb - Priority 2
9. E2E not protected signal
10. Voltage monitoring
11. Watchdog monitoring
12. Safe State Handling - SM20 Safe State Handling - XC-CT China - Docupedia (bosch.com) SSH can handle SS10 - still in discussion on how to handle Safety Shutdown path How to handle this SS10 - whether via SSH
13. Safe Error Memory - We dont need as an seperate SM. Now it is a part of SSH Jayaraj Praveen (BCSC/ENG1) to check with System team
14. Program flow monitoring - no need of an new Sm, Can we combine with SM7 Jayaraj Praveen (BCSC/ENG1) to check with System team
15. Safe DLT will be from CART and ECT is responsible.

### Date: 10 Jan 2023

### Participants: Easwar, Praveen, Prabu , Yanqiang, Weiwei

### Meeting Minutes:

Discussion on Safe States and Reset Handling

SM20 Safe State Handling - XC-CT China - Docupedia (bosch.com)

https://sites.inside-share3.bosch.com/sites/167912/_layouts/15/VisioWebAccess/VisioWebAccess.aspx?id=|0&DocId=%7BEFB0675E-5DB7-409E-8D71-46F55DE8466F%7D&file=Zeekr 8295 Safety Path.vsdx

- SM52 and SSH on clearing SS10 and moving back to normal state
- Jayaraj Praveen (BCSC/ENG1) will finalize whether we have this Safe State within next week

SM14 SoC state monitor

- Taken by the China project team

### Action Items:

1. Links to TSR from SWRS , new attribute shall be created user-14275 INPROGRESS
2. Dependencies with CART - user-14275
3. Integration of external WDG for next sample Easwaran Mahalingam Devaraj (MS/ECT-XC plan accordingly
4. HSI delivery plan - WANG Wei (XC/ESS3-CN)
5. TSR draft version - Priority 1
6. Aurix - Safety Mechanism Status - XC-CI China - Docupedia (bosch.com) - user-14275 to update
7. Follow up with CART - SCC Safe Startup - XC-CT China - Docupedia (bosch.com) - user-14275
8. SSR1a is on end of Feb - Priority 2
9. Smoke Test
10. E2E not protected signal

### Date: 03 Jan 2023

### Participants: Easwar, Praveen, Carven, Yanqiang, Weiwei

### Meeting Minutes:

Discussion on Safe Config and SoC State monitor

#### SoC State Monitor

- We can take SM52 completely from Geely (including SoC State monitor)
- Safe Touch may also need SoC State Monitor
- External Temperature monitoring
- If they are reusing, decision is we will keep within SM52, if needed we can redesign
- @Zhao Yanqiang, reuse complete SM52

#### Safe Config

- CART mentioned nothing yet
- We will do on our own

### Action Items:

1. Links to TSR from SWRS , new attribute shall be created user-14275
2. Car Config structure to be updated in FSHLR  - ZHAO Yanqiang (XC-CP/ESW2-CN)
3. Dependencies with CART - user-14275
4. Review of System requirements for SW telltale and Safe output signals - user-14275 COMPLEDTED
5. Integration of external WDG for next sample Easwaran Mahalingam Devaraj (MS/ECT-XC plan accordingly
6. HSI delivery plan - WANG Wei (XC/ESS3-CN)
7. TSR draft version - Priority 1
8. Aurix - Safety Mechanism Status - XC-CI China - Docupedia (bosch.com) - user-14275 to update
9. Follow up with CART - SCC Safe Startup - XC-CT China - Docupedia (bosch.com) - user-14275
10. Tool classification
11. SSR1a is on end of Feb - Priority 2
12. Smoke Test
