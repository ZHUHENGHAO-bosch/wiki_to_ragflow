# AuSm - Hints and Lesson Learnt

> Source: /spaces/CARSFW/pages/3170508184/AuSm+-+Hints+and+Lesson+Learnt
> Last modified: 2023-06-25T12:38:25.000+02:00

---

### Lesson 1:

Clearing an SMU alarm for a SSH (SRAM support Hardware) from application SW will not happen if ECCD of the corresponding SSH is set. So if you find an SMU alarm is not able to clear from application SW, check the corresponding ECCD register is cleared or not.

For example, as shown in below picture ECCD for CAN21 SSH is not cleared. With this when we test RAM FIT we got a Reset from AuSM_SMU_AlarmStatusClear API since the SBE alarm of CAN is not able to clear.

Issue Fix: We cleared the ECCD of CAN2, then the API AuSM_SMU_AlarmStatusClear passed.

![](../../../../../_images/AuSm%20-%20Hints%20and%20Lesson%20Learnt/image-2023-6-25_18-35-21.png)
