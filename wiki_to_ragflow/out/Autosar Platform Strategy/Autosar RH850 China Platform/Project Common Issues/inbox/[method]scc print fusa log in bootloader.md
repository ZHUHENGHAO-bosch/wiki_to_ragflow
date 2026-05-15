# [method]scc print fusa log in bootloader

> Source: /spaces/CARSFW/pages/2904693313/method+scc+print+fusa+log+in+bootloader
> Last modified: 2023-03-31T07:07:55.000+02:00

---

### Infomation

We have a requirement, if reseting 25 times in application, mcu should jump into bootloader.

In order to troubleshoot whether it was caused by FUSA, We should print fusa error memory infomation to help analysis.

### Solution

we can print the data of FUSA SM15 stored in retention RAM in the app in the bootloader.

| project | status | patch & RTC |
| --- | --- | --- |
| Geely | DONE | RTC link |
|  |  |  |
