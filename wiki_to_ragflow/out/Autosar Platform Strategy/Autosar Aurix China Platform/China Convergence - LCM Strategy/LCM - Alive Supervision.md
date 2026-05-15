# LCM - Alive Supervision

> Source: /spaces/CARSFW/pages/3346629335/LCM+-+Alive+Supervision
> Last modified: 2023-08-15T05:14:51.000+02:00

---

### Overview

we have enabled supervision at each transitional mode in EcuM so that system will not stuck due to issues in triggers.

### Supervision Entity - Configuration

| Supervision Entity | Expected SP | Supervision Ref Cycle (10ms) | Max Margin | Min Margin | Failed Alive SP tolerance |
| --- | --- | --- | --- | --- | --- |
| EcuM_AliveSupervision_OnEnterWakeup | 1 | 3000 | 0 | 0 | 0 |
| EcuM_AliveSupervision_OnEnterStartup | 1 | 3000 | 0 | 0 | 0 |
| EcuM_AliveSupervision_OnEnterStartup | 1 | 3000 | 0 | 0 | 0 |
| EcuM_AliveSupervision_OnEnterSccRun* | 1 | 3000 | 0 | 0 | 0 |
| EcuM_AliveSupervision_OnEnterSocRun* | 1 | 3000 | 0 | 0 | 0 |
| EcuM_AliveSupervision_OnEnterPostrun | 1 | 10000 | 0 | 0 | 0 |
| EcuM_AliveSupervision_OnEnterShutdown | 1 | 3000 | 0 | 0 | 0 |

*SCCRUN and SCORUN are stable state so we are not enabling this SEs

### Error Handling

In case of any supervision enters Expired state we will do reset via FEL
