# ENABLE and DISABLE instruction in USER-1 Mode

> Source: /spaces/CARSFW/pages/3245435640/ENABLE+and+DISABLE+instruction+in+USER-1+Mode
> Last modified: 2023-07-15T06:13:22.000+02:00

---

### Overview

As per the Tricore architecture we can call ENABLE and DISABLE instruction in USER-1 Mode

![](../../../../../_images/ENABLE%20and%20DISABLE%20instruction%20in%20USER-1%20Mode/image-2023-7-15_12-11-31.png)

But we see Trap is called if we execute these instructions in User mode with Vector OS

Reason for this issue is

we can explicitly disable the access of these instructions in User-1 mode by enabling U1_IED bit in SYSCON register

- Start OS is enabling this bit and hence if we call ENABLE or DISABLE instruction in USER mode ends in trap (Protection Hook)

![](../../../../../_images/ENABLE%20and%20DISABLE%20instruction%20in%20USER-1%20Mode/image-2023-7-15_12-13-9.png)
