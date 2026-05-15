# 202314 version GHS update

> Source: /spaces/CARSFW/pages/4454309646/202314+version+GHS+update
> Last modified: 2024-07-05T12:55:24.000+02:00

---

### When update GHS from 202114 to 202314 version.  with compile option -ONone , program flied and running in dead address.

![](../../../_images/202314%20version%20GHS%20update/image-2024-7-5_18-1-58.png)

Reason:

#### Normal case:  with -ODebug option

![](../../../_images/202314%20version%20GHS%20update/image-2024-7-5_18-2-26.png)

Startup_MbistTriggerNDST()  is a inline function and not  use a4 register.

![](../../../_images/202314%20version%20GHS%20update/image-2024-7-5_18-4-28.png)

#### Error Case:

#### with -ONone option

Startup_MbistTriggerNDST()  use a4 register and  Startup_MbistCheckResutl() --the 2ed function don't recalucate a4 address.

These 2 points result in the issue.

![](../../../_images/202314%20version%20GHS%20update/image-2024-7-5_18-3-10.png)

------------------------------------------------------------------------

#### Maybe Compiler think no one should change a4 register when use pseudo jump. So a4 won't change between 1st and 2ed function.

### There is a macro MBIST_USE_JUMP_FUN_CALL to use pseudo jump OR inline . Only pseudo jump can cause this issue

Below picture MBIST_USE_JUMP_FUN_CALL is 0u (inline function ).

![](../../../_images/202314%20version%20GHS%20update/image-2024-7-5_18-30-0.png)

![](../../../_images/202314%20version%20GHS%20update/image-2024-7-5_18-32-8.png)
