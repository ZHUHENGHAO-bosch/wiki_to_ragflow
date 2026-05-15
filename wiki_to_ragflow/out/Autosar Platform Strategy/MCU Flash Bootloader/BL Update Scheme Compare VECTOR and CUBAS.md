# BL Update Scheme Compare VECTOR and CUBAS

> Source: /spaces/CARSFW/pages/6874275970/BL+Update+Scheme+Compare+VECTOR+and+CUBAS
> Last modified: 2026-03-12T03:59:16.000+01:00

---

### 1.BL 需要的所有模块以及比较情况如下：

|   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- |
| 序号 | 模块 | Vector | Cubas | CommonModule | 备注 | 是否能和app共用 |
| 1 | vector_bsw | 有 |  |  | Vector释放的代码包 |  |
| 2 | vector_bsw_cfg（BL\BM\BLU） | 有 |  |  | Vector代码配置工程 |  |
| 3 | Cubas_Fbl |  | 有 |  | Cubas释放的代码 |  |
| 4 | Cubas_FblCfg |  | 有 |  | Cubas代码配置文件 |  |
| 5 | Cubas_Mcal |  | 有 |  | Cubas Mcal配置工程 |  |
| 6 | Cubas_BM |  | 有 |  | Cubas释放的代码 |  |
| 7 | Cubas_BLU |  | 有 |  | Cubas释放的代码 |  |
| 8 | Cubas_BoschData |  | 有 |  | Cubas BM配置文件 |  |
| 9 | startup |  |  | 有 | 不同类型芯片使用不同启动代码 | 是 |
| 10 | BM_ApplicationCode | 有 |  |  | 处理异常、复位以及secureboot的操作 |  |
| 11 | BM_ApplicationCodeCfg | 有 |  |  | 处理 异常、复位、startup配置 |  |
| 12 | Mcal | 有 |  |  | EB 配置工程 |  |
| 13 | AliveLedCtrl |  |  | 有 | 控制debugboard呼吸灯 |  |
| 14 | SoftwareVersion |  |  | 有 | 控制BL的软件版本号 |  |
| 15 | DltLite |  |  | 有 | 打印系统运行时log |  |
| 16 | FBL_RetentionRam |  |  | 有 | 升级成功后清理指定retention ram区域 |  |
| 17 | IncRouter |  |  | 有 | 与soc之间通信的应用层 |  |
| 18 | inctp |  |  | 有 | 与soc之间通信的协议层 | 是 |
| 19 | Rbuf |  |  | 有 | 数据传输协议 | 是 |
| 20 | FblTask |  |  | 有 | BL应用代码初始化以及周期函数处理模块 |  |
| 21 | IoHwAb |  |  | 有 | 对DIO进行pin的封装 |  |
| 22 | Kds |  |  | 有 | 不同项目需求可能不同 |  |
| 23 | DiagGw |  |  | 有 | 升级数据转换逻辑模块 |  |
| 24 | DiagProxy |  |  | 有 | 升级数据转换逻辑模块 |  |
| 25 | DiagR |  |  | 有 | 升级数据转换逻辑模块 |  |
| 26 | Fbl_ApExt |  |  | 有 | SGM项目和其他项目有区别 |  |
| 27 | PowerMLite |  |  | 有 | 项目的主要控制逻辑基本一致，但是各个action不同 | 是 |
| 28 | SystemStateHandler |  |  | 有 | soc给BL发送下电、远程刷写、切面等指令 |  |
| 29 | FBL_AB_Swap |  |  | 有 | BL下使能AB功能时使用 |  |
| 30 | FlashDrive |  |  | 有 | 根据不同芯片选择不同的驱动 |  |
| 31 | Scr |  |  | 有 | SGM项目独有 | 是 |
| 32 | Service.ResetHistory |  |  | 有 | SGM项目独有 | 是 |
| 33 | ThermalCtrl |  |  | 有 | 温度监控模块根据项目需求使用 |  |
| 34 | SilentUpdate_SwapBank |  |  | 有 | APP下实现静默升级，实际切面在BL下，使用该模块 |  |
| 35 | Security |  |  | 有 | HSM模块使用 |  |
|  |  |  |  |  |  |  |
