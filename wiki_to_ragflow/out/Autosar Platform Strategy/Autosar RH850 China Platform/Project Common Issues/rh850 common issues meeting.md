# rh850 common issues meeting

> Source: /spaces/CARSFW/pages/2904701199/rh850+common+issues+meeting
> Last modified: 2024-12-13T09:03:23.000+01:00

---

13 Dec 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | NA |
| VCU Pro(F1KH) | soc 8255 下电时序需要更新 | NA |
| VCU Plus | vcu plus/CCU 升级DBC,从CAN到CANFD的 RTE错误修复 | NA |
| CCU | NA | MPU报错 DMA？ 没再复现，再观察下 |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA |
| Chery 8255 (D01) | N A audio 6511替代6424 6511 只在chery 8255和MAXUS 8155项目上用 soc 8255 下电时序需要更新 | S AIL → Taiji 波特率：961200 ， 会偶尔丢数据 改成DMA，问题解决 wiki |
| MAXUS 8155 | NA | NA |
| SGMW 五菱 --暂停 | MIC优化：支持持续检测mic通道故障 PCM6240/PCM6260 supports to continuous detect mic channel faults | NA |

3 同步情况

见 00_Overview

29 Nov 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A SM52 的AI方案 |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki 64byte canfd 刷标定, Bootload需要更改CANIF,CANTP，CAN Drv, ECUC相关配置 | 触发OS_ERROR_HOOK (Bug 2295232) https://rbcm-gerrit.de.bosch.com/c/projects/vcupro/autosar/bosch/+/856946 udrop 60连续触发os set event.测试问题 |
| VCU Plus | vcu plus/CCU 升级DBC,从CAN到CANFD的 RTE错误修复 | NA |
| CCU |  |  |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |
| Chery 8255 (D01) | N A. audio 6511替代6424 | SAIL → Taiji 波特率：961200 ， 会偶尔丢数据 |
| MAXUS 8155 | NA | NA. |
| SGMW | MIC优化：支持持续检测mic通道故障 PCM6240/PCM6260 supports to continuous detect mic channel faults | NA. |

3 同步情况

见 00_Overview

15 Nov 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A SM52 的AI方案 |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki 64byte canfd 刷标定, Bootload需要更改CANIF,CANTP，CAN Drv, ECUC相关配置 | 触发OS_ERROR_HOOK (Bug 2295232) https://rbcm-gerrit.de.bosch.com/c/projects/vcupro/autosar/bosch/+/856946 |
| VCU Plus | vcu plus/CCU 升级DBC,从CAN到CANFD的 RTE错误修复 | NA |
| CCU |  |  |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |
| Chery 8255 (D01) | N A. audio 6511替代6424 | SAIL → Taiji 波特率：961200 ， 会偶尔丢数据 |
| MAXUS 8155 | NA | NA. |
| SGMW | MIC优化：支持持续检测mic通道故障 PCM6240/PCM6260 supports to continuous detect mic channel faults | NA. |

3 同步情况

见 00_Overview

01 Nov 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A SM52 的AI方案 |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki | 触发OS_ERROR_HOOK (Bug 2295232) |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn RTC随机值问题，低概率会导致MCU不能退STR问题 https://inside-docupedia.bosch.com/confluence/display/GG/RTC+RA8804CE+unexpectedly+triggered+the+AF+flag | NA. |
| Chery 8255 (D01) | N A. inc-tp timeout https://rbcm-gerrit.de.bosch.com/q/topic:%22RTC1-2213961%22 | SAIL → Taiji |
| MAXUS 8155 | NA | NA. |
|  |  |  |

3 同步情况

见 00_Overview

18 Oct 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A SM52 的AI方案 |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki | APPLTask_ASIL 堆栈溢出 saiL bootcfg ，→ A1 MD13，14 output; B0  MD13，14  input |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn RTC随机值问题，低概率会导致MCU不能退STR问题 https://inside-docupedia.bosch.com/confluence/display/GG/RTC+RA8804CE+unexpectedly+triggered+the+AF+flag | NA. |
| Chery 8255 (D01) | N A. inc-tp timeout https://rbcm-gerrit.de.bosch.com/q/topic:%22RTC1-2213961%22 | NA. |

3 同步情况

见 00_Overview

TODO:

Black screen Issue Analysis - XC-CT China - Docupedia (bosch.com)

06 Sep 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki VCU 1.0 inc-TP spi 偏移1bit ： ongoing 片选设置time短,当前 0.5 clock cycle → 高通建议3.5clock cycle | APPLTask_ASIL 堆栈溢出 saiL bootcfg ，→ A1 MD13，14 output; B0  MD13，14  input |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |
| Chery 8255 | N A. inc-tp timeout https://rbcm-gerrit.de.bosch.com/q/topic:%22RTC1-2213961%22 | NA. |

3 同步情况

见 00_Overview

23 Aug 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki VCU 1.0 multi 可以设置不初始化retention ram inc-TP spi 偏移1bit ： ongoing 片选设置time短,当前 0.5 clock cycle → 高通建议3.5clock cycle | APPLTask_ASIL 堆栈溢出 |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |
| Chery 8255 | How To - I2S on Aurix TC3xx - GEN4 generic - Docupedia (bosch.com) RTC Restructure/Optimize - SCC | NA. |

3 同步情况

见 00_Overview

26 Jul 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki VCU 1.0 multi 可以设置不初始化retention ram inc-TP spi 偏移1bit ： ongoing | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |
| Chery 8255 | How To - I2S on Aurix TC3xx - GEN4 generic - Docupedia (bosch.com) RTC Restructure/Optimize - SCC | NA. |

3 同步情况

见 00_Overview

28 Jun 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki |  |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |
| Chery 8255 | How To - I2S on Aurix TC3xx - GEN4 generic - Docupedia (bosch.com) RTC Restructure/Optimize - SCC | NA. |

3 同步情况

见 00_Overview

31 May 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | Audio 反向电动势引起的DC诊断故障 01- GAC TAS6424诊断问题 | NA |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |
| Chery 8255 | How To - I2S on Aurix TC3xx - GEN4 generic - Docupedia (bosch.com) RTC Restructure/Optimize - SCC |  |

3 同步情况

见 00_Overview

17 May 2024

背景：

在zeekr 的DV测试的时候曾经发现串口log打印太多把系统搞挂了

Action ：

@ZHAO Yanqiang (XC-CP/ESW2-CN) 检查下我们的代码，是否有直接调用printf把log打印到串口的实现，确认下是否必须打印到串口，如果非必须则需要使用其他的log机制。

https://inside-docupedia.bosch.com/confluence/display/CARSFW/Taiji+Log+Strategy

现在Taiji中改动，其他项目 @LIU Dezhi (XC-CP/ESW2-CN) 在FO sync会议中让大家检查和修改

19 Apr 2024

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | Audio 反向电动势引起的DC诊断故障 | NA |
| GAC | NA | NA |
| GWM | NA | NA GWM SUC 请求CRC，CRC响应新请求有延迟。 不会造成sm52校验失败 根本解决需要升高通基线，暂时不考虑。 |
| BYD | NA | N.A. |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |

3 同步情况

见 00_Overview

22 Mar 2024

重要问题

|  |  |
| --- | --- |
|  |  |
|  |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA info 8295 ROI MISR Summary Vedio : https://docs.qualcomm.com/bundle/resource/video/VD80-49946-1C |
| GAC | NA | NA SM54 和BSP都直接从屏寄存器，GAC check一下 |
| GWM | NA HSM key 读不出，导致卡在boot https://jira-shzj.auto-link.com.cn/browse/GWM35-63500 | NA GWM SUC 请求CRC，CRC响应新请求有延迟。 |
| BYD | NA | N.A. |
| VCU Pro(F1KH) | F1KH芯片型号更换的LL wiki | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |

3 同步情况

见 00_Overview

08 Mar 2024

重要问题

|  |  |
| --- | --- |
|  |  |
|  |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA info 8295 ROI MISR Summary Vedio : https://docs.qualcomm.com/bundle/resource/video/VD80-49946-1C |
| GAC | NA | NA SM54 和BSP都直接从屏寄存器，GAC check一下 |
| GWM | NA FW analysis and summary for Vdata abnormal transmit.msg HSM key 读不出，导致卡在boot https://jira-shzj.auto-link.com.cn/browse/GWM35-63500 | NA SM54 和BSP都直接从屏内读寄存器，导致冲突 SM54删掉读寄存器的逻辑,只走bsp通路 GWM SUC 请求CRC，CRC响应新请求有延迟。 |
| BYD | NA | N.A. |
| VCU Pro(F1KH) |  |  |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |

3 同步情况

见 00_Overview

29 Dec 2023

重要问题

|  |  |
| --- | --- |
|  |  |
|  |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | NA | NA info 8295 ROI MISR Summary Vedio : https://docs.qualcomm.com/bundle/resource/video/VD80-49946-1C |
| GAC | NA | NA SM54 和BSP都直接从屏寄存器，GAC check一下 |
| GWM | NA FW analysis and summary for Vdata abnormal transmit.msg | NA SM54 和BSP都直接从屏内读寄存器，导致冲突 SM54删掉读寄存器的逻辑 |
| BYD | NA | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA |
| Chery | Lessons Learn | NA. |

3 同步情况

见 00_Overview

15 Dec 2023

重要问题

|  |  |
| --- | --- |
| 1 | 把maindev patch强推SCC patch到sop分支，因SCC和SOC有共有仓库，导致SCC更新SOC没更新 后续做法不再强推，各模块自己维护各种模块 与SOC存在逻辑关联仓库 - GEN4 generic - Docupedia (bosch.com) |
|  |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | vdata txbuff full | Udrop40 issue |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | Alarm 7 – 在咨询英飞凌ing FW SRI Protocol error - SMU ALM717 - lesson learnt.msg |
| Chery | Lessons Learn | NA. |

3 同步情况

见 00_Overview

08 Dec 2023

重要问题

|  |  |
| --- | --- |
| 1 | RE Follow-up for IIC Bus driver enhancement.msg |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | vdata txbuff full | Udrop40 issue fusa进程 'signature-unit-controller' 拉了三次都没有被slm拉起来 https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1883143 wiki SOC侧进程无法启动issue |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | NA | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | Alarm 7 – 在咨询英飞凌ing FW SRI Protocol error - SMU ALM717 - lesson learnt.msg |
| Chery | Lessons Learn | NA. |

3 同步情况

见 00_Overview

24 Nov 2023

重要问题

|  |  |
| --- | --- |
| 1 |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | vdata txbuff full | Udrop40 issue fusa进程 'signature-unit-controller' 拉了三次都没有被slm拉起来 https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1883143 wiki SOC侧进程无法启动issue |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD |  | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | Alarm 7 – 在咨询英飞凌ing |
| Chery | Lessons Learn | MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... wiki |

3 同步情况

见 00_Overview

10 Nov 2023

重要问题

|  |  |
| --- | --- |
| 1 |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | vdata txbuff full | Udrop40 issue fusa进程 'signature-unit-controller' 拉了三次都没有被slm拉起来 https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1883143 |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) LIU Dezhi (XC-CP/ESW2-CN) 建个空白wiki 偶发 压测STR, LCM状态没有及时传上去， ongoing | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | Alarm 7 – 在咨询英飞凌ing |
| Chery | Lessons Learn SCR watch dog reset before enter sleep mode | MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... wiki |

3 同步情况

见 00_Overview

03 Nov 2023

重要问题

|  |  |
| --- | --- |
| 1 |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | boot 下路由诊断报文丢失testerpresent,ongoing doip/pdur/cantp链路 53F 不在SDB里，和7FF冲突  –-- 详细细节 wiki @ZHAO Wei Geely FS11-A2 Bootloader路由TesterPresent问题 NA. | NA Udrop40 issue |
| GAC | NA | NA |
| GWM | NA | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) LIU Dezhi (XC-CP/ESW2-CN) 建个空白wiki 偶发 压测STR, LCM状态没有及时传上去， ongoing | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | Alarm 7 – 在咨询英飞凌ing |
| Chery | Lessons Learn SCR | MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... BM→APP , 出问题时 80+ms zeekr, bm WDG 失效， HSM 拉复位 wiki |

3 同步情况

见 00_Overview

27 Oct 2023

重要问题

|  |  |
| --- | --- |
| 1 |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | boot 下路由诊断报文丢失testerpresent,ongoing doip/pdur/cantp链路 53F 不在SDB里，和7FF冲突  –-- 详细细节 wiki @ZHAO Wei NA. | NA |
| GAC | NA | SEG error,  硬件分析出UBAT_SENSE_ON 阻抗异常，MCU pin脚短路 https://rb-alm-20-p.de.bosch.com/ccm/web/projects/GAC_IDC#action=com.ibm.team.workitem.viewWorkItem&id=1921616 |
| GWM | NA | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) NA | N.A. WDG SE callback 调用提前 665207: [BYD][PCS04SOP][FUSA] PullBack delay WDG SE 10s \| https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/665207 |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | 改cmake，优化UTF的编译 等测试ok，同步到taiji Alarm 7 – 在咨询英飞凌ing MPU 分析MPU issue 的wiki SM04_Memory Protection 字节没对齐 or 内存越界 |
| Chery | Lessons Learn SCR | CHERYZEEKR ITM Sensor 差值比较复位取消.msg 如果DTS,DTSC 中只有一个sensor 产生了过温或者失温的Alarm ，需要进一步对DTS,DTSC的Result 进行合理性判断， 如果2者的结果相差超过9° 则认为存在故障，需要触发异常（SW ALARM） MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... BM→APP , 出问题时 80+ms zeekr, bm WDG 失效， HSM 拉复位 wiki |

3 同步情况

见 00_Overview

20 Oct 2023

重要问题

|  |  |
| --- | --- |
| 1 |  |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | boot 下路由诊断报文丢失testerpresent,ongoing doip/pdur/cantp链路 | Udrop 40 更新wiki 高通接口获取misr crc |
| GAC | NA | SEG error, U33P_Sense https://rb-alm-20-p.de.bosch.com/ccm/web/projects/GAC_IDC#action=com.ibm.team.workitem.viewWorkItem&id=1921616 |
| GWM | MIC不拾音问题 新增一些功放寄存器相关log的patch： https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/684847 NA | NA safe adc 参考电压 |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) NA | N.A. WDG SE callback 调用提前 665207: [BYD][PCS04SOP][FUSA] PullBack delay WDG SE 10s \| https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/665207 |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | NA zeekr fusa 安波福方案 最后定下来，用博世的方案 改cmake，优化UTF的编译 等测试ok，同步到taiji |
| Chery | Lessons Learn 燃油电阻 实车唤醒起不来问题 | CHERYZEEKR ITM Sensor 差值比较复位取消.msg MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... BM→APP , 出问题时 80+ms zeekr, bm WDG 失效， HSM 拉复位 wiki TC3XX， BM，HSM里是否还有fusa的代码。 没有了，BM下有点HSM相关的代码 做Memory test时，cache需要disable |

3 同步情况

见 00_Overview

13 Oct 2023

重要问题

|  |  |
| --- | --- |
| 1 | 18_因bootloader问题导致现场拆机的LessonLearnt |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | boot 下路由诊断报文丢失testerpresent,ongoing doip/pdur/cantp链路 | Udrop 40 更新wiki 高通接口获取misr crc |
| GAC | NA | SM15 cnt 200 正常唤醒时清safe errmem 循环队列 NA |
| GWM | MIC不拾音问题 新增一些功放寄存器相关log的patch： https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/684847 NA | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) 1101 reset, CLMA错误 hardware reset 需要改成software reset 当前MCU问题（VCU在跟） 注意清retention ram MIC 不拾音 pin短地 , 后续没在复现，先关闭 pullback 问题 休眠前，把port 处理成sleep时的IO配置 eg. IIC → PIO pullback后，并没有改回成IIC. 就出了问题。 GWM->GEELY没有pullback；TC377没有此问题。 | SM20 DTC 优化 N.A. WDG SE |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | LBIST disable /enable india 在修复 A3 /B0 ok, 其他硬件不行 NA |
| Chery | Lessons Learn 燃油电阻 实车唤醒起不来问题 | CHERYZEEKR ITM Sensor 差值比较复位取消.msg MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... BM→APP , 出问题时 80+ms zeekr, bm WDG 失效， HSM 拉复位 wiki |

3 同步情况

见 00_Overview

22 Sep 2023

重要问题

|  |  |
| --- | --- |
| 1 | 18_因bootloader问题导致现场拆机的LessonLearnt |

各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | N.A | Udrop 40 更新wiki 高通接口获取misr crc |
| GAC | NA | SM15 cnt 200 正常唤醒时清safe errmem 循环队列 NA |
| GWM | MIC不拾音问题 | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) 1101 reset, CLMA错误 hardware reset 需要改成software reset 当前MCU问题（VCU在跟） 注意清retention ram MIC 不拾音 pin短地 pullback 问题 | SM20 DTC 优化 N.A. WDG SE |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | LBIST disable /enable india 在修复 A3 /B0 ok, 其他硬件不行 NA |
| Chery | 燃油电阻 实车唤醒起不来问题 | CHERYZEEKR ITM Sensor 差值比较复位取消.msg MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... BM→APP , 出问题时 80+ms zeekr, bm WDG 失效， HSM 拉复位 wiki |

3 同步情况

见 00_Overview

08 Sep 2023

1重要问题

|  |  |
| --- | --- |
| 1 |  |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | N.A | Udrop 40 更新wiki 高通接口获取misr crc |
| GAC | NA | SM15 cnt 200 正常唤醒时清safe errmem 循环队列 NA |
| GWM | MIC不拾音问题 | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) 1101 reset, CLMA错误 hardware reset 需要改成software reset 当前MCU问题（VCU在跟） 注意清retention ram MIC 不拾音 pin短地 | SM20 DTC 优化 N.A. WDG SE |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | LBIST disable /enable india 在修复 A3 /B0 ok, 其他硬件不行 NA |
| Chery | 燃油电阻 实车唤醒起不来问题 | CHERYZEEKR ITM Sensor 差值比较复位取消.msg MCU初始化前，WDG触发->exception，performance_reset-> DET→performance_reset →DET... BM→APP , 出问题时 80+ms zeekr, bm WDG 失效， HSM 拉复位 wiki |

3 同步情况

见 00_Overview

04 Aug 2023

1重要问题

|  |  |
| --- | --- |
| 1 |  |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | N.A | Reg RH850 Safe ADC compensation reference voltage change.msg |
| GAC | N.A. IIC问题分享？ sw + hw + chip 引出的问题 （20089芯片） IIC读RTC等设备时，要判断外设3.3v电源是否上电—--发封邮件 @gongguan RE AutosarRH850 平台 I2C 总线问题总结 - - base on GAC A8E 黑屏问题.msg NA | SM15 cnt 200 正常唤醒时清safe errmem 循环队列 NA |
| GWM | NA | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) 1101 reset, CLMA错误 hardware reset 需要改成software reset 当前MCU问题（VCU在跟） 注意清retention ram NA | SM20 DTC 优化 N.A. WDG SE |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | LBIST disable /enable india 在修复 MPU 18个 Zeekr MPU一直enable，偶尔报MPU问题，立即就修掉了 NA |
| Chery | Pcm624_lic.c RX TX SEQ　NUM chery项目内的，已修改，测试ing DLT 被狗咬 DltIf_UartReceive rx_MsgCounter U16 ->U8 | CHERYZEEKR ITM Sensor 差值比较复位取消.msg N.A. |

3 同步情况

见 00_Overview

28 Jul 2023

1重要问题

|  |  |
| --- | --- |
| 1 |  |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | ErrorHook 跟Vector发了邮件 加了ErrorHook的log（ https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1808774 ） LIU Dezhi (XC-CP/ESW2-CN) 单独创建个 wiki N.A | NA. SM52 校验纯黑图片的问题，CRC==0 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/647570 BYD需要改，新平台没这个问题 NA |
| GAC | N.A. IIC问题分享？ sw + hw + chip 引出的问题 （20089芯片） IIC读RTC等设备时，要判断外设3.3v电源是否上电—--发封邮件 @gongguan NA | coverity risk 3 SM15 cnt 200 正常唤醒时清safe errmem 循环队列 NA |
| GWM | info: scc 和soc chn号相同但不连续，但还能正常通信 有的chn用了流控；大部分chn没用流控 参考 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/639908/2/VipIncRouter/Service.VipIncRouter/src/VipIncRouter.c#241 ，关注 VipIncRouter.c NA | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) 1101 reset, CLMA错误 hardware reset 需要改成software reset 当前MCU问题（VCU在跟） 注意清retention ram | SM20 DTC 优化 N.A. WDG SE |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | LBIST disable /enable india 在修复 MPU 18个 |
| Chery | Pcm624_lic.c RX TX SEQ　NUM chery项目内的，已修改，测试ing | CHERYZEEKR ITM Sensor 差值比较复位取消.msg RAM ECC地址定位方法 04_SMs Development Information ROM ECC enable WDG 中断使能晚，200ms自动喂 已修复（平台的） N.A. |

3 同步情况

见 00_Overview

21 Jul 2023

1重要问题

|  |  |
| --- | --- |
| 1 |  |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | ErrorHook 跟Vector发了邮件 加了ErrorHook的log（ https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1808774 ） LIU Dezhi (XC-CP/ESW2-CN) 单独创建个 wiki N.A | NA. SM52 校验纯黑图片的问题，CRC==0 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/647570 BYD需要改，新平台没这个问题 NA |
| GAC | N.A. IIC问题分享？ sw + hw + chip 引出的问题 （20089芯片） IIC读RTC等设备时，要判断外设3.3v电源是否上电—--发封邮件 @gongguan NA | coverity risk 3 SM15 cnt 200 正常唤醒时清safe errmem 循环队列 NA |
| GWM | info: scc 和soc chn号相同但不连续，但还能正常通信 有的chn用了流控；大部分chn没用流控 参考 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/639908/2/VipIncRouter/Service.VipIncRouter/src/VipIncRouter.c#241 ，关注 VipIncRouter.c NA | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) 1101 reset, CLMA错误 hardware reset 需要改成software reset 当前MCU问题（VCU在跟） 注意清retention ram | SM20 DTC 优化 N.A. WDG SE |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | LBIST disable /enable india 在修复 MPU 18个 |
| Chery | Pcm624_lic.c RX TX SEQ　NUM chery项目内的，已修改，测试ing | CHERYZEEKR ITM Sensor 差值比较复位取消.msg RAM ECC地址定位方法 04_SMs Development Information ROM ECC enable WDG 中断使能晚，200ms自动喂 已修复（平台的） N.A. |

3 同步情况

见 00_Overview

14 Jul 2023

1重要问题

|  |  |
| --- | --- |
| 1 |  |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | ErrorHook 跟Vector发了邮件 加了ErrorHook的log（ https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1808774 ） LIU Dezhi (XC-CP/ESW2-CN) 单独创建个 wiki | NA. |
| GAC | N.A. 经典问题分享？ | coverity risk 3 SM15 cnt 200 正常唤醒时清safe errmem 循环队列 |
| GWM | 多个SWC共同发同一个事件报文， GWM PPT info: scc 和soc chn号相同但不连续，但还能正常通信 有的chn用了流控；大部分chn没用流控 | NA |
| BYD | 休眠时log打不出来的问题 UXX_PERION wiki ZHAO Joanna (XC-CP/ESW2-CN) | SM20 DTC 优化 |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | LBIST disable /enable india 在修复 |
| Chery | Pcm624_lic.c RX TX SEQ　NUM chery项目内的，已修改，测试ing | CHERYZEEKR ITM Sensor 差值比较复位取消.msg RAM ECC地址定位方法 ROM ECC enable WDG 中断使能晚，200ms自动喂 已修复（平台的） |

3 同步情况

见 00_Overview

07 Jul 2023

1重要问题

|  |  |
| --- | --- |
| 1 |  |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | ErrorHook 跟Vector发了邮件 加了ErrorHook的log（ https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1808774 ） LIU Dezhi (XC-CP/ESW2-CN) 单独创建个 wiki | 亏电进recovery，退出方案 从中控屏上软按键触发退出，SOC 升级、LCM在主导, 升级组做完在测试ing SM21 safeTemperature reset 的counter（不再贡献到25次） https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/626118 |
| GAC | N.A. 6424 AMP 产线DTC误报,  带电操作，报对地短路故障 暂定产线操作问题 | coverity risk 3 SM15 cnt 200 正常唤醒时清safe errmem 循环队列 |
| GWM | 多个SWC共同发同一个事件报文， GWM PPT info: scc 和soc chn号不同，但还能正常通信 | NA |
| BYD | 因异常进bootloader，但soc不能进recovery → 需要先拉pin，再给soc上电 wiki scc 先给soc上电，再约100ms拉pin 因为 soc优化了启动过程 休眠时log打不出来的问题 UXX_PERION wiki | SM20 DTC 优化 |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | pFlash CRC check；mcu check 会reset pFlash CRC check， Chery 已解决 LBIST disable /enable india 在修复 |
| Chery | IIC 异步，传入临时变量buffer Lessons Learn Pcm624_lic.c RX TX SEQ　NUM | CHERYZEEKR ITM Sensor 差值比较复位取消.msg RAM ECC地址定位方法 ROM ECC enable WDG 中断使能晚，200ms自动喂 已修复（平台的） |

3 同步情况

见 00_Overview

30 Jun 2023

1重要问题

|  |  |
| --- | --- |
| 1 | RE DLT SoC存储SCC DLT Log丢失问题调查分析.msg |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | sleep 流程中，其他唤醒源唤醒DHU STR suspending时，监控信号往前放. ErrorHook 跟Vector发了邮件 加了ErrorHook的log（ https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1808774 ） LIU Dezhi (XC-CP/ESW2-CN) 单独创建个wiki | 亏电进recovery，退出方案 从中控屏上软按键触发退出，SOC 升级、LCM在主导, 升级组做完在测试ing U18S_CPU/U18S_WIFI，在STR退出的时候，经常不对 BSP在主导，U18S_CPU ok, U18S_WIFI nok 是否同步金老师分享的 低电压下ppt [VCU]VIP_Only_Reset+UnderVoltage_Reset_Handling.pptx 同步CVM test LIU Dezhi (XC-CP/ESW2-CN) 更新到wiki上 两个地方 udrop 40 初始化的时候 https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1785340 SM21 safeTemperature reset 的counter（不再贡献到25次） https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/626118 |
| GAC | N.A. 6424 AMP 产线DTC误报,  带电操作，报对地短路故障 暂定产线操作问题 | bootloader fusa log字节长度问题 11_add log in bootloader for anaylsis issue 进STR，SM19会reset(只有GAC fusa 有） 延时2min；slm 起改成 startup.sh起 N.A. |
| GWM | 多个SWC共同发同一个事件报文， GWM PPT BYD也有类似的问题，TODO：是否建个topic，另外讨论 LIU Dezhi (XC-CP/ESW2-CN) N.A | 进recovery，退出方案 ，SOC LCM主导，已验证ok NA |
| BYD | 因异常进bootloader，但soc不能进recovery → 需要先拉pin，再给soc上电 wiki scc 先给soc上电，再约100ms拉pin 因为 soc优化了启动过程 | N.A |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | pFlash CRC check；mcu check 会reset pFlash CRC check， Chery 已解决 LBIST disable |
| Chery | IIC 异步，传入临时变量buffer Lessons Learn | CHERYZEEKR ITM Sensor 差值比较复位取消.msg RAM ECC地址定位方法 ROM ECC enable |

3 同步情况

见 00_Overview

16 Jun 2023

1重要问题

|  |  |
| --- | --- |
| 1 |  |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | sleep 流程中，其他唤醒源唤醒DHU STR suspending时，监控信号往前放. ErrorHook 跟Vector发了邮件 | 亏电进recovery，退出方案 从中控屏上软按键触发退出，SOC 升级、LCM在主导, 在跟geely要图片 U18S_CPU/U18S_WIFI，在STR退出的时候，经常不对 BSP在主导，U18S_CPU ok, U18S_WIFI nok GEELY: SM52 长期方案 优化 是否同步金老师分享的 低电压下ppt [VCU]VIP_Only_Reset+UnderVoltage_Reset_Handling.pptx 同步CVM test udrop 40 两个地方 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch_mcal/+/621383 |
| GAC | N.A. 6424 AMP 产线DTC误报,  带电操作，报对地短路故障 暂定产线操作问题 | bootloader fusa log字节长度问题 11_add log in bootloader for anaylsis issue 进STR，SM19会reset(只有GAC fusa 有） 延时2min；slm 起改成 startup.sh起 N.A. |
| GWM | 多个SWC共同发同一个事件报文， GWM PPT BYD也有类似的问题，TODO：是否建个topic，另外讨论 LIU Dezhi (XC-CP/ESW2-CN) N.A | 进recovery，退出方案 ，SOC LCM主导，已验证ok NA |
| BYD | 因异常进bootloader，但soc不能进recovery → 需要先拉pin，再给soc上电 wiki scc 先给soc上电，再约100ms拉pin 因为 soc优化了启动过程 | N.A |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | pFlash CRC check；mcu check 会reset pFlash CRC check， Chery 已解决 LBIST disable |
| Chery | IIC 异步，传入临时变量buffer Lessons Learn | N.A. |

3 同步情况

见 00_Overview

09 Jun 2023

1重要问题

|  |  |
| --- | --- |
| 1 | 软件兼容性问题 不能变更的模块，提前开发 BM OptionByte/UCB autosar/fusa模块不兼容的，提前跟TPM沟通 Security 等其他模块有兼容性问题的，需要改时，拉TPM沟通 |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | sleep 流程中，其他唤醒源唤醒DHU STR suspending时，监控信号往前放. | 亏电进recovery，退出方案 从中控屏上软按键触发退出，SOC 升级、LCM在主导, 在跟geely要图片 U18S_CPU/U18S_WIFI，在STR退出的时候，经常不对 BSP在主导，U18S_CPU ok, U18S_WIFI nok GEELY: SM52 长期方案 优化 是否同步金老师分享的 低电压下ppt [VCU]VIP_Only_Reset+UnderVoltage_Reset_Handling.pptx |
| GAC | N.A. 6424 AMP 产线DTC误报,  带电操作，报对地短路故障 | bootloader fusa log字节长度问题 11_add log in bootloader for anaylsis issue 进STR，SM19会reset(只有GAC fusa 有） 延时2min；slm 起改成 startup.sh起 |
| GWM | 多个SWC共同发同一个事件报文， GWM PPT BYD也有类似的问题，TODO：是否建个topic，另外讨论 LIU Dezhi (XC-CP/ESW2-CN) N.A | 进recovery，退出方案 ，SOC LCM主导，已验证ok |
| BYD | 因异常进bootloader，但soc不能进recovery → 需要先拉pin，再给soc上电 wiki scc 先给soc上电，再约100ms拉pin 因为 soc优化了启动过程 | N.A |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | pFlash CRC check；mcu check 会reset pFlash CRC check， Chery 已解决 LBIST disable |
| Chery | IIC 异步，传入临时变量buffer | N.A. |

3 同步情况

见 00_Overview

02 Jun 2023

1重要问题

|  |  |
| --- | --- |
| 1 | 大家提交代码跟fusa相关的改动的commit里记得加上[fusa][SMXX] .... ,比如[fusa][sm52] add gear logic 方便测试同学去changelog上抓fusa的改动，方便他们同步测试的case |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | 冷启动/退出STR时三屏黑，ongoing 方向：SOC STR进入失败 , soc 在跟 sdb版本不匹配？ → 测试手法问题 sleep 流程中，其他唤醒源唤醒DHU | 亏电进recovery，退出方案 从中控屏上软按键触发退出，SOC 升级、LCM在主导，目前没进展 U18S_CPU/U18S_WIFI，在STR退出的时候，经常不对 BSP在主导，U18S_CPU ok, U18S_WIFI nok |
| GAC | 客户反馈：can 流控帧，连续两帧有问题（第一帧BS=1) 跟vector沟通ing → vector不支持，BS=1没有意义。不认为是个问题 | bootloader fusa log字节长度问题 11_add log in bootloader for anaylsis issue 触发Udrop40问题 做STR时，把整车电源拉到4V3. 硬件在主导 进STR，SM19会reset |
| GWM | 考虑，bootloader下 SOC卡住，解决方法。暂不实施 多个SWC共同发同一个事件报文， GWM PPT BYD也有类似的问题，TODO：是否建个topic，另外讨论 LIU Dezhi (XC-CP/ESW2-CN) | 仪表黑屏，花屏 –> 怀疑 display diag 内存泄漏 没再复现 进recovery，退出方案 ，SOC LCM主导，已验证ok 其他项目考虑是否同步 |
| BYD | 11_add log in bootloader for anaylsis issue | NA. |

|   |   |   |
| --- | --- | --- |
| Zeekr | Lesson Learn - Zeekr Autosar | pFlash CRC check；mcu check 会reset pFlash CRC check， Chery 已解决 |
| Chery | N.A | N.A. |

3 同步情况

见 00_Overview

26 May 2023

1重要问题

|  |  |
| --- | --- |
| 1 | N.A. |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | 冷启动/退出STR时三屏黑，ongoing 方向：SOC STR进入失败 , soc 在跟 sdb版本不匹配？ → 测试手法问题 sleep 流程中，其他唤醒源唤醒DHU | 亏电进recovery，退出方案 从中控屏上软按键触发退出，SOC 升级、LCM在主导 U18S_CPU/U18S_WIFI，在STR退出的时候，经常不对 BSP在主导 |
| GAC | 客户反馈：can 流控帧，连续两帧有问题（第一帧BS=1) 跟vector沟通ing | bootloader fusa log字节长度问题 11_add log in bootloader for anaylsis issue 触发Udrop40问题 做STR时，把整车电源拉到4V3. 硬件在主导 |
| GWM | 考虑，bootloader下 SOC卡住，解决方法。暂不实施 多个SWC共同发同一个事件报文， GWM PPT BYD也有类似的问题，TODO：是否建个topic，另外讨论 | 仪表黑屏，花屏 –> 怀疑 display diag 内存泄漏 没再复现 N.A. |
| BYD | 11_add log in bootloader for anaylsis issue NA | N.A. |

|   |   |   |
| --- | --- | --- |
| Zeekr | N.A | N.A. |
| Chery | N.A | N.A. |

3 同步情况

见 00_Overview

19 May 2023

1 重要问题

|  |  |
| --- | --- |
| 1 | 如果有个新需求，需要A B模块同时修改 最优做法： 各模块owner改各自的模块，改完后联调测试 少许情况，因为种种原因：A owner 改A B模块的代码，建议还是加B模块的Owner review一下 |

2 各项目本周Issue

|  | Autosar FO | Fusa FO |
| --- | --- | --- |
| GEELY | 冷启动/退出STR时三屏黑，ongoing 方向：SOC STR进入失败 , soc 在跟 | 亏电进recovery，退出方案 （同 GWM 问题） |
| GAC |  | bootloader fusa log字节长度问题 11_add log in bootloader for anaylsis issue 触发Udrop问题 |
| GWM | bootloader下 SOC卡住，解决方法 | 仪表黑屏，花屏 –> 怀疑 display diag 内存泄漏 |
| BYD | 11_add log in bootloader for anaylsis issue |  |

3 同步情况

见 00_Overview

12 May 2023

1 重要问题

chery code Commit Lesson Learn 10_chery-idc code commit lesson learn

2 各项目本周issue

GEELY ：

- 冷启动/退出STR时三屏黑，ongoing
- 09_bootloader下数组越界

GAC:

- bootloader fusa log字节长度问题
- Udrop 40 问题

GWM:

- NA
- bootloader下 SOC卡住，解决方法

BYD：

- 100套主题，SM52 SCC侧的代码优化问题，约个会 – LIU Dezhi (XC-CP/ESW2-CN)
- 接错线，会导致进bootloader

Chery：

- task名称分类问题，Chery 出guidline

3 同步情况

- BYD SCC 25次进bootloader后没有fusa log的一个原因 user-0e05a 识别进bootloader的原因 user-2cdd2
- 09_bootloader下数组越界 GEELY

05 May 2023

GEELY ：

- 冷启动/退出STR时三屏黑，ongoing

GAC:

- bootloader fusa log字节长度问题

GWM:

- NA

BYD：

- 100套主题，SM52 SCC侧的代码优化问题，约个会 – LIU Dezhi (XC-CP/ESW2-CN)

Chery：

- task名称分类问题，Chery 出guidline

28 Apr 2023

![](../../../_images/rh850%20common%20issues%20meeting/image-2023-4-28_17-19-21.png)

- SCC 25次进bootloader后没有fusa log的一个原因

21 Apr 2023

GEELY:

[geely] Key Points for Implementation and bug analysis of LIN Sleep Command requirements

台架播放声音出现了reset，最后查下来是因为，供电电源设置了电流限制，功率达不到，触发了Udrop40. link

GWM:

4s店 低电压进recovery

- LCM加reset原因，打印是否是fusa导致的reset →covered by 11_add log in bootloader for anaylsis issue

- BYD发现了HSM里某个变量没有初始化，导致2bit ECC的问题，其他项目也可能存在该变量没初始化的问题。 –
- bootloader 里一次性打印字符太多，会卡住，原因是 fbl_tracestring（）会产生数组越界，各项目check 09_bootloader下数组越界
- SM12 做了些改动，SocState ==Normal,等修改，需要拉会，跟fusa fo，系统，讨论是否要同步到其他项目，做出平台化需求。
- GWM项目上fusa log 存NVM评估 ongoing
- GWM Mic 无声偶发问题 LIU Jiqing (ETAS-ECM/XSF-CN)
- GAC HW clock问题 ongoing user-aa45a
- 同步 John 分享的VCU 低电压 PPT上的问题 – Autosar/Fusa FOs

14 Apr 2023

- BYD发现了HSM里某个变量没有初始化，导致2bit ECC的问题，其他项目也可能存在该变量没初始化的问题。 – LIU Dezhi (XC-CP/ESW2-CN) 邮件 XU Zhiyuan (XC/ESS4-CN) ，是否需要同步其他项目
- GWM项目上fusa log 存NVM评估 ongoing
- GWM Mic 无声偶发问题
- GAC HW clock问题 ongoing
- VCU 低电压9v-4v--12v下IIC  F1KH (8M ROM）问题/ F1KM(4M ROM)没有问题 ongoing
- 同步 John 分享的VCU 低电压 PPT上的问题 – Autosar/Fusa FOs

31 Mar 2023

MOM:

1 geely 产线报fusa DTC，HW clock问题（最近批量报，一天约10台车）。 Jira link . 产线流程问题，软件暂不做处理。

- 经排查这批车3月初生产完，拔了电池放置在车库约20天。之前正常生产时零星会报hw clock问题。
- 目前的现象：fusa hw clock问题跟蓄电池电压有很大关系 。这批车因geely生产流程的原因，他们特殊处理。

2 can trcv 自研topic ,单独拉会讨论 – @zhao wei

3 GWM 产线问题，kefeng跟congfei已经做了很多优化， PPT link .  整理到wiki inbox目录下 &&分享下patch  – JI Congfei (BCSC/ENG1)

- 关alive timeout monitor
- 跟security的一起的问题
- SOC OC的问题  – GAC也存在， 是否要同步修改   – user-aa45a
- 等等

4 fusa 新平台，收集rh850平台各项目fusa在soc的不同点，yanqiang再收集一下  – ZHAO Yanqiang (XC-CP/ESW2-CN)

- 例如，geely sm15 log 截图,系统loading等信息；增加了SM monitor进程等
- gac AC54 用CAN传TT 状态给屏幕 等

5 BYD USB升级后时起时不起→无法启动。 正在调查ing

24 Mar 2023

2023年3月24日 MOM:

这周有几类问题

1. GAC低压下Reset 25次进Bootloader的问题
2. BYD发现了HSM里某个变量没有初始化，导致2bit ECC的问题，其他项目也可能存在该变量没初始化的问题。
3. GWM项目产线上reset问题，产线刷新SecOC密钥导致的reset
4. GEELY 实车启动1 min左右时，触发Alive Timeout WDG reset, 还在调查中，建议各项目定周期做RTMO    --- GWM/GEELY/GAC/BYD AutoSar FO
5. Vector CAN Signal 超过６Byte后，会出现字节序的bug, Liu Jiqing 分享了 GWM Signals Over 48 Bits Set Order Issue_converted.pptx , Thanks ， Jiqing!

Info:

VCU解决了IPG的问题，Liu Dezhi在邮件沟通ing.
