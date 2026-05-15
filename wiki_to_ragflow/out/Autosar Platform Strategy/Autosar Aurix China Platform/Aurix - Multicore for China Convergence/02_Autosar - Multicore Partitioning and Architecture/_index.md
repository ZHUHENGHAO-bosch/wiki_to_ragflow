# 02_Autosar - Multicore Partitioning and Architecture

> Source: /spaces/CARSFW/pages/2383057423/02_Autosar+-+Multicore+Partitioning+and+Architecture
> Last modified: 2022-08-18T15:59:48.000+02:00

---

## Overview

Below picture shows an overview of partitioning in Multi Core system

Master Core -> Will be started after Power ON and starts the Slave Core

BSW Core – Core on which BSW Stack executes

![](../../../../_images/02_Autosar%20-%20Multicore%20Partitioning%20and%20Architecture/image2022-8-9_9-41-0.png)

## Autosar Architecture for Multicore

- Each Core should have at least one partition
- RTE is shared across all the cores
- BSW can reside on multiple cores, but it has to be present in one partition in a single core

BSW Modules can

- Located only on one core
- Duplicated for Multiple core
- Using proxy to share services
- Using Master/Satellite approach

It will be easy to run BSW in one Core during Multi Core bring up. Afterwards BSW can be split based on requirements

## BSW Clusters

BSW functional clusters are groups of functionally coherent BSW modules

Types of Clusters

- Communication Clusters
- Memory Cluster
- I/O Cluster
- Watchdog Cluster

### BSW Clusters Guidelines

- The same functional cluster can only exist at most once per BSW partition
- The communication and synchronization between modules in BSW functional clusters of the same type is not standardized
- It will be implemented by communication between entities (e.g. by a master and satellites) of specific modules, which can use non-standardized interfaces for communication across BSW partition boundaries

![](../../../../_images/02_Autosar%20-%20Multicore%20Partitioning%20and%20Architecture/image2022-8-9_10-12-31.png)

### Inter-BSW Communication

Function calls to tasks that are supposed to be executed in a different BSW partition/on a different core cannot be implemented as simple C calls to this function, because these calls would be handled on the local BSW partition

The BSW Scheduler (SchM) therefore provides functions to invoke masters or satellites of the same module on different BSW partitions using either client-server or sender-receiver communication

The functionality is generally similar to that of function calls between SWCs and the BSW. However, because the RTE may not be available at certain points of time (especially during startup of an ECU), this functionality must be available within the BSW itself

- For CS - Synchronous,

Std_ReturnType SchM_Call_<bsnp>[_<vi>_<ai>]_<name>( [OUT <typeOfReturnValue> returnValue] [IN|IN/OUT\|OUT]<data_1> ... [IN|IN/OUT|OUT] <data_n>)

- For CS - Asynchronous, Callback shall be available like below

Std_ReturnType SchM_Result_<bsnp>[_<vi>_<ai>]_<name>( [IN|IN/OUT|OUT]<data_1> ... [IN|IN/OUT|OUT] <data_n>)

- For SR Communication - Write data to a sender-receiver link between BSW modules, possibly crossing partition boundaries Std_ReturnType SchM_Send_<bsnp>[_<vi>_<ai>]_<name>(IN <data>)
- For SR Communication - Read data from a sender-receiver link between BSW modules, possibly crossing partition boundaries Std_ReturnType SchM_Receive_<bsnp>[_<vi>_<ai>]_<name>(OUT <data>)

> **INFO**
> This Autosar requirement of Inter-BSW Communication is not supported by Vector SIP BSW-Scheduler queued S/R communication [API: SchM_Send, SchM_Receive] and BSW-Scheduler C/S communication [API: SchM_Call, SchM_Result]
