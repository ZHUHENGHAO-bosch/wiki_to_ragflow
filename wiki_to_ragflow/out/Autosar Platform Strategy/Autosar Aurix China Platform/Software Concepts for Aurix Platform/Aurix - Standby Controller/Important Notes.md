# Important Notes

> Source: /spaces/CARSFW/pages/2372929857/Important+Notes
> Last modified: 2023-03-13T06:28:57.000+01:00

---

If you enable only SCR wakeup in PMSWCR0 (Standby and Wake-up Control Register_, then Aurix can be started only when actual wakeup source is detected

To make Aurix start on Power on Reset, make sure the below bit is set in PMSWCR0 register

![](../../../../_images/Important%20Notes/image2022-8-1_10-33-52.png)

![](../../../../_images/Important%20Notes/image2022-8-1_10-35-19.png)
