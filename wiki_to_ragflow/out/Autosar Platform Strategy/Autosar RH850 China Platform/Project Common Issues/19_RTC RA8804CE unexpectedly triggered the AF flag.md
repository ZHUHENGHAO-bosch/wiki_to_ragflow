# 19_RTC RA8804CE unexpectedly triggered the AF flag

> Source: /spaces/CARSFW/pages/4933326656/19_RTC+RA8804CE+unexpectedly+triggered+the+AF+flag
> Last modified: 2024-10-29T07:22:07.000+01:00

---

## 该问题由Chery项目发现，copy一份在这里做汇总，最新版请参考chery原版，链接：

## RTC RA8804CE unexpectedly triggered the AF flag

### 问题现象

JIRA问题链接： https://jira-shzj.auto-link.com.cn/browse/CHER-78745

【T1K国际】【中控】【电源管理】【实车】【客户问题】str30h后未自动关闭， 主机静态电流4.5mA左右（3/20）

### 复现操作

1. 客户实车连续两次测试30h从STR（4.5mA）退出进入深度休眠模式（0.5mA）失败，工作电流始终保持在4.5mA；
2. 故障件返回办公室后多次测试STR 5min，问题不复现；
3. 按照实际需求设置30h的STR用电脑抓DLT，最终复现问题；
4. 复现问题时，DLT记录到RTC返回的唤醒reason=5，如图1，该含义是TF=1&&AF=1，Fixed-Cycle Timer（TF: Timer Flag）和Alarm（AF： Alarm Flag）中断同时触发；
5. 分析LCM代码，发现对reason=5的判定，没有逻辑，导致了SCC LCM没有满足拉起SOC条件，直接走了SCC shut down，这也与客户问题现象吻合；
6. 另外，实际代码中用到的唤醒类型是Fixed-Cycle Timer，没有启用Alarm唤醒，这与期望不符；

![](../../../_images/19_RTC%20RA8804CE%20unexpectedly%20triggered%20the%20AF%20flag/image-2024-10-17_16-11-50.png)

图1

### 问题分析

针对上述步骤中5/6，得到了问题产生的根本原因有两个：

#### 问题点1：LCM没有判断reason=5的情况？

目前看LCM代码对于reason=5没有做逻辑，当5的情况出现时，SCC无动作，直到SCC shut down，实际上需要把Fixed-Cycle Timer和Alarm中断标志同时置位后发给SOC作进一步判断，并拉起SOC，

如下图3，左边是修复前，右边修复后：

![](../../../_images/19_RTC%20RA8804CE%20unexpectedly%20triggered%20the%20AF%20flag/image-2024-10-10_10-10-26.png)

图3

#### 问题点2：软件没有用Alarm中断，为何能读到AF标志？

图4是芯片厂家反馈的信息：

![](../../../_images/19_RTC%20RA8804CE%20unexpectedly%20triggered%20the%20AF%20flag/image-2024-10-10_10-16-8.png)

图4

1. 厂家反馈 图5 框图部分寄存器08~0A冷启动是随机数，因此当STR 30h内走时与随机数恰巧匹配，AF标志位会被置位，但因为AIE=0，没有产生中断；
2. 同时部分RTC芯片因为电容/工艺原因随机数不是真随机，会出现部分数值高概率出现的情况；
3. 第二点也是能够解释为什么客户反馈故障件能够高概率复现；
4. 目前随机数匹配导致的AF置位问题是唯一怀疑的可能原因，厂家也在针对这个芯片做上下电测试，读随机值分析；

### ROOT CAUSE

![](../../../_images/19_RTC%20RA8804CE%20unexpectedly%20triggered%20the%20AF%20flag/image-2024-10-17_16-5-25.png)

图5

![](../../../_images/19_RTC%20RA8804CE%20unexpectedly%20triggered%20the%20AF%20flag/image-2024-10-17_17-38-29.png)

图6

- 16台机器上电读ALARM寄存器数据结果，如图5
- LCM逻辑判定错误，如图6；

### 解决方案

![](../../../_images/19_RTC%20RA8804CE%20unexpectedly%20triggered%20the%20AF%20flag/image-2024-10-17_17-42-10.png)

图7

修复方案如图7所示：

#### 修复问题点1：增加LCM判断reason=5的情况

如图3所示修复，链接： https://rbcm-gerrit.de.bosch.com/q/topic:%22enter_str_fail_for_sop13%22

#### 修复问题点2：RTC驱动：reason判定条件增加，冷启动初始化设置alarm为无效值

1. 冷启动上电时，RTC驱动设置寄存器08~0A数值为0，正常时间不会出现DAY/WEEK为0状况，因此alarm永远匹配不上，AF标志不会置位；
2. reason判定条件更新：

- RTC_WAKEUP_FIXED_CYCLE（4）：(TIE==1) && (TE==1) && (TF==1)
- RTC_WAKEUP_ALARM（3）：(AIE==1) &&(AF==1)
- RTC_WAKEUP_ALARM_AND_FIXED_CYCLE（5）：以上条件全部满足

修复链接： https://rbcm-gerrit.de.bosch.com/q/topic:%22enter_str_fail_for_sop13%22

## 结束
