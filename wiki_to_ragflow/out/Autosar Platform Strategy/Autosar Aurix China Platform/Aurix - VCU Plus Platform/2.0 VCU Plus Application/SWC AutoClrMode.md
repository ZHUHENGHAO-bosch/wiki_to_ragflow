# SWC AutoClrMode

> Source: /spaces/CARSFW/pages/6920786330/SWC+AutoClrMode
> Last modified: 2026-03-11T08:55:58.000+01:00

---

目录： Autosar/Application/GM/gmGemIPCSwc/ImpArch/AutoClrMode AutoClrMode.c 主流程与状态机实现。 配置同步、时间窗口判断、定时器轮询 AutoClrMode.h 定时器结构体、状态常量定义 AutoClrMode_ar.h RTE 读写/Timer Service 的适配层（大量 LOCAL_INLINE ） AutoClrMode_Variables.c RTE 读写/Timer Service 的适配层（大量 LOCAL_INLINE ） AutoClrMode_Variables.h 模块全局变量与跨文件共享状态

## I. 这个 SWC 是做什么的

AutoClrMode 是 “自清洁模式可用性判定与触发协调” 模块，核心职责：

1. 读取配置参数（SOC 下发 + 有效性）。 2. 根据车辆状态和时间条件判断“是否允许自清洁”。 3. 通过状态机在 `Init -> CheckFeedback -> Active/DeActive` 之间切换。 4. 通过 RTE 输出当前可用状态和配置回写值。 5. 管理一个防抖/等待反馈定时器（3min）。

## II. 总览

![](../../../../_images/SWC%20AutoClrMode/image-2026-3-11_15-8-3.png)

## III. 状态机

![](../../../../_images/SWC%20AutoClrMode/image-2026-3-11_15-23-52.png)

-AutoClrMode_State_Init：等待所有触发条件满足。 -AutoClrMode_State_CheckFeedback：对外置 `AVAILABLE`，等待 VCU 反馈或超时。 -AutoClrMode_State_Active：记录一次成功活动，然后立即进入 DeActive（代码无 `break`，有意穿透）。 -AutoClrMode_State_DeActive：收尾，状态置不可用，取消定时器，回到 Init。

## IV. AutoClrMode.c 函数解析

#### AutoClrMode_Init(void)

- 功能：初始化运行期镜像参数（从 RTE 拉取一次）并 uploadCfgParam(), 同步配置
- 输出：更新全局变量（ AutClnMd* 、 VCUClnMdFdk ）并通过 SetAutClnMd*CurVal 回写。

#### AutoClrMode_Runnable(void)

- 主函数
- 关键步骤：
- 输出： SetAutClnMdSts() 、日志、定时器状态。

#### CheckCulDur(void)

- 功能：检查持续唤醒时长是否达到阈值
- 输入： AutoClrModeWakeup ， AutClnMdCulDurCurVal
- 输出： true/false
- 细节：

#### CheckExePer(void)

- 功能：检查当前时刻是否落在允许执行时间段
- 输入：UTC 时间有效位 + UTC 时间值 + AutClnMdStrTimCurVal + AutClnMdExePerCurVal
- 输出： true/false
- 细节：优先走 UTC 信号读取（ USE_UTF_TIME ）

#### CheckIntTim(void)

- 功能：检查“距离上一次活动是否超过间隔阈值”
- 输入： Active_AutClnMd_PreTimeMS 、 AutClnMdIntTimCurVal
- 输出： true/false
- 细节：用当前时基 GetHWIO_t_Current() 与上次活动时基比较

#### uploadCfgParam(void)

- 功能：将本地 *CurVal 持续写回 RTE
- 输出： SetAutClnMdCulDurCurVal 等 5 个写口
- 细节：每隔约 1000 次循环打一组日志

#### UpdateCfgParam(void)

- 功能：读取新配置与有效性，调用 UpdateOneCfg 更新缓存
- 输入：5 组 GetAutClnMd* + GetAutClnMd*Avl
- 输出：更新 AutClnMd* 和对应 *CurVal

#### UpdateOneCfg(uint8 avl, uint8 temp, uint8* cfg, uint8* curVal)

- 功能：单参数更新器
- 策略：仅当 avl == AUTCLN_CFG_AVL_AVAILABLE 且值发生变化时写入

#### TickAutoClrModeTimers(void)

- 功能：轮询模块内部 timer 队列
- 输出：到期后置位 AutoClrMode_DRVIND_TIMER_HAS_EXPIRED
- 细节：只置位，不直接驱动状态机，状态机在 Runnable 中读取

#### HMI_AutoClrMode_StartTimer(AutoTimerIndx_t, uint16)

- 功能：启动定时器并写入 100ms 单位时长
- 输出：设置 TIMER_SET ，清 HAS_EXPIRED

#### HMI_AutoClrMode_TimerStatus(AutoTimerIndx_t)

- 功能：返回当前 timer 状态位

#### HMI_AutoClrMode_ResetTimerSetFlag(AutoTimerIndx_t)

- 功能：仅清除 TIMER_SET 位

#### HMI_AutoClrMode_HasTimerExpired(AutoTimerIndx_t)

- 功能：查询是否到期
- 特性：未 SET 的 timer 返回 1 （按“已到期/可继续”语义处理）

#### HMI_AutoClrMode_CancelTimer(AutoTimerIndx_t)

- 功能：停止 timer 并清零状态位
