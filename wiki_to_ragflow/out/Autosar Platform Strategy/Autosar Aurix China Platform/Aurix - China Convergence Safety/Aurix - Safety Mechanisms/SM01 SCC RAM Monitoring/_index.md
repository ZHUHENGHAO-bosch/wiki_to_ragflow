# SM01 SCC RAM Monitoring

> Source: /spaces/CARSFW/pages/2421044513/SM01+SCC+RAM+Monitoring
> Last modified: 2023-01-29T06:53:02.000+01:00

---

### Overview

Aurix has the following safety measures to detect errors in SRAM

- Error Detection and Correction Codes / Logic
- Address Error Monitor

Any corruption in HW will be notified to SMU. SMU triggers the interrupt which will handled by Aurix.SafetyManager component

![](../../../../../_images/SM01%20SCC%20RAM%20Monitoring/SM1%20RAM%20Monitoring.bmp)

![](../../../../../_images/SM01%20SCC%20RAM%20Monitoring/image2022-9-16_13-34-45.png)
