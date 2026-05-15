# How to analyze kind of LCM issues --example by Chery 8155

> Source: /spaces/CARSFW/pages/4631368662/How+to+analyze+kind+of+LCM+issues+--example+by+Chery+8155
> Last modified: 2025-02-28T10:30:53.000+01:00

---

- Reset issues
- Pullback analysis(cycle_31.zip)
- Power issues(Jira bug )
- Sleep relevant issues
- SOC Startup issue(SOH Issues.dlt)
- SOH issue
- Rst[0~4] relevant
- STR issue
- Voltage issue
- Others

- Reset issues

- General reset info MCU reset reason (Print when SCC startup) MCUreset reason STBYR Reset Type LastWUSource LastTriReason Comment wake up( Wakeup.dlt ) 0xFE 0 0 not 0 not 0 warm reset/ porst reset 0x0A 0 4 0 0 Mcu_perform reset 0x03 0 2 0 0 power up( Power up reset.dlt ) 0xFE 1 (most case be 1, less case will be 0) 0 0 Retain ram 丢失

- 

- Note: ”Mcu_perform reset“ include almost all BSW and SWC requested reset.(几乎囊括了所有可能遇到的reset：  FUSA ， DIAG， LCM，APP，SOC) “ Porst reset ” 为外部触发了芯片PORST pin， include：WDG， SOC trigger by HW， JTAG . detail please refer HW schematic， Seach “ SYS_SCC_RESET_B_3V3 ”。

- Fusa reset( FUSA_RESET.dlt ) LOG 如下, 可以通过FEL 分析， 也可以通过SSH_的LOG 辅助分析，宏定义在 SSH_Cfg_Types.h 。 注意查看相关代码是否会执行reset。

- FEL reset Load LCM Filter in dlt, You can find logs similar to the one below in about 1 second。（DLT 工具中加载LCM filter之后，时间戳 1s左右会发现如下的类似LOG ）。 [270598145]  ----0-----f-;--$---------------|14 00 02 07 30 00 03 f1 c2 bf 66 00 3b 15 05 24 00 00 00 05 03 02 00 01 00 00 03 0b 00 00 00

- LOG 分析: Raw Data Means Data Comment Code refer 14 00 Error Count 0x0014 20 times 代表当前错误已经那发生了20次 02 0 7 30 Component ID 0x3007 COMPONENT_ID_PRJ_LCM_POWERSTATECONTROLLER NOTE： 07 34 ： FUSA     (Involve FUSA guy） 27 10： PowerM（一般为SOC 上电失败， 大约1-2s 发生reset） Macro defined in Project_ComponentIdentifier.h Code exist in FatalErrorLogger.c 00 ErrorCode 03 FELFlag 0x03 FEL_MSG_FLAG_PERSISTENT & FEL_MSG_FLAG_RESET_ALWAYS f1 c2 bf 66 Time stamp 00 Active Task 3B Las tActive Task 15 PowerM data PowerM_PowerMode:  0x01 Power_State:                0x05 PowerM_PowerMode:     POWERM_POWERMODE_NORMAL_VOLTAGE Power_State:                    POWERM_SM_STATE_RUN Code exist in FatalErrorLogger_Platform.c Macro defined in PowerM_Types.h 05 EcuMOpMode 0x05 ECUM_ECUOPMODE_SCCRUN Macro defined in EcuManager_EcuModeProxy.h 24 00 Wake up events 0x0024 00 00 05 EcuMOpMode 0x05 ECUM_ECUOPMODE_SCCRUN Macro defined in EcuManager_EcuModeProxy.h Message_p->Project.data[0] = (uint8)EcuM_getEcuOpMode();; 03 PSC state 0x03 PSC_SOC_SUSDC_STATEMACHINE_SOCSTARTUPSYNC Macro defined in Psc_Type.h Message_p->Project.data[1] = (uint8)Psc_SoC_SuSdC_Statemachine_GetState(); 02 Reset type 0x02 参考上面的 General reset info 中的reset type Message_p->Project.data[2] = (uint8)startup_log.sys_info.reset_type; 00 meaningless 01 00 00 03 0b 00 00 00 Error Data

- SOC request reset Load LCM Filter in dlt, You can find logs similar to the one below，Unclear timestamp。（DLT 工具中加载LCM filter之后，会发现如下的类似LOG， 时间戳不固定， 任何时间都可能会发生 ）。 LOG Apid Meanings Comments ShutdownRequest 1,3,1,0x2000 NOTE: If  there is no this msg , consider SWC reset or Diag reset. LCMC SOC send shutdown Request to SCC 1:                REQ_RESET                                        (request_type ) 3:                REQ_REASON_ERROR_RECOVERY  （shutdown_reason） 1:                CONTROLLED_SHUTDOWN           （shutdown_type ） 0x200:         OTA_RESET                                     （special_reason ） NOTE: Usually only focuses on  request_type and   special_reason SetResetInfo flag=512 Psc_ PSC_RESET_FLAG_SOC_CONTROLLED_RESET_APP

- SWC request reset(Hard Key reset)

- Load LCM Filter in dlt, You can find logs similar to the one below，Unclear timestamp。（DLT 工具中加载LCM filter之后，会发现如下的类似LOG， 时间戳不固定， 任何时间都可能会发生 ）。

- 也可通过第二次启动后early LOG 中的ReportStartupCondition来确定上一次的下电原因 LOG Apid Meanings Comments SetResetInfo flag=4 Psc_ PSC_RESET_FLAG_KEY_COMBINATION_SYSTEMRESET psc_SocShutdownRsn = 0x1000000 Psc_ com_bosch_cm_housekeeping_pb_lcmif_SpecialShutdownReason_LCM_SPECAIL_RESET_COMBINED_HARD_KEY

- Diag request reset(Refer to SWC reset) 如果是Hard reset的话，会导致Retainram 丢失， 重启后Rst[1~4]为空， Rst[0]中的resetcounter 从0开始重新计数。

- Pullback analysis( cycle_31.zip )

- 原因：当前所有项目的SOC 不支持P1 PULLBACK 。 此现象为满足客户定义的休眠条件后，系统开始走休眠流程，但在系统休眠过程中SCC 检测到了唤醒源，需要恢复整个系统，但因SOC 的休眠流程不可打断， 所以SOC 必然经历休眠唤醒的过程导致Cycle +1，而SCC 在SOC 完全休眠后，可以在自身不休眠的情况下重新唤醒SOC， 所以造成此现象， LOG： Early log中timestamp一栏与商议cycle可以衔接， 且可在LOG 中看到SOC 下电又重新上电的Psc_模块的关键词， 一般情况下为网络唤醒， 所以可在NetM模块的LOG 中查看到唤醒报文信息。

- Power issues( Jira bug )

- Sleep relevant issues

- SOC Startup issue( SOH Issues.dlt )

- SOH issue

- Rst[0~4] relevant

- STR issue

相关信息可参考wiki： RTC RA8804CE unexpectedly triggered the AF flag

- STR timeout

现象：进入STR失败，走了休眠唤醒的唤醒流程

原因： STR_MODE没有拉高导致SCC侧LCM认为STR超时，后续SOC走了下电冷起的过程

LOG：

![](../../../../_images/How%20to%20analyze%20kind%20of%20LCM%20issues%20--example%20by%20Chery%208155/image-2024-11-11_13-11-58.png)

措施：转给SOC 继续分析。

- STR failed

现象：进入STR失败，走了休眠唤醒的唤醒流程

原因： SOC主动退出STR，后续SOC走了下电冷起的过程

LOG：

![](../../../../_images/How%20to%20analyze%20kind%20of%20LCM%20issues%20--example%20by%20Chery%208155/image-2025-2-28_17-28-7.png)

![](../../../../_images/How%20to%20analyze%20kind%20of%20LCM%20issues%20--example%20by%20Chery%208155/image-2025-2-28_17-28-21.png)

措施：转给SOC 继续分析。

- Voltage issue

现象：实车报告仪表大屏黑屏重启

原因：实车电源电压出现波动，超高压（＞18.7V）导致SOC请求车机重启。

LOG：

![](../../../../_images/How%20to%20analyze%20kind%20of%20LCM%20issues%20--example%20by%20Chery%208155/image-2024-11-11_13-16-23.png)

措施：转回测试同事检查电源相关设备。

- Others
