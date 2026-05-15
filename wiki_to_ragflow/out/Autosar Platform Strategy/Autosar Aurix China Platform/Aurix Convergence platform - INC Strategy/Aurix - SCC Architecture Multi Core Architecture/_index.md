# Aurix - SCC Architecture Multi Core Architecture

> Source: /spaces/CARSFW/pages/2345532859/Aurix+-+SCC+Architecture+Multi+Core+Architecture
> Last modified: 2023-04-04T10:53:56.000+02:00

---

### Introduction

We need to think of an Multi Core solution for INC since few customers want INC over SPI at 10Mbps

Also in few projects, INC module was the one who took most of the CPU time causing CPU load issues

Below are the proposal for INC in Multicore

### Proposal 1:

Since Inc is in am QM path, we can have masters of IncTp and IncRouter modules to run Core 3 (Non-lockstep CPU)

And respective Satellite can run in other cores (Core 0 and Core 1)

![](../../../../_images/Aurix%20-%20SCC%20Architecture%20Multi%20Core%20Architecture/image2022-7-6_17-33-12.png)
