# SM14 SCC Self Test

> Source: /spaces/CARSFW/pages/2699330911/SM14+SCC+Self+Test
> Last modified: 2023-03-20T12:37:38.000+01:00

---

This SM is responsible to execute Self tests recommeneded by Aurix Safety manual

The self-test shall be executed in the below order as part of the safety startup.

- PBIST (executed by AURIX)
- LBIST - LBIST - XC-CT China - Docupedia (bosch.com)
- MONBIST - MONBIST - XC-CT China - Docupedia (bosch.com)
- MCU Check (MCU_START) - MCU_STARTUP - XC-CT China - Docupedia (bosch.com)
- FW Check - FW_Check - XC-CT China - Docupedia (bosch.com)
- SMU Alive Alarm test - SMU: REG_MONITOR_TEST - XC-CT China - Docupedia (bosch.com)
- Register Monitor Test - REG_MONITOR_TEST - XC-CT China - Docupedia (bosch.com)
- MBIST - MBIST - XC-CT China - Docupedia (bosch.com)
- FSP Control Self-Test - FSP_SELFTST - XC-CT China - Docupedia (bosch.com)
- CONVCTRL: PHASE_SYNC_ERR Self-Test - PHASE_SYNC_ERR - XC-CT China - Docupedia (bosch.com)

### Sample Self test sequence

![](../../../../../_images/SM14%20SCC%20Self%20Test/image2023-1-29_11-7-26.png)

> **INFO: AUSS**
> AUSS: Aurix Safety Startup

![](../../../../../_images/SM14%20SCC%20Self%20Test/SM14%20SCC%20Self%20Test.bmp)
