# Guidelines for Configuring Spinlock

> Source: /spaces/CARSFW/pages/2384997422/Guidelines+for+Configuring+Spinlock
> Last modified: 2024-04-25T04:05:00.000+02:00

---

## Introduction

Synchronization of cores is done by OS Spinlocks

> **INFO: Spinlock Usage**
> Spinlock can be used only in CAT 2 ISR and Task context

## Guidelines for Configuring Spinlock

- Short name: Give a proper name as per the module using the spinlock
- Spinlock Lock Method:

As explained in Deadlock Use Case 1 - Preemptive Task in Same Core - XC-CT China - Docupedia (bosch.com) , there is a chance that deadlock may occur with Spinlock.

Thus, it is necessary to configure lock method for each spinlock

- LOCK_CAT2_INTERRUPTS LOCK_ALL_INTERRUPTS LOCK_NOTHING - Will result in deadlock LOCK_WITH_RES_SCHEDULER

To Keep simple and to avoid deadlock, it is recommended to configure with LOCK_ALL_INTERRUPTS

- Spinlock Lock Type:

As explained in Deadlock Use Case 2 - Nesting Spinlock - XC-CT China - Docupedia (bosch.com) , we need to be careful in selecting which spinlock is required for our concept.

- STANDARD - AUTOSAR OS Spinlock type OPTIMIZIED - Vector specific OS Feature

AUTOSAR specified OS spinlocks cannot cause any deadlocks between cores (see unique order of nesting OS spinlocks in AUTOSAR OS standard). Therefore, some error checks on OS configuration data are necessary. The error checks are not performed with optimized spinlocks thus reducing the runtime of Spinlock API

If our module has a chance for nesting of Spinlock then we should configure spinlock lock type as STANDARD. But if our implementation does not have nesting of spinlocks then we can go with OPTIMIZED spinlock

![](../../../../_images/Guidelines%20for%20Configuring%20Spinlock/image2022-12-27_14-43-18.png)

- Spinlock Successor: This is need if we configure spinlock type as STANDARD spinlock

![](../../../../_images/Guidelines%20for%20Configuring%20Spinlock/image2022-8-10_18-9-7.png)

Reference:

- Vector OS manual
- MultiCore - OS Spinlock configuration guideline - XC-CT Cerberus Platform - Docupedia (bosch.com)
- Safety analysis: Execution context of multi-core synchronization API - XC-CT Cerberus Platform - Docupedia (bosch.com)
