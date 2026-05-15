# zAurix Reset Handling (Obsolete)

> Source: /spaces/CARSFW/pages/2503822826/zAurix+Reset+Handling+Obsolete
> Last modified: 2023-01-20T08:54:32.000+01:00

---

## Proposed solution for A0 Sample:

![](../../../../../_images/zAurix%20Reset%20Handling%20%28Obsolete%29/image2022-11-9_12-1-20.png)

Reset solution Alternate 1:

draw.io Diagram attachment access error: cannot display diagram

Reset Solution Alternate 2:

draw.io Diagram attachment access error: cannot display diagram

After PORST reset, FSP0 will be LOW state, after enabling external watchdog, SW must call SMU_ReleaseFSP() so that FSP pin can move to HIGH state

![](../../../../../_images/zAurix%20Reset%20Handling%20%28Obsolete%29/image2022-10-13_16-2-26.png)
