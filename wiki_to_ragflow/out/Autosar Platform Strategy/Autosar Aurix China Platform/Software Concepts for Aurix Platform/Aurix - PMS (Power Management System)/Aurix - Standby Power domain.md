# Aurix - Standby Power domain

> Source: /spaces/CARSFW/pages/2377378586/Aurix+-+Standby+Power+domain
> Last modified: 2023-05-09T07:26:29.000+02:00

---

## 1. Overview

The standby domain constitutes the standby RAM, the 8-bit standby controller, the Power Management unit, the Pin Wake-up unit, the Wake-up timer, the VEXT supply monitor, and basic infrastructure components

The standby domain is supplied by the EVRPR pre-regulator (VDDPD voltage) and is by default clocked by the 70 kHz internal low-power clock source in standby mode

## 2. Topologies

There are two possible topologies supported for standby operation depending on the supply connection

- Standby mode with both VEXT and VEVRSB supplied via common supply rail
- Standby mode with only VEVRSB domain supplied and VEXT domain switched off

### 2.1. Standby mode with both VEXT and VEVRSB supplied

![](../../../../_images/Aurix%20-%20Standby%20Power%20domain/image2022-8-5_14-47-10.png)

### 2.2. Standby mode with only VEVRSB domain supplied

![](../../../../_images/Aurix%20-%20Standby%20Power%20domain/image2022-8-5_14-48-14.png)

## 3. Topology for our Projects

We use the topology 2 where we switch OFF VEXT Supply to achieve sleep current consumption

In SCR code, we need to Turn OFF the external supply by making SYS_U33S_SCC_PWR_ON_3V3

![](../../../../_images/Aurix%20-%20Standby%20Power%20domain/image2022-8-5_15-1-21.png)

![](../../../../_images/Aurix%20-%20Standby%20Power%20domain/image-2023-5-9_13-26-24.png)
