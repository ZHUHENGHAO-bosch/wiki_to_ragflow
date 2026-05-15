# 06_Autosar - BSW Split Architecture

> Source: /spaces/CARSFW/pages/2396094469/06_Autosar+-+BSW+Split+Architecture
> Last modified: 2022-09-20T07:03:59.000+02:00

---

## Overview

BSW functional clusters are groups of functionally coherent BSW modules

Types of Clusters

- Communication Clusters
- Memory Cluster
- I/O Cluster
- Watchdog Cluster

## Guidelines for BSW Clusters

The same functional cluster can only exist at most once per BSW partition.

The communication and synchronization between modules in BSW functional clusters of the same type is not standardized

It will be implemented by communication between entities (e.g. by a master and satellites) of specific modules, which can use non-standardized interfaces for communication across BSW partition boundaries

BSW Split requires

- Thorough analysis of the considered modules
- Deep knowledge of BSW stack and its internal interactions and sequences

Vector Microsar provides

- Pre defined set of modules for relocation
- Additional functionality to support relocation

Below module have satellite implementation from Vector

- WdgM and WdgIf
- Dem
- EcuM
- Det

Below module have Proxy implementation from Vector

- Com
- NvM

## Communication Cluster

Relocation of individual channel is not possible in communication cluster

Example of communication cluster, Where all Ethernet related Stack can be mapped to Core1, like TCP/IP, SoAd, EthSM, Switch driver

![](../../../_images/06_Autosar%20-%20BSW%20Split%20Architecture/image2022-8-19_13-42-39.png)

COM stack uses proxy implementation to handle signals from other core

![](../../../_images/06_Autosar%20-%20BSW%20Split%20Architecture/image2022-8-19_13-51-45.png)

PduR acts as a router between cores for

- Interface PDUs
- Transport protocol PDUs

![](../../../_images/06_Autosar%20-%20BSW%20Split%20Architecture/image2022-8-19_14-3-58.png)

## Watchdog Cluster

There are 2 different concepts on how the WdgM Stack can react to detected violations, the independent and combined core reaction concept

### Independent Core reaction

![](../../../_images/06_Autosar%20-%20BSW%20Split%20Architecture/image2022-8-19_13-47-47.png)

### Combined core reaction

![](../../../_images/06_Autosar%20-%20BSW%20Split%20Architecture/image2022-8-19_13-48-49.png)

## Memory Cluster

Vector supports Nvm-Proxy component to support multicore NVM handling
