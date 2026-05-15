# 07_The Unix Time(Uint32) overflow issue

> Source: /spaces/CARSFW/pages/2482525363/07_The+Unix+Time+Uint32+overflow+issue
> Last modified: 2024-11-01T08:50:02.000+01:00

---

## Information

The Unix Time is based on a second counter which was started counting on 01.Jan 1970. This value is using a signed 32bit type, which will overflow on „19th Jan 2038 (at 3:14:07 AM)“. Overflow here means that the MSB will be set, which usually means time before 1970! this will result in mis-interpretation of the value as „13th Dec. 1901 (8:45:52 PM)“

![](../../../_images/07_The%20Unix%20Time%28Uint32%29%20overflow%20issue/image2022-11-16_19-36-42.png)

Currently VCU is using time64 to avoid this issue, but our MCU is 32 bit operation system, and clarified with GHS, time64 is not a qualified compiler, we cannot use it in production. I think time is used for STR and RTC wakeup topic, vehicle is long term used, in the meanwhile, 2038 is not so far now, we should take care of this issue as well.

## Solution

int 32 → uint32

## Fix Status
