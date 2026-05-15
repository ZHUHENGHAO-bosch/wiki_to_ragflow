# How to configure NvM

> Source: /spaces/CARSFW/pages/6240474395/How+to+configure+NvM
> Last modified: 2026-04-07T04:02:17.000+02:00

---

## 1.Requirements

SGM Local 8155 - NvM Requirements - All Documents

## 2.Review check List

| 编号 | 内容 | 检查结果 |
| --- | --- | --- |
| 1 | 新增的NVM block，需要在layout最后增加 |  |
| 2 | 新增NVM的时候强制检查一下数据类型，NVM_Readall会读取NVM数据，并设置mirror变量，配置不对，导致设置mirror变量失败，从而pending |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |

## 3.NvM Configuration

|   |   |   |
| --- | --- | --- |
| 存储协议栈缩略语表 |  |  |
| 缩略语 | 英文全称 | 中文解释 |
| EEPROM | Electrically Erasable Programmable Read-Only Memory | 电可擦可编程ROM |
| EA | EEPROM Abstraction | EEPROM抽象层 |
| FEE | Flash EEPROM Emulation | Flash EEPROM仿真 |
| LSB | Least Significant Bit | 最低有效位 |
| MemIf | Memory Abstraction Interface | 内存抽象接口 |
| MSB | Most Significant Bit | 最高有效位 |
| Logical block | Logical block | FEE模块用户看到的最小的可写/可擦单元 |
| Virtual page | Virtual page | 可由一个或多个物理页面组成的虚拟页面 |
| Internal residue | Internal residue | 虚拟页面末尾的未使用空间 |
| Virtual address | Virtual address | 由块号和偏移量组成的虚拟地址 |
| Physical address | Physical address | 设备特定格式的物理地址 |
| Dataset | Dataset | NVRAM管理器的可寻址块数组 |
| Redundant copy | Redundant copy | 提高可靠性的数据冗余存储 |
| DMU | Data Memory Unit | 数据存储单元 |
| Fls | Flash | Flash存储器 |
| OPER | Flash Operation Error | Flash操作错误 |
| SQER | Command Sequence Error | 命令序列错误 |
| EVER | Erase Verify Error | 擦除验证错误 |

应用程序和内存堆栈之间的交互以及所涉及的模块图如下：

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-17_10-45-55.png)

NvM Block配置 ：

基本存储对象: NV BLOCK(必选）, RAM BLOCK（可选，驻留在RAM),ROM BLOCK(可选）,Administrative block（必选）

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-17_10-53-47.png)

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-27_13-29-38.png)

注意点1：

在ECU启动阶段，如果配置了ROM BLOCK,NVMReadall会把 rom block的default value拷贝到 ram block。

注意点2：

如果没有配置ROM Block，则RAM Block的值需相应SWC来保证。在Davinci Developer中可以配置RAMBlock的InitValue，也可以让RAMBlock有一个初始值。

注意点3：

如果，RAM Block的Init value和ROM Block都没有配置且从没有写过NvBlock，那么第一次去读的RAMBlock是.BSS段的一个全局变量（未初始化的全局变量在.BSS段），而MCU上电后会对.BSS段作清零的操作，也就是说我们会读到0。

注意点4：

Q : 新增 NV block ，如何根据需求区分创建 c/s port 还是 s/r port

A : SWC ,NV 同核 C/S, 异核， S/R

注意点5：

Q : NVM 涉及代码有那几部分，位置？

A:

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-21_9-54-11.png)

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-21_9-54-21.png)

注意点6：截图配置项含义

NvMDynamicConfiguration：如果使能此配置，NvM在NvM_ReadAll期间会比较程序当前的NV存储的ID与当前程序配置ID，如果不一致的话，只有NvMResistantTochangedSw配置为Ture的存储块会被读取出来。

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-21_9-56-31.png)

注意点7：截图配置项注意点

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-21_9-57-44.png)

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-21_9-57-54.png)

注意点8：SUM模块和DEM模块这两个模块自建NV BLOCK后会自动生成NVM的CFG配置。

注意点9：复合组件在dev中port mapping

![](../../../../_images/How%20to%20configure%20NvM/image-2026-1-7_15-45-59.png)

![](../../../../_images/How%20to%20configure%20NvM/image-2026-1-7_15-42-58.png)

NVM处理总体逻辑流程图：

NvM 操作时序

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-17_16-38-20.png)

在使用NvM模块时，支持两种类型的RAM同步机制（隐式/显式）。

隐式：

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-27_10-17-1.png)

显式：

![](../../../../_images/How%20to%20configure%20NvM/image-2025-10-27_10-18-29.png)

上述截图参考文章 【AUTOSAR 基础软件】存储栈（NvM、MemIf、Fee）详解_autosar fee-CSDN博客

![](../../../../_images/How%20to%20configure%20NvM/Untitled%20Diagram-1757659830096.png)

FEE

![](../../../../_images/How%20to%20configure%20NvM/image-2025-12-10_10-59-36.png)

Memory Layout of VCUPLUS - XC-CT China - Docupedia

NVM测试方法

Q:如何实现NV BLOCK 写入底层FLS完成回调通知进行DLT_LOG打印,详情如截图；

A:

NVM Readall/writeall 的优化方法，来源：网络上各路大神

1.提升NvM_WriteAll（）速度的办法 -NVM_SET_RAM_BLOCK_STATUS_API 配置为 TRUE，通过调用NvM_SetRamBlockStatus(NvMBlock_ID, TRUE)通知Nvm更新数据时，只更新数据发生改变的NvmBlock。

-NvMBlockUseCRCCompMechanism配置为TRUE，通过比较上次写入数据的CRC与想要更新的数据的CRC进行对比，当CRC不变时，直接跳出写操作。 该操作有一个弊端：当RAM数据发生变化，但是CRC不变的情况下，那么对应的RAM数据将不会被更新。

实例：

```
关于 AHL_IMU_AB NVBLOCK 从应用程序(AHLProcess)到FlsIf_NvM  跨核同步调用RTE NV数据访问实现实现分析如下：调用链应用程序调用    ↓Rte_Call_AHLProcess_AHL_IMU_AB_Get(&data)    ↓跨核IOC发送 (Core4 → Core0)    ↓触发Core0事件，唤醒任务    ↓Core0执行：EEP_AHL_IMU_AB_Get()    ↓Core0读取NV数据到队列    ↓通知Core4完成    ↓Core4等待完成，复制数据    ↓返回给应用程序
```

Rte_Call_AHLProcess_AHL_IMU_AB_Get函数结构分析

1.函数签名 FUNC(Std_ReturnType, RTE_CODE) Rte_Call_AHLProcess_AHL_IMU_AB_Get( P2VAR(EEP_Uint16, AUTOMATIC, RTE_AHLPROCESS_APPL_VAR) arg)

返回类型：Std_ReturnType（标准错误码）

参数：EEP_Uint16*类型指针

这是RTE生成的客户端调用接口

执行流程分析

阶段1：请求发送

Rte_DisableOSInterrupts(); Rte_CS_ClientQueue2_AHLProcess_AHL_IMU_AB_Get.Rte_CallCompleted = !Rte_CS_ClientQueue_AHLProcess_AHL_IMU_AB_Get.Rte_CallCompleted; ret = Rte_IocSend_Rte_CS_ServerQueue_FlsIf_NvM_EEP_AHL_IMU_AB_Get( Rte_CS_ClientConfigIndex_AHLProcess_AHL_IMU_AB_Get);

关键操作：使用Rte_IocSend发送IOC（Inter-OS-Application Communication）请求

完成标志切换：通过切换完成标志来跟踪请求状态

这是跨核通信：Client在Core4，Server在Core0

阶段2：触发服务器端运行

Rte_OsApplication_QM_Core4_InternalEventFlag_OsApplication_QM_Core0_Set_Rte_Ev_Run_FlsIf_NvM_EEP_AHL_IMU_AB_Get(); (void)SetEvent(AplTask_Core0, Rte_Ev_InternalEventHandling_AplTask_Core0);

设置事件标志：通知Core0有任务需要执行

触发事件：唤醒Core0上的任务处理队列

阶段3：等待完成

do /* FETA_RTE_BLOCKING */ { (void)WaitEvent(Rte_Ev_WP_AplTask_10ms_Core4); (void)GetEvent(AplTask_10ms_Core4, &ev); (void)ClearEvent(ev & (Rte_Ev_WP_AplTask_10ms_Core4)); callCompleted = (Rte_CS_ClientQueue_AHLProcess_AHL_IMU_AB_Get.Rte_CallCompleted == Rte_CS_ClientQueue2_AHLProcess_AHL_IMU_AB_Get.Rte_CallCompleted) ? TRUE : FALSE; } while (callCompleted == FALSE);

阻塞等待：在Core4上等待服务器完成处理

轮询检查：通过比较两个队列的完成标志判断是否完成

这是同步调用：客户端会阻塞直到服务器完成

阶段4：返回结果

*arg = Rte_CS_ClientQueue_AHLProcess_AHL_IMU_AB_Get.arg; return ret;

数据复制：从客户端队列复制结果到调用者参数

返回状态：返回操作结果

```

```

```

```

EEP_AHL_IMU_AB_Get(&ClientQueue->arg);调用分析

1.参数类型匹配

调用端： &ClientQueue->arg：取arg成员的地址

假设ClientQueue->arg是EEP_Uint16类型

那么&ClientQueue->arg就是EEP_Uint16*类型

函数声明端： EEP_AHL_IMU_AB_Get(P2VAR(EEP_Uint16, AUTOMATIC, RTE_FLSIF_NVM_APPL_VAR) arg)

P2VAR宏展开为指针：EEP_Uint16*

✅ 类型完全匹配

2. 调用流程可视化

Client应用程序 ↓ 调用 EEP_AHL_IMU_AB_Get(&ClientQueue->arg) ↓ RTE层（生成的代码） ↓ 实际读取：ClientQueue->arg = Rte_NvSWC_Prototype_NVBlockDescriptor_AHL_IMU_AB

3. 内存操作过程

// 1. 调用 EEP_AHL_IMU_AB_Get(&ClientQueue->arg);

// 2. 函数内部（展开后） void EEP_AHL_IMU_AB_Get(EEP_Uint16* arg) { // 宏展开： *(arg) = Rte_NvSWC_Prototype_NVBlockDescriptor_AHL_IMU_AB; // 返回值RTE_E_OK被忽略 }

// 3. 实际发生的操作： // arg指向ClientQueue->arg的内存位置 // 所以等价于： ClientQueue->arg = Rte_NvSWC_Prototype_NVBlockDescriptor_AHL_IMU_AB;

Rte_NvSWC_Prototype_NVBlockDescriptor_AHL_IMU_AB 是AUTOSAR架构中一个关键的系统变量

![](../../../../_images/How%20to%20configure%20NvM/image-2026-1-7_17-58-33.png)

Subsystem-VKM相关的NV block配置实现，*注意： VKID 01-50相似block多，为方便操作封装为1个接口，增加index索引参数，此处的EEP接口会与其他block不同

一个典型的 AUTOSAR架构下跨核（Core4↔Core0）进行NV（NVRAM）数据操作 的实现过程

接口信息： Rte_Call_Rte_EEP_NvacsVKMaryVKIDOpr_Set

实际流程：Core4 (调用方) → RTE跨核通信 → Core0 (执行NV写入)

Phase 1: Core4侧 - SWC发起调用 c // 在Core4的某个SWC中： Std_ReturnType ret = Rte_Call_Rte_EEP_NvacsVKMaryVKIDOpr_Set(dataBuffer, index); Phase 2: Core4侧 - RTE处理 c // 1. 切换双缓冲标志（关闭中断保护） Rte_CS_ClientQueue2_KMEEpAdapter_Rte_EEP_NvacsVKMaryVKIDOpr_Set.Rte_CallCompleted = !Rte_CS_ClientQueue_KMEEpAdapter_Rte_EEP_NvacsVKMaryVKIDOpr_Set.Rte_CallCompleted;

// 2. 复制数据到ClientQueue2 Rte_MemCpy32(Rte_CS_ClientQueue2_KMEEpAdapter_Rte_EEP_NvacsVKMaryVKIDOpr_Set.arg, arg, sizeof(FlsIf_Uint8_Arr26));

// 3. 通过IOC发送到Core0 ret = Rte_IocSend_Rte_CS_ServerQueue_FlsIf_NvM_Rte_EEP_NvacsVKMaryVKIDOpr_Set( Rte_CS_ClientConfigIndex_KMEEpAdapter_Rte_EEP_NvacsVKMaryVKIDOpr_Set); Phase 3: Core4侧 - 触发Core0并等待 c // 1. 设置Core0的内部事件标志 Rte_OsApplication_QM_Core4_InternalEventFlag_OsApplication_QM_Core0_Set_Rte_Ev_Run_FlsIf_NvM_Rte_EEP_NvacsVKMaryVKIDOpr_Set();

// 2. 触发Core0的事件处理任务 (void)SetEvent(AplTask_Core0, Rte_Ev_InternalEventHandling_AplTask_Core0);

// 3. Core4阻塞等待Core0完成 do { // 等待Core0设置的事件 (void)WaitEvent(Rte_Ev_WP_AplTask_1_Core4);  // AplTask_1是Core4的任务 // 检查完成标志 callCompleted = (Rte_CS_ClientQueue_KMEEpAdapter_Rte_EEP_NvacsVKMaryVKIDOpr_Set.Rte_CallCompleted == Rte_CS_ClientQueue2_KMEEpAdapter_Rte_EEP_NvacsVKMaryVKIDOpr_Set.Rte_CallCompleted); } while (callCompleted == FALSE); Phase 4: Core0侧 - 事件处理循环 c // 在Core0的AplTask_Core0任务中： if ((ev_Rte_InternalEventFlag_Rte_Ev_Run_FlsIf_NvM_Rte_EEP_NvacsVKMaryVKIDOpr_Set == 1U)) { // 1. 从IOC接收Core4的请求 while ((cnt < 2U) && (!Rte_IsInfrastructureError( Rte_IocReceive_Rte_CS_ServerQueue_FlsIf_NvM_Rte_EEP_NvacsVKMaryVKIDOpr_Set(&clientIdtmp)))) { // 2. 获取数据（来自Core4的ClientQueue2） ClientQueue2 = Rte_CS_ClientConfig_FlsIf_NvM_Rte_EEP_NvacsVKMaryVKIDOpr_Set[clientId].Rte_ClientQueue2; // 3. 调用FlsIf_NvM的运行体（在Core0执行） Rte_EEP_NvacsVKMaryVKIDOpr_Set(&(&ClientQueue2->arg)[0][0], ClientQueue2->Index); // 4. 更新ClientQueue的完成标志 ClientQueue->Rte_CallCompleted = ClientQueue2->Rte_CallCompleted; // 5. 通知Core4的等待任务 waitingTask = Rte_CS_ClientConfig_FlsIf_NvM_Rte_EEP_NvacsVKMaryVKIDOpr_Set[clientId].Rte_WaitingTaskList[0]; (void)SetEvent(waitingTask, RTE_TASK_WAITPOINT_EVENT_MASK);  // 这是Core4的任务 } } Phase 5: Core0侧 - NV数据写入 c // FlsIf_NvM组件在Core0的实现 void Rte_EEP_NvacsVKMaryVKIDOpr_Set(uint8* arg, uint8 Index) { // 1. 查找NvM Block ID BlockId = NvacsVKMaryVKIDBlockTbl[Index-1]; // 2. 调用Flash接口 (void)FlsIf_WriteBlock(BlockId, (uint8*)arg); }

void FlsIf_WriteBlock(NvM_BlockIdType BlockId, uint8* NvM_SrcPtr) { // 3. 复制数据到RAM镜像 memcpy(local_destptr, NvM_SrcPtr, local_count); // 4. 触发NvM异步写 NvM_WriteBlock(BlockId, NULL_PTR);

}

```

```
