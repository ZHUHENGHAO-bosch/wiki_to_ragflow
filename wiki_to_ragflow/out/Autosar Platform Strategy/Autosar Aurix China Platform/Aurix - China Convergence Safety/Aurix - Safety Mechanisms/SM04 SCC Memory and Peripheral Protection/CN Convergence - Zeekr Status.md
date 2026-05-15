# CN Convergence - Zeekr Status

> Source: /spaces/CARSFW/pages/2940967737/CN+Convergence+-+Zeekr+Status
> Last modified: 2023-04-13T10:50:54.000+02:00

---

#### First Version Status:

Delivered Date: 13 Apr 2023

|   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- |
| Core | Application | Mode | Peripheral region access | Memory region access (RAM) | Memory region access (FLASH) |
| 0 | SystemApplication_OsCore0 | Supervisor Mode | For all region | For all region (MPU access) | For all region (MPU access) |
| OsApplication_ASIL_Core0 | Supervisor Mode | For all region | For all region (MPU access) | For all region (MPU access) |
| OsApplication_QM_Core0 | User Mode - 1 | Protected – Access grant via OS | No access to ASIL region | For all region (MPU access) |
| 1 | SystemApplication_OsCore1 | Supervisor Mode | For all region | For all region (MPU access) | For all region (MPU access) |
| OsApplication_ASIL_Core1 | Supervisor Mode | For all region | For all region (MPU access) | For all region (MPU access) |
| OsApplication_QM_Core1 | User Mode - 1 | Protected – Access grant via OS | No access to ASIL region | For all region (MPU access) |
| 2 | SystemApplication_OsCore2 | Supervisor Mode | For all region | For all region (MPU access) | For all region (MPU access) |
| OsApplication_QM_Core0 | User Mode - 1 | Protected – Access grant via OS | No access to ASIL region | For all region (MPU access) |
