# FuSa SoC Platform

> Source: /spaces/CARSFW/pages/6966125854/FuSa+SoC+Platform
> Last modified: 2026-03-25T06:03:40.000+01:00

---

We need build SoC side applications for both QNX and linux  on Qualcomm/MTK.

|  | Qualcomm | MTK |
| --- | --- | --- |
| QNX |  | NA |
| Linux |  |  |

## Tasks

Task1: 分析linux下差异及需要抽象化的功能。

Task2: 对模块的重构， 兼容linux。 分析yocto 编译架构做兼容。 主要为 中间件，log 以及 display 接口的抽象和兼容。

Task3: 合入taiji分支项目，并压测。

Task4: 分析MTK Telltale 校验架构。

Task5: 实现平台中的MTK 兼容。

![](../../../_images/FuSa%20SoC%20Platform/fusa%20soc%20different%20platform%20plan.png)
