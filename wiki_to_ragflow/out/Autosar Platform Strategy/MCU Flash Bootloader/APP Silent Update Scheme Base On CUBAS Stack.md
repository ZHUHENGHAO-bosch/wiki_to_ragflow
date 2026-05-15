# APP Silent Update Scheme Base On CUBAS Stack

> Source: /spaces/CARSFW/pages/6874275179/APP+Silent+Update+Scheme+Base+On+CUBAS+Stack
> Last modified: 2026-02-26T10:49:07.000+01:00

---

### Contents

### 一．          TC397 Pflash

### 二．          FOTA 功能

### 1. 功能框图

### 2. 升级流程图

### 三．          切面功能

### 四．          app 下实现升级的模块路径

### 五．          初始化函数的调用路径

### 六．          INC 诊断协议

### 一. TC397 Pflash

#### 1.TC397 Pflash swap  每个面的大小为7M，如下图：

![](../../_images/APP%20Silent%20Update%20Scheme%20Base%20On%20CUBAS%20Stack/image-2026-2-26_17-32-51.png)

#### 2.在芯片的数据手册中，对Dflash和Pflash的操作有明确的规定，即Dflash和Pflash不能同时进行操作，一次只能操作一个，所以需要使用MemACC模块进行指令的并发处理。

如下：

![](../../_images/APP%20Silent%20Update%20Scheme%20Base%20On%20CUBAS%20Stack/image-2026-2-26_17-34-3.png)

### 二. FOTA 功能

#### 1. 功能框图

![](../../_images/APP%20Silent%20Update%20Scheme%20Base%20On%20CUBAS%20Stack/image-2026-2-26_17-35-15.png)

##### 1.1 在app模式下，增加DiagGw、DiagR、DiagProxy模块来处理接收的升级数据；

##### 1.2 在app模式下的配置工程中增加DiagProxy PduR和Dcm的连接配置；

##### 1.3 在app模式下，增加升级相关的诊断服务，如10 60，31 01 ff 00，34，36，37，31 01 02 02，31 01 02 05；以及调用MemAcc接口的Flash hanle服务函数；

##### 1.4 Infineon TC397 不能同时操作DFlash和PFlash，集成这个模块，实现DFlash和PFlash的互斥访问；

##### 1.5 在app模式下，增加SysStateHandle服务，用来处理接收到的swap bank指令以及读取scc information的指令；

### 2. 升级流程图

![](../../_images/APP%20Silent%20Update%20Scheme%20Base%20On%20CUBAS%20Stack/image-2026-2-26_17-37-50.png)

### 三. 切面功能

#### 3.1 在app模式下接收到切面指令后，会存储一个标志到Retention Ram中；这个标志是BL和app共享的标志；

#### 3.2 在升级完后接收到下电指令，app会判断下电指令的类型，如果是升级完且下电的指令，app则会reset，并设置重启目标为BL；

#### 3.3 在进入BL后，会在上电之前运行swap函数，然后进行reset；

#### 3.4 经过上面的过程后，mcu就完成了切面并重启的过程；

### 四. app 下实现升级的模块路径

#### 4.1 bosch应用逻辑控制路径

#### .\Config\Autosar\Application\SilentUpdate\

#### 4.2 cubas 代码逻辑路径

#### .\Config\Autosar\stdcore\Cubas\CubasBSWCfgTemp\SilenceUpdate_CubasFbl\

#### 4.3 地址配置文件路径

#### .\Config\Autosar\stdcore\Cubas\CubasBSWCfgTemp\SilenceUpdate_CubasFbl\Cubas_FblCfg\ApplicationLayer\rba_BldrCmp\api\ rba_BldrCmp_Cfg_LogBlkHdl.h

#### 4.4 实际切面文件路径

#### . \Bootloader\Config\Bootloader\SilentUpdate_SwapBank\

### 五. 初始化函数的调用路径

#### 5.1

#### .\Config\Autosar\stdcore\Cubas\CubasBSWCfgTemp\RtaosBuildLib\RTAOS_Cbk\ RTAOS_ISR_TaskCbk.c

### 六. INC 诊断协议

|   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- |
| byte 0 | byte 1 | byte 2 | byte 3 | byte 4 | byte 5 | … |
| Message ID | Version | Segment Type | Domain ID | Payload Size |  | Payload Data |

Message ID:

Request (SOC -> SCC)

|   |   |   |
| --- | --- | --- |
| Message ID | Description | Dcm Req Mapping |
| 0x62 | Session Control: Enter Programming Session | 10 60 |
| 0x43 | Routine Control | 31 01 xx xx |
| 0x44 | Request Download | 34 |
| 0x45 | Data Transfer | 36 |
| 0x46 | Transfer Exit | 37 |

Response (SCC -> SOC)

|   |   |   |
| --- | --- | --- |
| Message ID | Description | Dcm Rsp Mapping |
| 0xE2 | Session Control: Enter Programming Session | 50 60 xx xx xx xx |
| 0xC3 | Routine Control | 71 01 xx xx |
| 0xC4 | Request Download | 74 |
| 0xC5 | Data Transfer | 76 |
| 0xC6 | Transfer Exit | 77 |

Version: 0xA1

Segment Type:

|   |   |
| --- | --- |
| Bit | Description |
| Bit 7 | Indicates if first segment |
| Bit 6 | Indicates if last segment |
| Bit 5 | 1 request or 0 response |
| Bit 4 | Abort/Failure (last segment) |
| Bit 0-3 | Unique ID to identify message (0 indicates notification only) |

Domain ID: SOC - 0x20   SCC - 0x02

Payload Size: 0x0 – 0xFFFF   (Big End)

#### 6.1 Session Control

|   |   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Service |  | MsgID | Ver | SegType | DomainID | Payload Size |  | Payload Data |  |
| Session Control | Request | 0x62 | 0xA1 | 0xE0 | 0x20 | 0x00 | 0x01 | 0x01 | Update Target |
| Response | 0xE2 | 0xA1 | 0xC0 | 0x02 | 0x00 | 0x01 | 0x00 |  |

Update Target Definition：

|   |   |
| --- | --- |
| Update Target | Description |
| 0x01 | Update Target is App |
| 0x02 | Update Target is Hsm |
| 0x03 | Update Target is Bl |

#### 6.2 Routine Control

|   |   |   |   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Service |  | MsgID | Ver | SegType | DomainID | Payload Size |  | Payload Data |  |  |  |
| Routine Control | Req | 0x43 | 0xA1 | 0xE0 | 0x20 | 0x00 | 0x01 | 0x01 | RID | RID | 0x01 |
| Rsp | 0xC3 | 0xA1 | 0xC0 | 0x02 | 0x00 | 0x01 | 0x00 | RID | RID | Result |

RID Definition：

|   |   |
| --- | --- |
| RID | Description |
| 0xFF00 | Erase Memory |
| 0x0212 | Signature Verification |
| 0x0205 | Compatibility Verification |

Result Definition：

|   |   |
| --- | --- |
| Result | Description |
| 0x00 | Successful |
| 0x01 | Failed |

#### 6.3 Request Download

|   |   |   |   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Service |  | MsgID | Ver | SegType | DomainID | Payload Size |  | Payload Data |  |  |  |
| Request Download | Req | 0x44 | 0xA1 | 0xE0 | 0x20 | 0x00 | 0x0A | 0x00 | 0x44 | Adr | Adr |
| Rsp | 0xC4 | 0xA1 | 0xC0 | 0x02 | 0x00 | 0x04 | 0x00 | 0x20 | 0x0F | 0xFE |

|   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- |
| Payload Data |  |  |  |  |  |
| Adr | Adr | Len | Len | Len | Len |
|  |  |  |  |  |  |

#### 6.4 Data Transfer

|   |   |   |   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Service |  | MsgID | Ver | SegType | DomainID | Payload Size |  | Payload Data |  |  |  |
| Data Transfer | Req | 0x45 | 0xA1 | 0xA1 [FF] | 0x20 | 0x0F | 0xFE | SN | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x22 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x23 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x24 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x25 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x26 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x27 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x28 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x29 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x2A | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x2B | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x2C | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x2D | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x2E | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x2F | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x20 | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
|  | 0x45 | 0xA1 | 0x61 [LF] | 0x20 | 0x0F | 0xFE | Data | Data | Data | ... |
| Rsp | 0xC5 | 0xA1 | 0xC0 | 0x02 | 0x00 | 0x02 | 0x00 | 0x01 |  |  |

##### SN: Sequence Number, 从0x01开始累加到0xFF复位到0x00后再继续累加。

#### 6.5 Transfer Exit

|   |   |   |   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Service |  | MsgID | Ver | SegType | DomainID | Payload Size |  | Payload Data |  |  |  |
| Transfer Exit | Req | 0x46 | 0xA1 | 0xE0 | 0x20 | 0x00 | 0x00 |  |  |  |  |
| Rsp | 0xC6 | 0xA1 | 0xC0 | 0x02 | 0x00 | 0x00 |  |  |  |  |
