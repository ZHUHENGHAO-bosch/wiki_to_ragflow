# 08_Multicore Communication

> Source: /spaces/CARSFW/pages/2396097495/08_Multicore+Communication
> Last modified: 2022-08-19T11:39:40.000+02:00

---

## Overview

Data exchange between core boundaries can be done in

- Proxy Component
- Master-Satellite functionality

## Concepts

### Master-Satellite functionality

- A BSW satellite is a part of a BSW service module
- The idea is that the satellite offers services core-local, which means that it is executed on the same core as the accessing application SWC.
- The functional scope of satellites ranges from full copies of the service to very basic functionality

With Microsar below modules use Satellites

- WdgM
- Dem
- EcuM
- Det

Example WdgM,

![](../../../_images/08_Multicore%20Communication/image2022-8-19_15-6-17.png)

![](../../../_images/08_Multicore%20Communication/image2022-8-19_15-7-2.png)

### Proxy Component

- A proxy translates the services of a BSW service module to a different interface type
- The idea is to substitute the execution time expensive cross-core Client/Server operations with more lightweight Sender/Receiver Port Interfaces. Hence, whenever a SWC uses a service, it merely reads or writes data in shared RAM (Rte) instead of triggering a RPC
- Proxies are located above the Rte
- The usage of proxies requires a change of the SWC port interface from C/S to S/R. That is why a SWC must either be designed like this right from the beginning or allow such a modification during integration

Modules which uses proxies:

- NvM-Proxy
- Com-Proxy

COM

- Receives Tx signal data via S/R interface instead of C/S Calls
- Passes latest data to COM immediately before transmission
- Buffers Rx data in RTE to allow direct cross-core access

NVM

- Access to NV data via S/R interface instead of C/S calls

![](../../../_images/08_Multicore%20Communication/image2022-8-19_15-9-33.png)
