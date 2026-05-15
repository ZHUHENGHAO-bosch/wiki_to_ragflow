# Taiji - VCU Architecture difference

> Source: /spaces/CARSFW/pages/7010069212/Taiji+-+VCU+Architecture+difference
> Last modified: 2026-04-22T04:01:13.000+02:00

---

## Overview

This page is to summarize the architecture difference between VCU and Taiji platform

## Architecture Differences

| Usecase/Domain | VCU | Taiji | Solution |
| --- | --- | --- | --- |
| Stack supported | Vector | Vector and Cubas and (RTA-CAR in future) |  |
| LCM | PLC - PowerLifeCycle | PSC - PowerStateController |  |
| Service.EcuModeManager |  | John: Propose to move to VCU architecture |
| Service.PowerManager |  | John: Propose to move to VCU architecture |
| SystemM - full feature since it is connected with PSC | SystemM - just as interface |  |
|  | SystemStateManager | SystemStateController |  |
| Audio |  |  |  |
| Thermal |  |  |  |
| RtcHandler |  |  |  |
|  |  |  |  |
|  |  |  |  |
