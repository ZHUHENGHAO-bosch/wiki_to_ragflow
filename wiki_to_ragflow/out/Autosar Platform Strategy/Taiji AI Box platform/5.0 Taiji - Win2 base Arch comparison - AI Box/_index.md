# 5.0 Taiji - Win2 base Arch comparison - AI Box

> Source: /spaces/CARSFW/pages/7111923828/5.0+Taiji+-+Win2+base+Arch+comparison+-+AI+Box
> Last modified: 2026-05-09T13:56:49.000+02:00

---

## Overview

This page is to analyze the architectural difference between Win2 and Taiji platform

AI-Box平台方案评估 - XC-CT China - Docupedia

6. Architectural design — BOSCH (China) ADCC BSW documentation

For each feature owner to first analyze the difference and find how big change we need in Taiji to adapt

Note: EINC协议中对数据Data的要求是第一个Byte是msg id 暂定设计方案是EINC→INC Router层，所有INC user根据需要使用protobuf，因此需要SOC端确认把msgid还给用户统一做序列化 ref4.1 (4): 2 EINC Solution Discussion - wave 3 development - Docupedia

### Overall features

| F.No | Feature | Taiji | Win2 | Owner | einc payload | Complexity | Efforts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | timesync |  | einc chn - 0x0c msgid - 0x00 sequence - soc req（period） mcu response current time | LIU Jun (XC-CP/ESW2-CN) | typedef struct { uint64 time_ns ; uint8 isValid ; uint8 pad [ 7 ]; } UTCTIME_Info_t ; |  |  |
| 2 | LCM - PSC (SUSD), System State |  | einc chn - 0x00 MCU→SOC 普通报文 msgid-0x00 发送系统状态给SOC,(也可以作为MCU给SOC的心跳使用) 发送周期500ms typedef struct { uint8 u8MsgId; rbW3SysMgr_SystemStateEnumType eSystemState; rbW3SysMgr_McuModeEnumType eMcuMode; ComM_StateType eComMState; // not used uint8 u8IpduGroup; // not used }rbW3SysMgr_TxMsg_SystemState_MsgType; msgid-0x08 发送power cycle cnt给SOC, 收到SOC心跳200ms后发送 typedef struct { uint8 u8MsgId; uint8 u8PowerCntU32Arr[4]; uint8 u8AppCntU32Arr[4]; uint8 u8BootCntU32Arr[4]; }rbW3SysMgr_TxMsg_PowerCntToSoc_MsgType; msgid-0x28 通知SOC系统模式发生了热切换，在sysmode热切换后发送 typedef struct { uint8 u8MsgId; uint8 u8SysModeMsgVal;  //系统模式对应的value }rbW3SysMgr_TxMsg_SysModeNotify_MsgType; ========================================================== SOC→MCU 普通报文 msgid-0x3F SOC心跳, typedef struct { uint8 u8MsgId; uint8 u8Dummy; }rbW3SysMgr_RxMsg_SocHeart_MsgType; msgid-0x07 SOC收到DoIp消息,通知MCU，用于MCU维持CAN网络 typedef struct { uint8 u8MsgId; uint8 u8Dummy; }rbW3SysMgr_RxMsg_SocDiagMsgRx_MsgType; ========================================================== MCU→SOC request-response报文 请求msgid-0x40 请求SOC关机, 应答msgid-0x80，应答超时200ms, retry:19次 请求msg结构体 typedef struct { uint8 u8MsgId; rbW3SysMgr_IncSignal_SocShutdownType eSocShutdownType;  // soc关机类型，有完整关机，快速关机 }rbW3SysMgr_TxReqMsg_ReqSocPostrun_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_TxReqMsg_ReqSocPostrun_AckType; ========================================================== SOC→MCU request-response报文 请求msgid-0x4C SOC请求Ecu Reset, 应答msgid-0x8C 请求msg结构体 typedef struct { uint8 u8MsgId; rbW3SysMgr_RxSiganl_EcuResetType eEcuResetType; rbW3SysMgr_IncSignal_SocShutdownType eSocShutdownType; // soc关机类型，有完整关机，快速关机 }rbW3SysMgr_RxReqMsg_ReqEcuReset_MsgType; typedef enum { RBW3SYSMGR_RXSIGVAL_ECU_SOFT_RESET = 0x00, RBW3SYSMGR_RXSIGVAL_ECU_HARD_RESET = 0x01, RBW3SYSMGR_RXSIGVAL_ECU_KEY_OFFON_RESET = 0x02, RBW3SYSMGR_RXSIGVAL_ECU_CUSTOM_RESET = 0x03, RBW3SYSMGR_RXSIGVAL_ECU_RESET_NUM }rbW3SysMgr_RxSiganl_EcuResetType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_RxReqMsg_ReqEcuReset_AckType; 请求msgid-0x44 SOC请求Mcu Reset进FBL, 应答msgid-0x84 请求msg结构体 typedef struct { uint8 u8MsgId; boolean u8Dummy; }rbW3SysMgr_RxReqMsg_ReqEnterBoot_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_RxReqMsg_ReqEnterBoot_AckType; 请求msgid-0x45 SOC请求Mcu复位SOC并让SOC进入Recovery, 应答msgid-0x85 请求msg结构体 typedef struct { uint8 u8MsgId; boolean u8Dummy; }rbW3SysMgr_RxReqMsg_ReqSocEnterRcm_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_RxReqMsg_ReqSocEnterRcm_AckType; 请求msgid-0x4A SOC通知MCU SOC的诊断进程已经拉起, 应答msgid-0x8A 请求msg结构体 typedef struct { uint8 u8MsgId; boolean u8Dummy; }rbW3SysMgr_RxReqMsg_SocNotifyDiagServActive_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_RxReqMsg_SocNotifyDiagServActive_AckType; 请求msgid-0x4B SOC设置sysmode, 应答msgid-0x8B 请求msg结构体 typedef struct { uint8 u8MsgId; uint8 u8SysModeMsgVal; }rbW3SysMgr_RxReqMsg_SocReqSysModeSet_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_RxReqMsg_SocReqSysModeSet_AckType; 请求msgid-0x4D SOC请求获取当前sysmode, 应答msgid-0x8D 请求msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Dummy; }rbW3SysMgr_RxReqMsg_SocReqSysModeGet_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8SysModeMsgVal; }rbW3SysMgr_RxReqMsg_SocReqSysModeGet_AckType; 请求msgid-0x50 SOC请求获取当前MCU模式, 应答msgid-0x90 请求msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Dummy; }rbW3SysMgr_RxReqMsg_SocReqMcuModeGet_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8McuModeMsgVal; }rbW3SysMgr_RxReqMsg_SocReqMcuModeGet_AckType; 请求msgid-0x5F SOC请求Debug, 应答msgid-0x9F 请求msg结构体 typedef struct { uint8 u8MsgId; rbW3SysMgr_DebugEnumType eDebugType;  // 0:none 1:关闭SOC关机超时监控 uint8 u8DebugParaLen; uint8 u8DebugPara[5]; }rbW3SysMgr_RxReqMsg_SocReqDebug_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_RxReqMsg_SocReqDebug_AckType; 请求msgid-0x55 SOC通知MCU SOC升级后激活成功, 应答msgid-0x95 请求msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Dummy; }rbW3SysMgr_RxReqMsg_SocStopUpdateSession_MsgType; 应答msg结构体 typedef struct { uint8 u8MsgId; uint8 u8Ack; }rbW3SysMgr_RxReqMsg_SocStopUpdateSession_AckType; |  | 2.0 Taiji AI Box - SCC LCM Architecture - XC-CT China - Docupedia |  |  |
| 3 | DLT logging |  | unuse einc, directly through dlt's port 3490 by tcp/ip stack | SHI Zuolei (BCSC/ENG1) |  |  |  |
|  | VehicleData |  | einc chn - 0x01 msgid - 0x00 sequence - soc req mcu response current status（speed/Gear） | SHI Zuolei (BCSC/ENG1) | typedef struct { uint8     msg_id; uint8     ActualGear; uint16    ActualGearValid; uint16    VehicleSpeedVSOSig; uint16    VehicleSpeedVSOSigValid; } st_EincVehicle_type ; |  |  |
| 4 | OTA |  | follow “ LCM - PSC (SUSD), System State ” | ZHANG Xiaochen (BCSC/ENG1) |  |  |  |
| 5 | LCM - PowerManager |  | no EINC | LI Haojun (BCSC/ENG1) |  |  |  |
| 7 | Thermal |  | SOC→MCU 周期发送 einc chn - 0x09 msgid - 0x01 ![](../../../_images/5.0%20Taiji%20-%20Win2%20base%20Arch%20comparison%20-%20AI%20Box/image-2026-5-9_19-6-34.png) 无MCU->SOC消息发送 | LI Haojun (BCSC/ENG1) CAI Jiachao (XC-CP/ESW2-CN) |  |  |  |
| 8 | camer control |  | no camera on AIBOX, also no camera POC |  |  |  |  |
| 9 | Lifecycle |  |  |  |  |  |  |
| 10 | SystemInfo |  | einc chn - 0x0a 1. soc req 2. mcu response version（app /boot / hw ） |  | uint8* u8TxBuf （variable length） |  |  |
| 11 | EincLog |  | EINC内部使用 einc chn - 0x0e (用于EINC 内部心跳监测) |  |  |  |  |
| 12 | Loopback |  | EINC内部使用 einc chn - 0x0f（用于测试通路） |  |  |  |  |
| 13 | diag |  | einc chn - 0x04 soc req (trigger) mcu response | CAO Ping (XC-CP/ESW3-CN) |  |  |  |
| 14 | evm |  | einc chn - 0x05 soc send to mcu mcu send to soc(period) | CAO Ping (XC-CP/ESW3-CN) |  |  |  |
