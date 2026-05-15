# CDD for Multicore

> Source: /spaces/CARSFW/pages/2394061660/CDD+for+Multicore
> Last modified: 2022-09-21T07:25:10.000+02:00

---

## Overview

In case of CDD, multicore capability has to be ensured by implementation and design

Methods to achieve consistency

1. Avoid shared RMW data
2. Serialize access to shared resources
3. Partition awareness / Core dependent branching → Core specific behavior implementation

## Methods

### 1. Avoid RMW data (Same Code runs in different Cores)

Each CDD BSW instance should operate on its own set of RMW (Read-Modify-Write) data, reducing the serialization to maximum

![](../../../../_images/CDD%20for%20Multicore/Avoid%20RMW%20data.png)

Note: This approach this very difficult if MCAL runs only in BSW Core

### 2. Serialize data

Use Spinlock for shared data

![](../../../../_images/CDD%20for%20Multicore/Serialize%20data.png)

### 3. Core specific Handling

Core dependent branching

- Using GetCoreId() and GetApplicationId() APIs
- Each core invokes different APIs in one module

### Example use case for Core specific Handling:

MCAL only in BSW Core

If the design is such a way that MCAL modules present only in BSW Core, then a satellite or proxy functions are required for CDD

![](../../../../_images/CDD%20for%20Multicore/CDD%20Proxy.png)
