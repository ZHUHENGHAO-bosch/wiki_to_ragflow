# How to configure Multi-core COM on VCUPLUS

> Source: /spaces/CARSFW/pages/5494351317/How+to+configure+Multi-core+COM+on+VCUPLUS
> Last modified: 2025-03-13T09:29:49.000+01:00

---

只分 Com

|   |   |
| --- | --- |
| Com | 添加MainFunctionCore4并将Partition改为QM Core4 |
| Com IPdus | 使用 Channel 过滤 VKCAN 的 Pdu ， 移到MainFunctionCore4上，并移动Partition核为Core4 |
| EcuC | 移动上一步对应的 EcuC 到 QM Core4 |
| PduR | PduR 改为 DEFFER 使用 Slove 创建 Queue ，并填写 Queue Size 2000 创建多核队列后，需要添加手写代码，否则编译不过 在Autosar\BSW\Vector_bsw\Components\PduR\Implementation\PduR_McQ.c 定义如下函数： FUNC ( void , PDUR_CODE) Appl_DataSyncBarrier ( void ) { } ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47.png) ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-1.png) |
|  |  |
| MemMap | Slove 可以解决 |
| RTE13055 | 在 Runtion System 中， Add Task Mapping 如果加了其他核，需要在 OS Tasks 中新建 Tasks ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-2.png) 创建一个 task ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-3.png) ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-4.png) ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-5.png) |
| Cmake | Compare GenData 和 GenDataTemp 添加新生成的文件 ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-6.png) ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-7.png) ![](../../../../_images/How%20to%20configure%20Multi-core%20COM%20on%20VCUPLUS/image-2025-3-13_16-23-47-8.png) |
