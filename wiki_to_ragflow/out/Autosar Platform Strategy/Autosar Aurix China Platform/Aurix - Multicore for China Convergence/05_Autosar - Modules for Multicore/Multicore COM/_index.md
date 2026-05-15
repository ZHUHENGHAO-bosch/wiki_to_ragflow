# Multicore COM

> Source: /spaces/CARSFW/pages/2754792481/Multicore+COM
> Last modified: 2023-12-01T02:45:45.000+01:00

---

In order to provide a load distribution amongst different partitions (cores),

the main threads of execution in the COM module, namely the respective MainFunctions are assigned to different partitions.

The general concept for the multipartition support of the COM is, that the ComIPdus are processed in the MainFunction which is referenced via the ComIPduMainFunctionRef.

The Main Functions are assigned to a partition via the ComMainTx/Rx/RouteSignalsPartitionRef. Additionally, the ComIPdus are assigned to a partition via the “global” Pdu which defined in EcuC.

Zeekr need implement multicore COM on core0 and core1. All the flexRay PDUs should be process on core1, for CAN and Lin Pdus should be process on core0.

![](../../../../../_images/Multicore%20COM/Multicore%20COM%20stack.png)

Initialization and Deinitialization

The COM shares all RAM between partitions, due to that the Com_Init() and Com_DeInit() functions must only be called once to initialize/deinitialize the COM variables.

Zeekr call Com_Init() on core0.

#### Com main function configuration

Create main functions and assign to EcucPartition_QM_Core0 and EcucPartition_QM_Core1.

Assign them to BSWTask_5ms_Core0 and BSWTask_5ms_Core1 in OS.

![](../../../../../_images/Multicore%20COM/image2023-2-28_10-30-38.png)

#### Com Ipdu configuration

FlexRay ComIPdus should reference ComMainFunctionTx_Core1 and ComMainFunctionRx_Core1.

CAN Lin ComIPdus should reference ComMainFunctionTx_Core0 and ComMainFunctionRx_Core0.

![](../../../../../_images/Multicore%20COM/image2023-2-28_10-49-13.png)

![](../../../../../_images/Multicore%20COM/image2023-2-28_10-46-17.png)

#### ECUC need assign global PDU to different partition

Global pdu should assign to EcucPartition_QM_Core0 and EcucPartition_QM_Core1.

#### 

#### Step4

Signal Routings and Description Routings are only supported “partition local”. This can't match the customer requirement.

I deleted GW mapping locally.

![](../../../../../_images/Multicore%20COM/image2023-2-28_11-52-4.png)

#### PDUR configuration.

![](../../../../../_images/Multicore%20COM/image2023-3-13_14-21-10.png)

PDUR shared ram should be assigned in MemMap module.

![](../../../../../_images/Multicore%20COM/image2023-3-1_10-22-17.png)

![](../../../../../_images/Multicore%20COM/image2023-3-1_15-46-42.png)

![](../../../../../_images/Multicore%20COM/image2023-3-1_15-15-18.png)

.OS_OsApplication_QM_Core1_VAR_NOINIT needed, but no define in ld file.

#### Rte configuration

Set RteOptimizationMode from MEMORY to RUNTIME.

![](../../../../../_images/Multicore%20COM/image2023-2-28_12-10-45.png)

#### Step7

The ports between Com and Rte need to check.

| SWC | port prototype | data element |
| --- | --- | --- |
| SWC_DiagserviceHdlr | RP_VehModMngtGlbSafe1 | VehModMngtGlbSafe1 |
| SWC_BusE2ESignalHandler | SWC_BusE2ESignalHandler_SPort_DeactiveTJPReq | DeactiveTJPReq |
| SWC_BusE2ESignalHandler | SWC_BusE2ESignalHandler_SPort_SftySigGroupFromHmiSafe1 | SftySigGroupFromHmiSafe1 |

![](../../../../../_images/Multicore%20COM/image2023-2-28_12-26-52.png)

![](../../../../../_images/Multicore%20COM/image2023-3-15_18-5-41.png)
