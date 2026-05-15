# Aurix - China Convergence - OS Guidelines

> Source: /spaces/CARSFW/pages/3011088330/Aurix+-+China+Convergence+-+OS+Guidelines
> Last modified: 2023-05-15T13:57:11.000+02:00

---

#### General Guidelines

- Please map your cyclic runnable to proper Tasks as explained in below table
- It is always not needed to map your runnable to 5 or 10ms. Please check whether the runnable has to schedule every 10ms if not please move to other higher period runnable like 20 or 50ms runnable. (Module owners will take care of this point).
- When you map new runnable make sure the RTMO report is taken to check the maximum stack usage of the task that the runnable is mapped. If task usage is >75%, Please increase the stack size
- For accessing Safety APIs, don't create the trusted function directly in OS. Use Context Switcher module  - Context Switcher - How To Configure - XC-CT China - Docupedia (bosch.com)
- If the code logic is very complex and has less interaction with other modules → Try to move it to slave cores

### Core 0 (Master Core)

BSW → All MCAL, CDD and BSW Modules

Apl → All services layer and application modules

| Task | Priority | Type | Schedule | Comments |
| --- | --- | --- | --- | --- |
| QM Tasks |  |  |  |  |
| AplTask_5ms_Core0 | 52 | Basic | NON | Application 5ms Cyclic Runnable |
| AplTask_10ms_Core0 | 51 | Basic | NON | Application 10ms Cyclic Runnable |
| AplTask_20ms_Core0 | 50 | Basic | NON | Application 20ms Cyclic Runnable |
| AplTask_Core0 | 49 | Extended | NON | Other Application  Cyclic Runnable and Event based Runnable WdgM will monitor this low Priority task |
| ClusterApp_10ms_Core0 | 51 | Extended | NON | Third Party Runnable. Dont change the logic. It can have event based runnables |
| BSWTask_5ms_Core0 | 201 | Basic | NON | BSW 5ms Cyclic Runnable |
| BSWTask_10ms_Core0_Com | 201 | Basic | NON | BSW Com Stack 10ms runnable this is for Chery. For Zeekr → No need to create this task. For Zeekr in Flexray, no need to do any modifications as part of OS Cleanup Jayaraj Praveen (BCSC/ENG1) FYI & NA |
| BSWTask_10ms_Core0 | 200 | Basic | NON | BSW 10ms Cyclic Runnable |
| BSWTask_20ms_Core0 | 199 | Basic | NON | BSW 20ms Cyclic Runnable |
| BswTask_Core0 | 200 | Extended | NON | Other Application Cyclic Runnable and Event based Runnable |
| QM Init Tasks |  |  |  |  |
| Apl_InitTask_core0 | 490 | Basic | NON | All QM Init Runnable |
| ClusterApp_InitTask_Core0 | 150 | Basic | NON | Third Party Application Init runnable |
| ASIL Tasks |  |  |  |  |
| BswTask_ASIL_10ms_Core0 | 480 | Basic | NON | BSW ASIL 10ms Cyclic Runnable - High priority Task After Init Task - Due to WdgM |
| AplTask_ASIL_10ms_Core0 | 150 | Basic | NON | Safe ASIL Application 10ms Cyclic Runnable Extended since WdgM Check point event has to be mapped. |
| BswTask_ASIL_Core0 | 201 | Extended | NON | Other BSW ASIL cyclic and Event based Runnable |
| AplTask_ASIL_Core0 | 150 | Extended | NON | Other Safe ASIL Application cyclic and Event based Runnable |
| ASIL Init Tasks |  |  |  |  |
| Apl_InitTask_ASIL | 498 | AutoStart | NON | Init task for all ASIL Init APIs → It is not OS created task. It is a manual implemented task (AutoStart) |

### Core 1 (Slave Core)

Only for QM Modules

| Task | Priority | Type | Schedule | Comments |
| --- | --- | --- | --- | --- |
| QM Tasks |  |  |  |  |
| AplTask_5ms_Core1 | 52 | Basic | NON | Application 5ms Cyclic Runnable |
| AplTask_10ms_Core1 | 51 | Basic | NON | Application 10ms Cyclic Runnable |
| AplTask_Core1 | 49 | Extended | NON | All other application cyclic runnable and Event based runnable WdgM will monitor this low Priority task |
| BSWTask_5ms_Core1 | 201 | Basic | NON | BSW 5ms Cyclic Runnable |
| BSWTask_10ms_Core1 | 200 | Basic | NON | BSW 10ms Cyclic Runnable |
| BSWTask_Core1 | 200 | Extended | NON | All other application cyclic runnable and Event based runnable |
| QM Init Tasks |  |  |  |  |
| Apl_InitTask_core1 | 490 | Basic | NON | Init task for all Application in Core 1 |
| ASIL Task |  |  |  |  |
| BswTask_ASIL_10ms_Core1 | 480 | Basic | NON | For WdgM runnable |

### Core 2 (Slave Core)

Only for QM Modules

| Task | Priority | Type | Schedule | Comments |
| --- | --- | --- | --- | --- |
| QM Tasks |  |  |  |  |
| AplTask_5ms_Core2 | 51 | Basic | NON | Application 5ms Cyclic Runnable |
| AplTask_10ms_Core2 | 50 | Basic | NON | Application 10ms Cyclic Runnable |
| AplTask_Core2 | 49 | Extended | NON | All other application cyclic runnable and Event based runnable WdgM will monitor this low Priority task |
| BSWTask_5ms_Core2 | 201 | Basic | NON | BSW 5ms Cyclic Runnable |
| BSWTask_10ms_Core2 | 200 | Basic | NON | BSW 10ms Cyclic Runnable |
| BSWTask_Core2 | 200 | Extended | NON | All other application cyclic runnable and Event based runnable |
| QM Init Tasks |  |  |  |  |
| Apl_InitTask_core2 | 490 | Basic | NON | Init task for all Application in Core 2 |
| ASIL Task |  |  |  |  |
| BswTask_ASIL_10ms_Core2 | 480 | Basic | NON | For WdgM runnable |

### Other Tasks - Only for reference

| Task | Priority | Type | Schedule | Comments |
| --- | --- | --- | --- | --- |
| EcuM Init Tasks |  |  |  |  |
| ECUM_InitTask_Core0 | 500 | AutoStart | NON | EcuM Init task - Multicore Sync using Barriers |
| ECUM_InitTask_Core0_ASIL | 499 | AutoStart | NON | EcuM Init ASIl task  - To enable ASIL OS ISRs in Core 0 |
| ECUM_InitTask_Core1 | 500 | AutoStart | NON | EcuM Init task - Multicore Sync using Barriers |
| ECUM_InitTask_Core1_ASIL | 499 | AutoStart | NON | EcuM Init ASIl task  - To enable ASIL OS ISRs in Core 1 |
| ECUM_InitTask_Core2 | 500 | AutoStart | NON | EcuM Init task - Multicore Sync using Barriers |
| ECUM_InitTask_Core2_ASIL | 499 | AutoStart | NON | EcuM Init ASIl task  - To enable ASIL OS ISRs in Core 2 |
| INC Tasks |  |  |  |  |
| Inc_Rx_Process_Core0 | 201 | AutoStart | FULL | INC Rx notification in Core 0 |
| Inc_Rx_Process_Core1 | 201 | AutoStart | FULL | INC Rx notification in Core 1 |
| Inc_5ms_Core2 | 160 | Basic | FULL | SPI0 INC message processing |
| Inc_9ms_Core2 | 150 | Basic | FULL | SPI1 INC Message Processing |
| Background Tasks |  |  |  |  |
| RTMO_BG_TASK | 0 | AutoStart | FULL | For Real time measurements |
| RTMO_BG_TASK1 | 0 | AutoStart | FULL | For Real time measurements |
| RTMO_BG_TASK2 | 0 | AutoStart | FULL | For Real time measurements |
| IdleTask | 0xFFFFFFFF | AUTO | FULL | Needed by Vector System application |
| IdleTask_OsCore1 | 0xFFFFFFFF | AUTO | FULL | Needed by Vector System application |
| IdleTask_OsCore2 | 0xFFFFFFFF | AUTO | FULL | Needed by Vector System application |
| UTF Tasks |  |  |  |  |
| UTM Task | 100 | Basic | NON | This Task will be activated only in UTF binary |

For Zeekr:

| Task | Priority | Type | Schedule | Comments |
| --- | --- | --- | --- | --- |
| Tasks |  |  |  |  |
| Bsw_FlexRay_5msTask | 490 | Basic | FULL | Can we delete it? Jayaraj Praveen (BCSC/ENG1) No, this is the actual FR task. Dont change please |
| Bsw_FlexRay_5msTask_Dummy | 10 | Basic | FULL | Can we rename to _5ms task Jayaraj Praveen (BCSC/ENG1) This is the dummy task to make Vector build pass |
|  |  |  |  |  |
