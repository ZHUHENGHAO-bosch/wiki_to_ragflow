# Issues summary

> Source: /spaces/CARSFW/pages/6208586926/Issues+summary
> Last modified: 2026-01-16T10:53:56.000+01:00

---

## 1. 不休眠问题排查步骤

1.1 先看powermode和system state状态是否都为0，若都为0，则继续1.2步骤排查。若system state不为0，则无法休眠，可参考“ 软件不休眠，system state状态为3 HMIINACTIVE ”该问题定位原因

448 2025/08/23 06:31:19.919999 10.0283 201 SCC SSMM SSM0 4148 log error non-verbose 12 SystemState_System_Task_Handle: prev_powermode =  0 cur_powermode =  0 cur_SysSts =  0 AccSigStatus =  0 SUM_SSC_SysPwrMd =  0 SysPwrMd_toflg =  0

1.2 看log NM= 里是否有非零值,如有非零值则证明网络被拉起，无法休眠

6336 2032/04/12 22:54:44.150990 80.8047 147 SCC INC_ TP__ 4111 log info verbose 1 Nm= 2 0 0 0P 0 0 0 0PN 0Rffc0W 0 0Daaaa2aE2 0 0 （不全为0）

1233 2032/04/12 22:52:01.839123 30.0080 229 SCC INC_ TP__ 4111 log info verbose 1 Nm= 0 0 0 0P 0 0 0 0PN 0R 0 0Wffc0Dffff3fE2 0 0   （全0）

1.3 看 sumwakeup source 是否未清零

133481 2032/04/12 23:33:59.788060 2436.7604 60 SCC INC_ TP__ 4111 log info verbose 1 sumwkupsts_bits= 0x00001009 , 2 2 2 2 2 2 2 2 2 2 2

1234 2032/04/12 22:52:01.842123 30.0081 230 SCC INC_ TP__ 4111 log info verbose 1 sumwkupsts_bits=0x00000000, 0 0 0 0 0 0 0 0 0 0 0

sumwkupsts_bits 解析方法：将0x00001009 转成2进制 0001000000001001 对应为1的bit 为SUM wakeup source置起位（bit0代表wakeupsource_0）。与如下表格对应即可知：

1589 2025/09/26 13:56:19.050994 32.5913 45 SCC PLCM PLC0 4146 log error non-verbose 2 evPNActivated:WakeupSource : 0

![](../../../../_images/Issues%20summary/image-2025-9-23_13-20-18.png)

SUM_SUSD_ActiveWakeupList

| main | NS |
| --- | --- |
| ![](../../../../_images/Issues%20summary/image-2025-9-23_13-27-47.png) | ![](../../../../_images/Issues%20summary/image-2025-9-24_19-34-38.png) |
| ![](../../../../_images/Issues%20summary/image-2025-9-23_13-28-33.png) | ![](../../../../_images/Issues%20summary/image-2025-9-29_11-28-49.png) |
|  |  |

|   |   |   |
| --- | --- | --- |
| wakeup ID | ActiveWakeupID | EcuM_WakeupSourceType |
| WakeupSource_0 | 16u | EcuMConf_EcuMWakeupSource_Firewall_ICB_fee23c01 |
| WakeupSource_1 | 25u | EcuMConf_EcuMWakeupSource_CN_LIN00_53928378 |
| WakeupSource_2 | 17u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_IPC_LIN1_Cluster |
| WakeupSource_3 | 20u | EcuMConf_EcuMWakeupSource_Firewall_PCB_ed15a4fe |
| WakeupSource_4 | 12u | EcuMConf_EcuMWakeupSource_Firewall_DCAN_edd8daae |
| WakeupSource_5 | 6u | EcuMConf_EcuMWakeupSource_Firewall_B2CB_a600a9bc |
| WakeupSource_6 | 23u | EcuMConf_EcuMWakeupSource_Firewall_S2CAN_f7ba91e5 |
| WakeupSource_7 | 9u | EcuMConf_EcuMWakeupSource_Firewall_CCB_f375b9d7 |
| WakeupSource_8 | 8u | EcuMConf_EcuMWakeupSource_Firewall_BCB_f2b7d3e0 |
| WakeupSource_9 | 14u | EcuMConf_EcuMWakeupSource_Firewall_H2CB_c9bd49d8 |
| WakeupSource_10 | 21u | EcuMConf_EcuMWakeupSource_Firewall_S1CAN_e50f3e0b |
| WakeupSource_11 | 18u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_BUTTON |
| WakeupSource_12 | 5u | EcuMConf_EcuMWakeupSource_CN_VKSCAN_07868bf6 |
| WakeupSource_13 | 11u | EcuMConf_EcuMWakeupSource_Firewall_EL2CB_fd4908a6 |
| WakeupSource_14 | 22u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_BUTTON |
| WakeupSource_15 | 24u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_DP0_LVDS |
| WakeupSource_16 | 26u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_DP1_LVDS |
| WakeupSource_17 | 27u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_DS1_LVDS |
| WakeupSource_18 | 28u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_DSI_LVDS |
| WakeupSource_19 | 0u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_POWER |
| WakeupSource_20 | 29u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_REVRSGEAR |
| WakeupSource_21 | 30u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_RTC_IRQ_B |
| WakeupSource_25 | 10u | EcuMConf_EcuMWakeupSource_ECUM_WKSOURCE_ACTIVE_LINE |

## 2. 重启问题排查

参考如下wiki:

How to analysis reset issue and wakeup source - GEN4 generic - Docupedia

Hint：先通过McuResetRaw值判断是不断重启还是不断休眠唤醒，如为不断休眠唤醒则应调查唤醒源是谁。

0 2025/08/23 06:31:19.868136 0.0452 21 SCC REST HSTY 4184 log warn verbose 1 [RH] McuResetRaw: 0x10 , ResetType:0x1, ScrWakeup:0x0, FELReset:0x0  (重启) 2226 2025/08/23 06:33:11.456994 0.0503 22 SCC REST HSTY 4184 log warn verbose 1 [RH] McuResetRaw: 0x40010000 , ResetType:0x0, ScrWakeup:0x1, FELReset:0x0 （休眠唤醒）

## 3. System state issues

### 3.1. System state 状态不切换

通常因为powermode的MAC校验有问题，导致system state无法正常收到powermode的值，powermode一直为0，需找security同事排查.

可从以下log获取powermode和system state的状态：SUM_SSC_SysPwrMd为sum模块传过来的powermode值

374808 2025/08/24 20:04:37.115988 5780.1063 158 SCC SSMM SSM0 4148 log error non-verbose 12 SystemState_System_Task_Handle: prev_powermode =  0 cur_powermode =  0 cur_SysSts =  0 AccSigStatus =  0 SUM_SSC_SysPwrMd =  0 SysPwrMd_toflg =  0

system state状态定义如下：

![](../../../../_images/Issues%20summary/image-2025-9-4_18-17-51.png)

### 3.2. 软件不休眠，system state状态一直为run，无法切换

KDS刷写不对，刷成了不下电的KDS，通过查看AccSigStatus值是否为1来判断KDS版本， 1-不下电版本  0-正常下电版本

374808 2025/08/24 20:04:37.115988 5780.1063 158 SCC SSMM SSM0 4148 log error non-verbose 12 SystemState_System_Task_Handle: prev_powermode =  0 cur_powermode =  0 cur_SysSts =  0 AccSigStatus =  0 SUM_SSC_SysPwrMd =  0 SysPwrMd_toflg =  0

Hint: SysPwrMd_toflg关键字用于指示powermode 111报文是否存在timeout，可用于辅助分析P CAN是否正常。

### 3.3. 软件不休眠，system state状态为3 HMIINACTIVE

应用端请求了长模式或者哨兵模式，会有如下log的周期性打印：需应用端不在请求长模式后会超时退出HMIINACTIVE

![](../../../../_images/Issues%20summary/image-2025-9-5_10-11-47.png)

相关函数代码： SystemState_ControlPartialNetworkExt_0x90（）触发0x90函数； SS_Timer_Expired（）超时退出函数

### 3.4. STR条件不满足，未进 STR

PIS-9006 System Power Management 文档中有描述进入STR的前提条件。

如下log关键字会指示哪个condition不满足进STR

239177 2025/08/20 21:49:19.682061 4458.5260 230 SCC SSMM SSM0 4148 log error non-verbose 20 iSBCGood :  0 BattSOXSat :  0 NoIFWKUP :  0  SMT3 :  0  OtaCrVal :  141  OtaCrValInv :  0  IbsCheck1 :  0  IbsCheck2 :  1  IbsCheck3 :  1  IbsCheck4 :  1 239178 2025/08/20 21:49:19.689994 4458.5260 231 SCC SSMM SSM0 4148 log error non-verbose 24 STRAllowed: 0 CalChk: 1 CSChk: 1 TLMChk: 1 MSWUPChk: 1 BCChk: 0 IRChk: 1 4BChk: 1 PMChk: 1 FRChk: 1 IgPM : 0 BattCondIgnore: 0

### 3.5. Remote flash 相关问题

system state 未停留在infotainment 进入了HMIInactive：需要ota master侧下发is_remote_reflash_campaign_available =TRUE才能进入 LocalInfo_UpdateAvailable。

代码关注 isLocalInfoEnabled和 isUpdateAvailable两个函数会打印相关log ， 可参考如下log和bug中的分析comment。

46696 2025/08/11 17:44:22.127971 288.6686 5 SCC SSMM SSM0 4148 log error non-verbose 4 UpdateAvail: 1 VehicleSupportPPM: 1

Bug 1108753: [NDLB MY26][8155][OTA]AMP刷新，进度条持续0%显示，刷新过程中失败退出 - Change and Configuration Management

### 3.6. system state EA 状态图

代码Autosar\Application\GM\gmGemIPCSwc\ImpArch\SWC_INFO_SystemState_SRC\model中有system state的EA状态图，各个子模块之间的跳转以及跳转条件都可从EA图上获取。

system state启动阶段状态变化： Powermode : off ----run System state ：Off—Animation Init—HMI Init----RUN

system state下电阶段状态变化： Powermode : run ----off System state ：Run—localinfotainment (门开门关后)—HMIInactive—OFF

system state其他状态变化： Powermode :任意状态切到start System state ：从当前状态跳转进start

Powermode :start --run System state ：参考start 状态图，如果animation未ready 则进入animation init, 如果animation ready, hmi 未ready, 则进入Hmiinit,如果两者都ready且动画播放完成则进run状态。

在SystemState_Appl_Power_Mode_Init函数中初始化了 ss_timer_value[]数组， 其中包含了各个状态机的超时时间

Rte_SWC_INFO_SystemState_SystemStateP_VeSystemState变量用于观测system state的状态变化

system state相关文档参考如下：

“FG.04.03-Determine Infotainment System State.pdf”

“PIS-9006 System Power Management V0.0.0.x.docx”

"SFS-107_VCU_System State and PLC state HLD_v3.2.pdf"  [system state 和PLC INC channel 里的message ID 定义和含义都在这份文档里]

## 4. PLC

### 4.1. PLC log中能看到sum状态和是否有ECUMwakeup list, log关键字如下：

701 2025/09/04 06:18:39.978983 39415.3497 39 SCC PLCM PLC0 4146 log error non-verbose 6 SUMState =  1  , SUM_PNC_ShutdownPermission =  1 , EcuMWakeupList =  1065057

### 4.2. PLC 请求shutdown type

一定要 maxSuspendTime 不等于0才能成功请求suspend

9057 2025/08/08 15:10:56.708039 179.5541 69 SCC PLCM PLC0 4146 log error non-verbose 6 PLC_co_Command_Shutdown: AlarmVal_Second =  38784 ElapsedTime_Second =  38725  , maxSuspendTime =  120 9058 2025/08/08 15:10:56.708039 179.5542 70 SCC PLCM PLC0 4146 log error non-verbose 4 cb INC TX->INC_ID_RequestShutdown (0xC0): shutdownCmdType =  2 , maxSuspendTime =  120

shutdown type:

typedef enum

{

PLC_SHUTDOWN_NORMAL,

PLC_SHUTDOWN_FASTSHUTDOWN,

PLC_SHUTDOWN_SUSPEND,

PLC_SHUTDOWN_SUSPEND_NOINFOWAKE,

PLC_SHUTDOWN_SHUTDOWN_NOINFOWAKE

} PLC_SHUTDOWN_T;

### 4.3. PLC Pull back

如下log中会打印pullback wakeup source, wakeup source 对应关系参考上表：

138 2025/05/20 13:19:02.149478 0.1045 131 SCC PLCM PLC0 4146 log error non-verbose 44 evPNActivated: WakeupSource_0: 1 WakeupSource_1: 0 WakeupSource_2: 0 WakeupSource_3: 0 WakeupSource_4: 0 WakeupSource_5: 0 WakeupSource_6: 0 WakeupSource_7: 0 WakeupSource_8: 0 WakeupSource_9: 0 WakeupSource_10: 0 WakeupSource_11: 0 WakeupSource_12: 0 WakeupSource_13: 0 WakeupSource_14: 0 WakeupSource_15: 0 WakeupSource_16: 0 WakeupSource_17: 0 WakeupSource_18: 0 WakeupSource_19: 0 WakeupSource_20: 0 WakeupSource_21: 0

### 4.4. PLC EA 状态图

代码Autosar\Application\GM\gmGemIPCSwc\ImpArch\SWC_INFO_PowerLifeCycle_SRC\model中有PLC的EA状态图，PLC状态跳转条件可从EA上获取。

plc_timer_value[]数组中定义了PLC各个状态机的超时时间

PLC相关文档参考如下：

“SFS_123_VCU_VIP_PowerLifeCycle Management_HLD_Ver1.20.pdf”

"SFS-107_VCU_System State and PLC state HLD_v3.2.pdf"

### 4.5. PLC 代码

PLCCheckNmStatus () 中进行 pull back

PLC_Timer_Expired() 所有 timer 超时通过这里

PLCM_Report_Power_Level_SoC() to get soc power level

PLC_Task() PLC模块主要task，在里面判断下电条件是都满足，是否有高低压高低温发生。

IoHwAb_PLC_State变量用于观测plc的状态

## 5. SUM SUSD

### 5.1. 主要函数与变量：

SUM_SUSD_ASS_Init();

SUM_SUSD_ASS_Main_Runnable();

SUM_SUSD_ASS_Update_ActiveWakeupList(); SUM_SUSD_ActiveWakeupList 变量用于观测wakeup的状态

SUM_SUSD_ASM:

Input 和 output 见下图：

![](../../../../_images/Issues%20summary/image-2025-9-10_10-20-20.png)

用的是 SUM_SUSD_ASM_Main_Runnable （）从 SUM_SUSD_ASM_ShutdownPermission_Runnable () 拿 ShutdownPermissionState

0关联SUM_DIAG_ShutdownPermission_Runnable  ------全局变量Rte_SUM_DIAG_SUM_DIAG_ShutdownPermission_SUM_SUSD_UserRequest

1关联SUM_ERRH_ShutdownPermission_Runnable  ------全局变量 Rte_SUM_ERRH_SUM_ERRH_ShutdownPermission_SUM_SUSD_UserRequest

2关联SUM_PNC_ShutdownPermission_Runnable  ------全局变量 Rte_SUM_PNC_SUM_PNC_ShutdownPermission_SUM_SUSD_UserRequest

3关联Rte_SWC_INFO_PowerLifeCycle_PLC_SUM_SSC_ShutdownPermissionP_data  -

4关联 Runnable_EA_SYS_DIAG（）需要写入255   ------全局变量 Rte_SWC_EA_SYS_IPC_Diag_GP_ShutdownPermission_SUM_SUSD_ShutdownPermission

5关联 PLC_ShutdownPermission  ------全局变量Rte_SWC_INFO_PowerLifeCycle_PLC_ShutdownPermissionP_VePLC_ShutdownPermission

SUM_SUSD_ASS:

The Application Start / Shutdown function controls the SUSD_<SUM/SWC>_PermitExecution<1..n>

interfaces.

![](../../../../_images/Issues%20summary/image-2025-9-10_10-21-27.png)

具体功能和描述参考如下文档：

GB8002_AUTOSAR_Standard_Utility_Modules_Specification.pdf

### 5.2. 如何添加一个新的唤醒源

参考如下提交链接

topic:"ACTIVE_LINE_WAKEUP" · Gerrit Code Review

topic:"ACTIVE_LINE_WAKEUP_part2" · Gerrit Code Review

## 6. BPMM

参考文档 sfs-107  12.5.3 Backup Power Mode Master章节 的需求描述。以及文档“GB3001_PowerModeClientSpecification.pdf”

bug参考：

Bug 2558420: [PPV][LCM] 点击一键下电触发VCU作为BPMM，未找到相应的CAN信号和vdata输出 - Change and Configuration Management

文档链接：

Documents - XC-CT China - Docupedia

## 7. RTC SWC

参考文档 INC_Message_Definitions_GM_Info_4.0_v2.0_Bosch_AddOn 1 (1) 3.4    DATE_TIME Channel 章节 的需求描述。

其中描述了soc与scc间RTC 时间传输格式和alarm type的传输格式。

RTC SWC在vcuplus上做了适配，适配taiji平台的RTC，精度从minute适配成了second。

## 8. FastShutdown

290839 2019/01/01 08:00:09.567907 10.5598 54 SCC PLCM PLC0 4146 log error non-verbose 1 Diag_RequesetFastShutdown!

## 9. vcuBootCount

2198 2026/01/16 17:49:46.044661 10.0639 114 SCC PLCM PLC0 4146 log error non-verbose 4 PLC: startupLogPrint(10s): vcuBootCount = 250 resetHistory = 33620226
