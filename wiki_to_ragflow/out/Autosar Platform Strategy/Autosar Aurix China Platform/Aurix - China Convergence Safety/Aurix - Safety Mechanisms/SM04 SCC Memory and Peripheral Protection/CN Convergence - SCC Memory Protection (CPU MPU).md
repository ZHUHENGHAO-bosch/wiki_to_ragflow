# CN Convergence - SCC Memory Protection (CPU MPU)

> Source: /spaces/CARSFW/pages/2940961184/CN+Convergence+-+SCC+Memory+Protection+CPU+MPU
> Last modified: 2023-04-13T08:20:48.000+02:00

---

### Introduction

To support memory protection which protects ASIL regions from QM access we have the following components.

- Service.OsHooks
- Service.ContextSwicher
- Aurix.SafetyManager

Usually, any illegal memory access will end up in Trap. All Traps are processed by OS and we enter Safe State via Service.OsHooks module.

![](../../../../../_images/CN%20Convergence%20-%20SCC%20Memory%20Protection%20%28CPU%20MPU%29/SM04%20Memory%20Protection.bmp)
