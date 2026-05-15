# FSP Handling - SCC Reset control

> Source: /spaces/CARSFW/pages/2635505397/FSP+Handling+-+SCC+Reset+control
> Last modified: 2023-01-13T09:46:07.000+01:00

---

### Overview

Since we have External WDG in Aurix convergence projects, it is important that we need make sure any internal Reset in SCC should not end in a double reset by external WDG

### FSP connection

- When any one of the Reset pins of external WDG is asserted, WDG monitoring functionality of external WDG will be disabled
- FSP0 pin is connected to IN2 of external WDG and IN2 has direct mapping with Reset2 pin.

![](../../../../../_images/FSP%20Handling%20-%20SCC%20Reset%20control/image2023-1-9_10-44-25.png)

- Below picture shows the FSP pin control

![](../../../../../_images/FSP%20Handling%20-%20SCC%20Reset%20control/image2023-1-9_10-46-59.png)

- So, at startup, FSP will be in asserted state which means external WDG functionality will be disabled, only when ReleaseFSP is called, external WDG functionality will start.

### Open points:

@Luo Ellen

1. At which point Safety module will release FSP ?
2. When there is an issue with SM52 we will assert FSP, at this time external WDG will be disabled. Is this ok from Safety view?
