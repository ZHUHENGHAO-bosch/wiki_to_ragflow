# 01_Multicore Introduction

> Source: /spaces/CARSFW/pages/2383057042/01_Multicore+Introduction
> Last modified: 2022-09-20T16:38:47.000+02:00

---

## Overview

We already struggled a lot on performance (OS loading) problems with Single core systems (example RH850) in previous convergence projects.

Since we are moving to Aurix which has Multiple core (i.e. TC37x has three cores), it is important to have multicore concept and implementation for China convergence platform

## Motivation of Multicore

Speed: A computational problem can be calculated in shorter time

Speed can be increased by parallel processing

But synchronization between cores have overhead

![](../../../_images/01_Multicore%20Introduction/Untitled%20Diagram.png)

## Workload Split

![](../../../_images/01_Multicore%20Introduction/Worksplit.png)
