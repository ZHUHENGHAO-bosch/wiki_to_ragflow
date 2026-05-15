# How to implement TC3xx EVADC reference plausibility check using VDDK

> Source: /spaces/CARSFW/pages/6699097678/How+to+implement+TC3xx+EVADC+reference+plausibility+check+using+VDDK
> Last modified: 2026-01-16T09:47:59.000+01:00

---

1.Requirement Analysis

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_9-59-36.png)

According to the user manual, to perform a plausibility check of the Vref voltage of the EVADC, the internal

Vddk of the EVADC can be used to verify the plausibility of the Vref voltage. Vddk is sampled by the voltage

configured on GxCH29, and GxCH29 can be mapped to GxCH0 of any EVADC hardware unit. That is, the voltage

sampling value of Vddk can be read from the result register of GxCH0 (if configured correctly).

user manual information interpretation

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-5-35.png)

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-6-24.png)

By configuring Alias register in CH0/CH1.The Alias feature allows the user to redirect conversion requests for

channels 0 and/or 1 to other channel numbers. Using the alias feature, a conversion request for channel 0 or

channel 1 leads to a conversion of the analog input channel “x” instead of channel 0 or channel 1. To use CH29

(Vddk reference signal) for channel 0 or 1 simply setGxALIAS.ALIAS0/1=29 and the successive conversion

result on Ch0/1 will contain the Vddk signal level. Channel configuration and result register assignment are

chosen in GxCHCTR0/1 (Channel Control Registers).

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-8-37.png)

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-8-54.png)

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-9-6.png)

2.Function Implementation-Mcal Configuration

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-10-1.png)

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-10-14.png)

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-10-40.png)

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-36-38.png)

3.Function Implementation-Coding

![](../../../_images/How%20to%20implement%20TC3xx%20EVADC%20reference%20plausibility%20check%20using%20VDDK/image-2026-1-16_10-11-28.png)

After mapping the VDDK voltage sampling to GxCHy using EB configuration, the VDDK voltage sampling value can be read in

the result register of GxCHy.
