# VCU Plus - Optimization

> Source: /spaces/CARSFW/pages/5446836110/VCU+Plus+-+Optimization
> Last modified: 2025-02-28T09:46:00.000+01:00

---

## Overview

This page is to analyze the following topics and come up with data and optimization steps

- OS load
- Memory consumption
- Boot time

### List of tasks in Core 0 and Core 1 (High level)

how many tasks and Isrs

| Core 0 Tasks | Runnable | Risk | Description | To Do |  |
| --- | --- | --- | --- | --- | --- |
| BswTask_ASIL_10ms_Core0 | WdgM_MainFunction ClockMonitor_10ms AdcC_MainFunction TempSensor_Aurix_Main PflashCrcChecker_MainFunction SafeTelltale_SWC_Runnable | No | Safety tasks | NA |  |
| BSWTask_10ms_Core0 | Dcm_MainFunction Dlt_MainFunction Fee_MainFunction BswM_MainFunction_OsApplication_QM_Core0 Fls_17_Dmu_MainFunction NvM_MainFunction DltIf_UartMainFunctionRx CDD_ErrorMemory_ErrorMemory_MainFunction_Wrapper RTCHandler_MainFunction EcuM_MainFunction AudioAmpDriver_mainFunction DLT_Runnable_10ms FatalErrorLogger_MainFunction AudioAmpHandler_mainFunction SEH_Main WdgMTaskSupervision_BswTask_10ms_Core0 CanNm_MainFunction LinIf_MainFunction_CHNL_45618847 LinSM_MainFunction CanTrcv_30_Tja1040_MainFunction CanTrcv_30_Tja1145_MainFunction LinIf_MainFunction_CHNL_8e3d5be2 EcuInternalAwakeHandler_DBGWakeUpRunnable SMAV_Runnable PowerMode_Run PduR_MainFunction | Yes | Takes ~20% of load without CAN connected |  |  |
| AplTask_5ms_Core0 | WdgMTaskSupervision_AplTask_5ms_Core0 RtcExtRA8804CEDriver_Main Dlt_TSync_Toggle_Retry IVI_RxMsg_Runnable | No |  |  |  |
| ECUM_InitTask_Core0 | Init task | No |  |  |  |
| TCI_AppTask3 |  |  |  |  |  |
| AplTask_10ms_Core0 |  |  |  |  |  |
| AplTask_ASIL_Core0 |  |  |  |  |  |
| AplTask_EcuModeChange |  |  |  |  |  |
| BSW_PowerM |  |  |  |  |  |
| BswTask_Core0 |  |  |  |  |  |
| ECUM_ShutdownTask_Core0 |  |  |  |  |  |
| RTMO_BG_TASK |  |  |  |  |  |
| IdleTask_OsCore0 |  |  |  |  |  |
| BSW_SystemM |  |  |  |  |  |
| Inc_Rx_Process_Core0 |  |  |  |  |  |
| BSW_ThermalMonitor |  |  |  |  |  |
| UTM_Task |  |  |  |  |  |
| ECUM_InitTask_Core0_ASIL |  |  |  |  |  |
| TCI_AppTask6 |  |  |  |  |  |
| AplTask_Core0 |  |  |  |  |  |
| AplTask_20ms_Core0 |  |  |  |  |  |
| Apl_InitTask_core0 |  |  |  |  |  |
| BSWTask_5ms_Core0 |  |  |  |  |  |
| BSWTask_20ms_Core0 |  |  |  |  |  |
| TCI_AppTask1 |  |  |  |  |  |
| TCI_AppTask4 |  |  |  |  |  |
| TCI_AppTask5 |  |  |  |  |  |
| Apl_ASIL_InitTask_core0 |  |  |  |  |  |
| Appl_InitTask_ASIL |  |  |  |  |  |
| BSWTask_10ms_Core0_Com |  |  |  |  |  |
| BswTask_ASIL_Core0 |  |  |  |  |  |
| TCI_AppTask2 |  |  |  |  |  |
| BSWTask_Core1 |  |  |  |  |  |
| TCI_AppTask7 |  |  |  |  |  |
| TCI_AppTask8 |  |  |  |  |  |
| TCI_AppTask10 |  |  |  |  |  |
| TCI_AppTask11 |  |  |  |  |  |
| TCI_AppTask12 |  |  |  |  |  |
| TCI_AppTask13 |  |  |  |  |  |
| TCI_AppTask14 |  |  |  |  |  |
| TCI_AppTask15 |  |  |  |  |  |
| TCI_AppTask16 |  |  |  |  |  |
| TCI_AppTask17 |  |  |  |  |  |
| TCI_AppTask18 |  |  |  |  |  |
| AplTask |  |  |  |  |  |
| TCI_SumTask5 |  |  |  |  |  |
| TCI_SumTask6 |  |  |  |  |  |
| TCI_SumTask7 |  |  |  |  |  |
| TCI_SumTask8 |  |  |  |  |  |
| TCI_SumTask9 |  |  |  |  |  |
| TCI_SumTask10 |  |  |  |  |  |
| TCI_SumTask11 |  |  |  |  |  |
| GM_ASIL_Task |  |  |  |  |  |
| UaesTask_10ms_Core1 |  |  |  |  |  |
|  |  |  |  |  |  |

| Core 1 | Task | Runnable | Description | To Do |
| --- | --- | --- | --- | --- |
| BswTask_ASIL_10ms_Core0 |  |  |  |  |
| IdleTask_OsCore1 |  |  |  |  |
| ECUM_InitTask_Core1 |  |  |  |  |
| RTMO_BG_TASK1 |  |  |  |  |
| Inc_Rx_Process_Core1 |  |  |  |  |
| ECUM_InitTask_Core1_ASIL |  |  |  |  |
| Apl_InitTask_core1 |  |  |  |  |
| AplTask_10ms_Core1 |  |  |  |  |

| Core 2 | Task | Runnable | Description | To Do |
| --- | --- | --- | --- | --- |
| BSWTask_10ms_Core2 |  |  |  |  |
| IdleTask_OsCore2 |  |  |  |  |
| AplTask_10ms_Core2 |  |  |  |  |
| ECUM_InitTask_Core2 |  |  |  |  |
| RTMO_BG_TASK2 |  |  |  |  |
| Inc_5ms_Core2 |  |  |  |  |
| Inc_9ms_Core2 |  |  |  |  |
| ECUM_InitTask_Core2_ASIL |  |  |  |  |
| BSWTask_Core2 |  |  |  |  |
| Apl_InitTask_core2 |  |  |  |  |
| BswTask_ASIL_10ms_Core2 |  |  |  |  |
|  |  |  |  |  |

Can channels and Ethernet channels

Current Ram allocation of each core

#### General information:

IFX: 2.3 DMIPS/MHZ

One Core DMIPs is 690 DMIPS

TC39x total DMIPs is : 2700 DMIPS in ASIL-D and 1300 DMIPS in ASIL-B

### Issues:

- Cannot measure RTMO. Scripts has issues. Fixed in local for now. Need to deliver
- But still have issues in System load values

| I.No | Issue description | Owner | Status |
| --- | --- | --- | --- |
| 1 | RTMO script doesn't work in Vcuplus. The path is not updated properly during integration In local changed the path. Will clean and deliver today | Jayaraj Praveen (BCSC/ENG1) | INPROGRESS |
| 2 | FEL is called in Core 3, Core 4 and Core 5 frequently due to Systemtimer is not configured for Core 3-5 This is making FEL main function in Core 0 to wait for spinlock and the FEL task spins for too long time ![](../../../_images/VCU%20Plus%20-%20Optimization/image-2025-2-28_13-17-16.png) |  |  |
| 3 | FEL is called frequently in Core 0 from Det report error due to CanTrcv_30_Tja1040_SetOpMode API ![](../../../_images/VCU%20Plus%20-%20Optimization/image-2025-2-28_13-18-22.png) |  |  |
| 4 | System load in RTMO is not correct giving wrong values ![](../../../_images/VCU%20Plus%20-%20Optimization/image-2025-2-28_13-19-28.png) |  |  |

### Current OS load:
