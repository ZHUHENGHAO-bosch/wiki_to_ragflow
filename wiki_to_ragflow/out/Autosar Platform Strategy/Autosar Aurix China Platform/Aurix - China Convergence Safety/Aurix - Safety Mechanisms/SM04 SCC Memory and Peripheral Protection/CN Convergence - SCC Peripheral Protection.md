# CN Convergence - SCC Peripheral Protection

> Source: /spaces/CARSFW/pages/2940961931/CN+Convergence+-+SCC+Peripheral+Protection
> Last modified: 2023-04-15T07:51:22.000+02:00

---

### Introduction

We need to protect the peripheral from other Bus Master access.

- Aurix provides Access Enable Register for all peripheral where we can configure which Bus master can access the Register of peripherals
- Each Memory sections are protected with BUS MPU, we can configure the access to required Bus Masters. If any Bus master tries to access the Memory without access will end up in a trap.

![](../../../../../_images/CN%20Convergence%20-%20SCC%20Peripheral%20Protection/SM04%20Peripheral%20Protection.bmp)
