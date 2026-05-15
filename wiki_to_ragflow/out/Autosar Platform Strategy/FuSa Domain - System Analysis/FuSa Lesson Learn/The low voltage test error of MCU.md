# The low voltage test error of MCU

> Source: /spaces/CARSFW/pages/6692160466/The+low+voltage+test+error+of+MCU
> Last modified: 2026-01-16T02:55:03.000+01:00

---

1、Background information:

MAXUS软件在做低压缓启动时，KL30电压在3.9V时MCU一直在reset，当KL30电压再上升时该reset一直存在，现象表现为MCU

启动失败。

2、测试数据分析如下：

黄色 WDI 绿色 SYS_ALIVE  蓝色 reset1 红色reset2

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-15_11-14-54.png)

如上图，MCU复位后执行LBIST，此时外狗WDI被拉高（由HWCFG6影响），激活外狗的喂狗时序，之后外狗进入close window。

但是由于LBIST执行完后大约18ms左右触发MCU冷复位且会影响WDI的电平翻转（由低变高），激活喂狗action，但外狗仍处在

close window，此时喂狗属于错误喂狗时序，导致外狗RESET pin拉低，从而引发MCU的PORST拉低，导致MCU的warm power

reset，这种情况循环往复出现从而导致MCU未能正确启动运行。

3、Error分析如下：

由于TC3xx是ASIL-D标准芯片，在MCU上电且未执行PORT初始化前，需要将PORT的状态设置为已知的配置状态。该操作是由

HWCFG6的状态指引的，而HWCFG6的状态是由如下图寄存器（PMSWCR5.TRISTREQ）配置指示。

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-15_14-29-56.png)

HWCFG pin的状态在MCU reset之后是默认的weak pull-up

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-15_17-54-50.png)

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-15_14-32-57.png)

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202026-01-15%20143202.png)

PMSWCR5配置由EB实现，配置方式及生成代码如下

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-15_17-13-42.png)

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-15_17-16-20.png)

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-16_9-53-46.png)

4、软件修改后测试（3.9V）

![](../../../_images/The%20low%20voltage%20test%20error%20of%20MCU/image-2026-1-15_17-32-17.png)

软件修改后测试，在MCU上电后WDI pin电平状态load HWCFG6 pin电平状态（pull-up），在执行LBIST时和LBIST完成之后，WDI

电平不会发生翻转，故不会导致异常的外狗喂狗时序，此时MCU可以正确启动运行。
