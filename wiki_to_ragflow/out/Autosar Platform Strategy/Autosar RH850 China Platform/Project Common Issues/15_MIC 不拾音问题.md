# 15_MIC 不拾音问题

> Source: /spaces/CARSFW/pages/3422484123/15_MIC+%E4%B8%8D%E6%8B%BE%E9%9F%B3%E9%97%AE%E9%A2%98
> Last modified: 2023-09-21T04:48:56.000+02:00

---

| Version | Detail | Date | Author | comment |
| --- | --- | --- | --- | --- |
| V0.1 | first version | 2023.09.08 | liu dezhi | initial template & 增加问题背景邮件 |
| V0.2 | 添加Chery T1J项目分析 | 2023.09.21 | Ji Hongguang |  |
|  |  |  |  |  |

## 问题背景

1. FW 关于 GWM35-B07GWMB-1584 预约升级完成之后，麦克风无法收音，重启后恢复 的问题咨询.msg

2. Chery IDC T1J项目实车报告偶现启动完成后MIC不拾音问题

GWM 遇到

Chery 遇到

BYD 遇到

## CHERY IDC T1J遇到的问题

### 问题1：状态机Config读芯片版本号失败，导致状态停留在这个函数没有继续向下进一步初始化

![](../../../_images/15_MIC%20%E4%B8%8D%E6%8B%BE%E9%9F%B3%E9%97%AE%E9%A2%98/image-2023-9-21_10-28-21.png)

#### 1A.问题分析

这个是偶现问题没有找到根本原因，但是延长Rst状态机的等待时间可以解决这个问题，同时我们咨询德器FAE，不建议读芯片版本号，手册里也没有体现这个寄存器的任何信息。

#### 1B.解决办法

- 延长Rst状态机等待时间至2s；
- 删除该状态机获取芯片版本号的操作，直接使用B0版本的芯片配置；

### 问题2：上电读及运行过程中ASI_STS寄存器数据是0x30或0x0，导致芯片工作异常，无法拾音

#### 2A.问题分析

正常运行时，ASI_STS寄存器数值是0x48，当出现无法拾音时，数值变成了0x30或0的情况。与GAC项目了解，ASI_STS寄存器状态受SOC输出给PCM时钟的影响，如果SOC输出的时钟时间太慢，会导致SCC初始化PCM失败，ASI_STS异常。

#### 2B.解决办法

- Rst状态机等待时间至2s；
- 增加ClkChk状态机等待超时时间，一旦检测不通过时间过长，则状态机进入init重新启动芯片；
- 运行过程中，状态机会周期从Run>AsiChk>ClkChk调用，一旦有异常会进入init重新启动芯片；

解决状态

| Affected Project | FixStatus | RTC/Gerrit Linkage |
| --- | --- | --- |
| GWM V3.5 |  |  |
| GEELY |  |  |
| GAC |  |  |
| BYD |  |  |
| Chery |  |  |
