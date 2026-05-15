# 18_因bootloader问题导致现场拆机的LessonLearnt

> Source: /spaces/CARSFW/pages/3468510280/18_%E5%9B%A0bootloader%E9%97%AE%E9%A2%98%E5%AF%BC%E8%87%B4%E7%8E%B0%E5%9C%BA%E6%8B%86%E6%9C%BA%E7%9A%84LessonLearnt
> Last modified: 2023-10-20T07:08:09.000+02:00

---

| Version | Detail | Date | Author | comment |
| --- | --- | --- | --- | --- |
| V0.1 | first version | 2023.09.21 | liu dezhi | initial template & 增加5复盘总结 初步描述 |
|  |  |  |  |  |
|  |  |  |  |  |

## 1. 问题背景

Chery T1P换了新硬件，装车后发现升级功能不能用，导致需要去现场拆车线刷。

## 2. 问题分析

user-0e05a 分析总结了此次的原因, 如下：

RE CHERY TIP9.15 升级问题分析与Lesson Learn .msg

![](../../../_images/18_%E5%9B%A0bootloader%E9%97%AE%E9%A2%98%E5%AF%BC%E8%87%B4%E7%8E%B0%E5%9C%BA%E6%8B%86%E6%9C%BA%E7%9A%84LessonLearnt/image-2023-9-21_10-14-8.png)

## 3. 解决办法

MCU侧：软件出了优化方案，不再读pin状态（CPU_RESET_OUT_B_3V3）

![](../../../_images/18_%E5%9B%A0bootloader%E9%97%AE%E9%A2%98%E5%AF%BC%E8%87%B4%E7%8E%B0%E5%9C%BA%E6%8B%86%E6%9C%BA%E7%9A%84LessonLearnt/image-2023-9-22_15-40-20.png)

## 4. 解决状态

- Chery所有分支都已同步
- zeekr已同步

## 5. 复盘 && 总结

扩展一下，如何避免现场拆机？

- 之前的项目，有哪些原因导致的去现场拆机的？
- 以后如何避免现场拆机

初步总结一下：

当发生以下case时：

1. 新sample
2. 修改BM/修改BL
3. 修改Memory Layout/存FLASH的数据（UCB）

需要：

- 需要FO重点关注
- 如果硬件改动，需要拉LCM&&BL同事review 硬件的changelist.
- 需要丰富的测试（旧版本，新版本必须是服务器上生成的版本）

1. 休眠唤醒 升级 旧版本升级到新版本 新版本自升级
