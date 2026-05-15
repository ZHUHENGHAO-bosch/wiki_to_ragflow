# Qual 8155 SM52 Suc 大屏Telltale显示监控测试

> Source: /spaces/CARSFW/pages/4204511260/Qual+8155+SM52+Suc+%E5%A4%A7%E5%B1%8FTelltale%E6%98%BE%E7%A4%BA%E7%9B%91%E6%8E%A7%E6%B5%8B%E8%AF%95
> Last modified: 2024-04-25T11:13:00.000+02:00

---

QUAL 8155 平台以实现仪表屏幕Telltale 显示监控功能，但其是否支持大屏Telltale显示监控功能呢？

为验证该功能，执行了以下测试，本文为此过程的记录。

## 1. Test Environment

- Hw Version: CHERY T1J  B0(QUAL 8155)
- SOC & SCC SW Version:
- Test tool

ubwc.zip

## 2. Test case 1

- Test Objective

SM52 Suc可以监控大屏显示的Telltale, 计算CRC，使用ROI区域1。

- ROI CRC Request:

x:200, y:200, width:60 height: 60

- 8155 MISR ROI CRC value: 0x8d187c1c

![](../../../_images/Qual%208155%20SM52%20Suc%20%E5%A4%A7%E5%B1%8FTelltale%E6%98%BE%E7%A4%BA%E7%9B%91%E6%8E%A7%E6%B5%8B%E8%AF%95/image-2024-4-25_15-45-28.png)

- TOOL CRC value: 0x8d187c1c

![](../../../_images/Qual%208155%20SM52%20Suc%20%E5%A4%A7%E5%B1%8FTelltale%E6%98%BE%E7%A4%BA%E7%9B%91%E6%8E%A7%E6%B5%8B%E8%AF%95/image-2024-4-25_15-48-7.png)

- Test result: OK

## 3. Test case 2

- Test Objective

SM52 Suc可以监控大屏显示的Telltale, 计算CRC，使用ROI区域2。

- ROI CRC Request:

x:200, y:200, width:50 height: 50

- 8155 MISR ROI CRC value: 0x6b168e76

![](../../../_images/Qual%208155%20SM52%20Suc%20%E5%A4%A7%E5%B1%8FTelltale%E6%98%BE%E7%A4%BA%E7%9B%91%E6%8E%A7%E6%B5%8B%E8%AF%95/image-2024-4-25_15-45-57.png)

TOOL CRC value: 0x6b168e76

![](../../../_images/Qual%208155%20SM52%20Suc%20%E5%A4%A7%E5%B1%8FTelltale%E6%98%BE%E7%A4%BA%E7%9B%91%E6%8E%A7%E6%B5%8B%E8%AF%95/image-2024-4-25_15-49-40.png)

- Test result: OK

## 4. Test case 3

- Test objective: SM52 Suc可以监控仪表，大屏显示的Telltale, 计算CRC。
- ROI CRC Request 1:

x:1546, y:112, width:50 height: 50

- ROI CRC Request 2:

x:200, y:200, width:60 height: 60

- 8155 MISR ROI CRC value 1: 0xa379968f

- 8155 MISR ROI CRC value 2: 0x8d187c1c

![](../../../_images/Qual%208155%20SM52%20Suc%20%E5%A4%A7%E5%B1%8FTelltale%E6%98%BE%E7%A4%BA%E7%9B%91%E6%8E%A7%E6%B5%8B%E8%AF%95/image-2024-4-25_15-39-30.png)

- TOOL CRC value 1: 0xa379968f， 与MCU ROI CRC Request的计算结果相同。OK。

![](../../../_images/Qual%208155%20SM52%20Suc%20%E5%A4%A7%E5%B1%8FTelltale%E6%98%BE%E7%A4%BA%E7%9B%91%E6%8E%A7%E6%B5%8B%E8%AF%95/image-2024-4-25_16-1-20.png)

- TOOL CRC value 2: 0x8d187c1c, ROI CRC Request同Test case 1， 结果相同， OK.

- Test result: OK
