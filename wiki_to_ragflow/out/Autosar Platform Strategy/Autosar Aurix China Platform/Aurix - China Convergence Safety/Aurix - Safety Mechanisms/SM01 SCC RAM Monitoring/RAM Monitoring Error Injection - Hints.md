# RAM Monitoring Error Injection - Hints

> Source: /spaces/CARSFW/pages/2910537349/RAM+Monitoring+Error+Injection+-+Hints
> Last modified: 2023-04-08T07:18:28.000+02:00

---

### Introduction

Aurix allows us to inject error to test the safety mechanisms.

### ECC error injection (Except DTAG)

It is possible to manually inject errors during memory tests (for example, to test the software). For a non-destructive test, an error in the data can be introduced by programming a word with wrong ECC before the test, via the ECCMAP bits.

![](../../../../../_images/RAM%20Monitoring%20Error%20Injection%20-%20Hints/image-2023-4-3_16-52-45.png)

![](../../../../../_images/RAM%20Monitoring%20Error%20Injection%20-%20Hints/image-2023-4-3_16-53-10.png)

![](../../../../../_images/RAM%20Monitoring%20Error%20Injection%20-%20Hints/image-2023-4-3_17-5-30.png)

### ECC Error Injection (DTAG)

The above section will work for all SSH except DTAG → The below details are from ERRATA sheet

![](../../../../../_images/RAM%20Monitoring%20Error%20Injection%20-%20Hints/image-2023-4-3_17-8-44.png)

![](../../../../../_images/RAM%20Monitoring%20Error%20Injection%20-%20Hints/image-2023-4-8_13-18-19.png)
