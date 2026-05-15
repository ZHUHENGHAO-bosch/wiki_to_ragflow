# Safety Meeting Minutes - 09-2022

> Source: /spaces/CARSFW/pages/2403660605/Safety+Meeting+Minutes+-+09-2022
> Last modified: 2022-09-27T08:08:53.000+02:00

---

### Date: 30 Aug 2022

### Participants: Easwar, Carven, Newton, Praveen, Senthil

### Meeting Minutes:

1. Discussed the Safety Mechanism needed for Zeekr - Aurix - Safety Mechanism Status - XC-CI China - Docupedia (bosch.com)

### Open points:

- Project will not maintain any documents for Safety mechanisms from CART/PF in Project Doors

### Action Items:

1. Discussion with CART to update the timeline - user-14275
2. Overview on next PI goals - user-14275
3. External WDG chip finalization  - user-1f19a OPEN
4. All external circuit details for Safety - user-1f19a INPROGRESS
5. Process - follow up with CART user-14275
6. Finalization on DLT and Error Memory user-1f19a
7. Update timeline details in Wiki user-1f19a COMPLETED - Zeekr Safety Timeline - GEN4 generic - Docupedia (bosch.com)

### Date: 07 Sep 2022

### Participants: Easwar, Praveen, Lakshmi, Wang Wei

### Meeting Minutes:

Discussed on

SM10 Voltage Monitoring - XC-CI China - Docupedia (bosch.com)

SM16 SCC Safe Temperature Monitoring - XC-CI China - Docupedia (bosch.com)

CART: We need SafeVoltageMonitor as an framework component and what to be monitored will be in configuration folder

PGOOD in QM Context → Need some analysis whether to be done in Safe Context

PGOOD comparator itself is QM HW complaint - so we don't need to monitor PGOOD

Get Daimler documents

### Action Items:

1. Discussion with CART to update the timeline - user-14275
2. Overview on next PI goals - user-14275
3. External WDG chip finalization  - user-1f19a OPEN
4. All external circuit details for Safety - user-1f19a INPROGRESS
5. Process - follow up with CART user-14275
6. Finalization on DLT and Error Memory user-1f19a
7. Get Power rail documents for Daimler - user-14275

### Date: 13 Sep 2022

### Participants: Easwar, Praveen

### Meeting Minutes:

Discussion on Safe State Handling

SM20 Safe State Handling - XC-CI China - Docupedia (bosch.com)

Safety Traceability - China Convergence Platform - XC-CI China - Docupedia (bosch.com)

### Action Items:

1. Discussion with CART to update the timeline - user-14275
2. Overview on next PI goals - user-14275
3. External WDG chip finalization  - user-1f19a OPEN
4. All external circuit details for Safety - user-1f19a INPROGRESS
5. Process - follow up with CART user-14275
6. Finalization on DLT and Error Memory user-1f19a
7. Get Power rail documents for Daimler - user-14275

### Date: 22 Sep 2022

### Participants: Easwar, Praveen, Wang Wei, Prabu, Senthil, Lakshmi

### Meeting Minutes:

Traceability will be taken care in another context

DLT and EM will be take care in Autosar area

Added a new SM - SM19 Safe ADC Calibration and Plausibility check - XC-CI China - Docupedia (bosch.com) - detailed discussion on next meeting

SM1 SCC RAM Monitoring - XC-CI China - Docupedia (bosch.com) - overview done - detailed discussion on next meeting

### Action Items:

1. Discussion with CART to update the timeline - user-14275
2. Overview on next PI goals - user-14275 - COMPLETED Attached the image below
3. External WDG chip finalization  - user-1f19a OPEN
4. All external circuit details for Safety - WANG Wei (XC/ESS3-CN) INPROGRESS
5. Process - follow up with CART user-14275
6. Finalization on DLT and Error Memory user-1f19a
7. Get Power rail documents for Daimler - user-14275 - COMPLETED
8. Draft version of safety path
9. Added the SM19 for ADC - user-14275 to check whether CART have this SM in their feature list

![](../../../../_images/Safety%20Meeting%20Minutes%20-%2009-2022/image2022-9-22_11-8-25.png)

### Date: 27 Sep 2022

### Participants: Easwar, Wang Wei, Praveen, Prabu

### Meeting Minutes:

Safe ADC is already planned by CART

Discussion on Safe path - SG1

SocStatemonitor - We need to analyze the CART mechanism with the one in GWM (BootModeSender)- Understand the dependencies

BootModeSender - Gives the status of SOC like Normal and Recovery mode, Pin for STR (Special mode)

GWM has two states

1. Normal (Inc message)
2. Recovery (Inc message)

Geely has three states

1. Normal (Inc message)
2. Recovery (Inc message)
3. STR (Pin)

### Action Items:

1. Discussion with CART to update the timeline - user-14275
2. External WDG chip finalization  - user-1f19a OPEN
3. All external circuit details for Safety - WANG Wei (XC/ESS3-CN) INPROGRESS - System team will give more input after system safety analysis
4. Draft version of safety path
5. Share the concept from CART on SOC State monitor - user-14275
6. ADC Handling on HW level -whether we will receive ADC in two different pins and processed by two ADC Convertors Or Get ADC in a single pin and processed redundantly by different ADC convertor (May be another group or another cluster) WANG Wei (XC/ESS3-CN)
