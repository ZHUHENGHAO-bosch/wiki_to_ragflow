# FEL and EM overview

> Source: /spaces/CARSFW/pages/2392025936/FEL+and+EM+overview
> Last modified: 2023-01-13T07:53:10.000+01:00

---

## Overview

We have two mechanisms to log error information into NVM memory

1. FatalErrorLogger(FEL) from CI2 Hydra Platform
2. ErrorMemory from CI1 Project (GM VCU)

We need to decide for China Convergence platform which mechanism to use (FEL or ErrorMemory or both)

## FatalErrorLogger

1. Modules write data into NVM via FEL module
2. To read the data from NVM we need
3. Once the data is read, we have a parser which will convert raw data to human readable format

![](../../../../_images/FEL%20and%20EM%20overview/FELOverview.jpg)

## ErrorMemory

1. Module write into SCC Error Memory buffer via ErrorMemory_WriteMessage
2. Service.ErrorMemory cyclically transfer error data to SoC ErrMem Resource Manager via INC
3. SoC ErrMem Resource Manager dumps error data into ErrMem file
4. Tester can read the error data via USB (em_trace module in SoC read data from ErrMem file on request via USB)

![](../../../../_images/FEL%20and%20EM%20overview/ErrorMemory_Overview.jpg)
