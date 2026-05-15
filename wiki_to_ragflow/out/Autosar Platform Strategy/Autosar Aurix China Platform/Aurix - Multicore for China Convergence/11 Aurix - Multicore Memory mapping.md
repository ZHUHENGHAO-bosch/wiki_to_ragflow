# 11 Aurix - Multicore Memory mapping

> Source: /spaces/CARSFW/pages/2441659017/11+Aurix+-+Multicore+Memory+mapping
> Last modified: 2023-02-21T02:03:23.000+01:00

---

## Overview

To achieve the performance it is needed to do the mapping of code and data properly

So, Where to keep the Share buffer ? DLMU of an Core where Write access from other cores would be 5 and read cycles would be 7

We need to keep Core 0 more efficient. So the memory which is accessed by Core 0 more frequently, better to keep it DLMU0. If this memory is not sufficient we will also use DLMU1 for sgared memory

![](../../../_images/11%20Aurix%20-%20Multicore%20Memory%20mapping/image2022-9-29_10-3-19.png)

![](../../../_images/11%20Aurix%20-%20Multicore%20Memory%20mapping/image2023-2-21_9-3-15.png)
