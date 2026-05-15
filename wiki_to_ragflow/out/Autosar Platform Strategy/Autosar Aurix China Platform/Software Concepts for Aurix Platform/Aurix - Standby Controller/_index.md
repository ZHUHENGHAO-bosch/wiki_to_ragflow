# Aurix - Standby Controller

> Source: /spaces/CARSFW/pages/2321473032/Aurix+-+Standby+Controller
> Last modified: 2023-03-13T06:28:16.000+01:00

---

TC3XX has an separate controller which runs with XC800 Core which is used to wakeup the Tricore controller

Below is the diagram which shows the shared pins between Tricore and SCR

Note : Only these pins can wake the Tricore on entering standby mode

SCR need an separate Compiler to compile its code Keil C51 (This compiler can be downloaded from VP_ArtifactoryTools Antifactory)

Cerberus PF team has an PoC for waking Tricore with SCR, below is the link

Integration of SCR in Cerberus PF - XC-CT Cerberus Platform - Docupedia (bosch.com)

![](../../../../_images/Aurix%20-%20Standby%20Controller/image2022-6-20_20-5-29.png)

### Block diagram of SCR

![](../../../../_images/Aurix%20-%20Standby%20Controller/image2022-6-21_8-25-34.png)
