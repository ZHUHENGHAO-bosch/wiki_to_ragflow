# SRAM Error Handling - Aurix Hints

> Source: /spaces/CARSFW/pages/2423647018/SRAM+Error+Handling+-+Aurix+Hints
> Last modified: 2022-09-16T14:17:00.000+02:00

---

Considerations for SRAM Error Handling is given in Aurix Safety Manual

|   |   |
| --- | --- |
| Error | Handling |
| SBE correction | the alarm can be configured for no reaction |
| DBE, address error detection, or ETRR overflow | First event occurrence do an Application Reset If Second error is detected within the same driver cycle, the function which uses the memory shall be considered non-operational. The system integrator has to take measures to prevent interference from the non-operational function |
| Error event signaled by FAULTSTS.OPERR or FAULTSTS.MISCERR bit fields | First event occurrence do the actions as mentioned in the tables Mapping of Errors to FAULTSTS.OPERR and UCE alarm Mapping of Errors to FAULTSTS.MISCERR and ME alarm If Second error is detected within the same driver cycle, the function which uses the memory shall be considered non-operational. The system integrator has to take measures to prevent interference from the non-operational function |

#### Mapping of Errors to FAULTSTS.OPERR and UCE alarm

![](../../../../../_images/SRAM%20Error%20Handling%20-%20Aurix%20Hints/image2022-9-16_17-40-22.png)

#### Mapping of Errors to FAULTSTS.MISCERR and ME alarm

![](../../../../../_images/SRAM%20Error%20Handling%20-%20Aurix%20Hints/image2022-9-16_17-41-5.png)
