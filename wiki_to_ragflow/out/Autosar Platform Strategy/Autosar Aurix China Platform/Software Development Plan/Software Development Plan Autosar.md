# Software Development Plan Autosar

> Source: /spaces/CARSFW/pages/2378223433/Software+Development+Plan+Autosar
> Last modified: 2023-01-05T01:56:05.000+01:00

---

Resources:

| Group | Developers for PI22.3 | Developers for PI23.1 |
| --- | --- | --- |
| Autosar | 5 | 4 |
| Multi Core | 2 | 3 |
| Audio | 2 | 2 |

Basic components from ECT:

| Feature Description | Priority | PI22.3 Status 25 Nov 2022 End Date | PI23.1 28 Nov 2022 to 27 Jan 2023 |
| --- | --- | --- | --- |
| Common DLT logging Usage of verbose and non-verbose Trc or xml file for parsing | Prio - 1 | Check on Monday. |  |
| FEL + Error Memory implementation Based on the Analysis from Architecture team regarding FEL/Error Memory conclusion | Prio - 1 | EM integration is done. | Start following activity in PI23.1. |
| UTF/XTM for China Convergence PF modules | Prio - 1 | Not start. | Will start in PI23.1. Need framework available for first sprint. |
| Audio modules - PF concept and implementation | Prio - 2 | Not start | Will start in PI23.1. |
| RTC driver | Prio - 1 | Integrated in cnconvbase and Zeekr. Not test in Zeekr. | Test in Zeekr board. |
| KDS_Zeekr | Prio - 1 | Not start | Available in VCU. We only have two KDS in cnconvbase project, much easier than VCU. |
| Variant Handler in Zeekr | Prio - 2 | Not start | Variant handler is based on Board Id. Consider make it common for all projects. |
| Boot time framework | Prio - 2 | Not start | Concept should be ready. |
| Third party library delivery as platform | Prio - 2 | Not start | Need to complete. |
| How To WIKI for all the modules. | Prio - 1 |  | With development activity together. |
| RTC driver as PF Module | Prio - 3 |  |  |
| Generic Boot manager | Prio - 3 |  |  |
| CAN and LIN bring up in CN Conv PF Based on Zeekr DBC | Prio - 3 |  |  |
| FR bring up in CN Conv PF - prio - 3 Based on Zeekr dbc | Prio - 3 |  |  |
| OTA - Swap A/B  - prio - 3 Future topic for download option | Prio - 3 |  |  |

Safety components:

| Feature Description | Priority |
| --- | --- |
| All the SM should be available in CN Conv repos before end of this year - Prio -1 Zeekr need Functional safety at March release | Prio - 1 |

Notes:

Prio -1  - means needed for Zeekr (Needed before end of this year)

Prio -2 - means may be needed for zeekr in Next year

Prio - 3 - is not for Zeekr it is for future projects
