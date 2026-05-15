# 13_sync vcu udrop40 issue and cvm test

> Source: /spaces/CARSFW/pages/3139348652/13_sync+vcu+udrop40+issue+and+cvm+test
> Last modified: 2024-11-15T10:07:58.000+01:00

---

| Version | Detail | Date | Author | comment |
| --- | --- | --- | --- | --- |
| V0.1 | first version | 2023.07.07 | LIU Dezhi (XC-CP/ESW2-CN) |  |

Local projects shared and synced  the method of clear counters when underVoltage, to avoid jumping into bootloader. 06_Jump to bootloader mistakenly due to Abnormal Ubat Voltage

Now, GM VCU project have another two changes about underVoltage  reset handling

- optimized Self Test CVM process
- reset immediately when detected Udrop40 in  mcu initialize state

More details, please refer the PPT shared by JIN John (XC-CP/ESW2-CN)

[ VCU]VIP_Only_Reset+UnderVoltage_Reset_Handling.pptx

### Fix Status

|   |   |   |
| --- | --- | --- |
| GEELY | COMPLETED | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch_mcal/+/621383 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/635479 |
