# Multicore Mode Handling

> Source: /spaces/CARSFW/pages/2917667492/Multicore+Mode+Handling
> Last modified: 2023-04-04T13:09:42.000+02:00

---

### Introduction

We need to have Multicore mode handling in slave cores as well, so that respective CDDs/Services in slave core can Init their modules based on EcuM modes

#### Solution 1: Mode Handling with BswM running only in Master Core

We will have BswM running in Master core and Service.EcuModeManager will have Master-Satellite approach

![](../../../../../_images/Multicore%20Mode%20Handling/UC6_ModeHandlingInSlaveCores_WithBswMonMastreCore.bmp)

- Vector recommended not to use BswM in Multi core aspect due to performance issue.

##### Solution 2: Mode Handling with Multi core BswM

We will have BswM running in all cores and mode sync will happen between BswM partition itself

![](../../../../../_images/Multicore%20Mode%20Handling/UC6_ModeHandlingInSlaveCores_WithBswMMultiPartition.bmp)

#### Decision

latest Vector SIP (from R28) BswM has an improved performance for Multicore handling. Hence we will go with Solution 2: Mode Handling with Multi core BswM since it is best Autosar way of handling modes

### Reference links:

Mode Synchronization across Cores - XC-CT Cerberus Platform - Docupedia (bosch.com)
