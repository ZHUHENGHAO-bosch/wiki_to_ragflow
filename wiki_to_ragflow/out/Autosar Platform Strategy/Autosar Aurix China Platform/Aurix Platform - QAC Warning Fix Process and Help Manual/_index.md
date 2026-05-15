# Aurix Platform - QAC Warning Fix Process and Help Manual

> Source: /spaces/CARSFW/pages/2929574733/Aurix+Platform+-+QAC+Warning+Fix+Process+and+Help+Manual
> Last modified: 2023-07-05T12:02:09.000+02:00

---

## QAC Waring Fix Process

![](../../../_images/Aurix%20Platform%20-%20QAC%20Warning%20Fix%20Process%20and%20Help%20Manual/QAC%20Warning%20Fix%20Process.png)

## QAC Warning Fix Help Manual

Note1: Write the Root Cause and Solution in Chinese.

Note2: Whistler is the guy who initially fixed the warning and also responsible for explain the waring to others.

| QAC Warning Id | Whistler | Root Cause | Solution |
| --- | --- | --- | --- |
| m3cm-2.4.0-5209 | ZHAO Joanna (XC-CP/ESW2-CN) | 使用basic type: int/char/.... 考虑代码的可移植性，我们不能直接使用basic type, 需要使用Typedef 的类型； | 将basic type修改为 Typedef的类型，例如：sint32/uint8/.... |
| qac-9.7.0-3415 | TAN Shanhe (XC-CP/ESW2-CN) | 如黄色选中行，\|\|右边的部分在左边为TRUE的时候就不会被执行，如果其中的函数中有一些赋值类的操作，将没有办法执行直接跳过 ![](../../../_images/Aurix%20Platform%20-%20QAC%20Warning%20Fix%20Process%20and%20Help%20Manual/image-2023-4-12_19-34-20.png) | 将函数提前执行，保证所有函数都能够执行到。 ![](../../../_images/Aurix%20Platform%20-%20QAC%20Warning%20Fix%20Process%20and%20Help%20Manual/image-2023-4-12_19-39-33.png) |
| qac-9.7.0-2986 | LI Minsheng (XC-CP/ESW2-CN) | QAC分析1615行的或操作是冗余的，原因是1610行 *channelStatus = 0x00； 0或上 channelStatus_as[index].isOpen，实际上等效于 *channelStatus = channelStatus_as[index].isOpen; ![](../../../_images/Aurix%20Platform%20-%20QAC%20Warning%20Fix%20Process%20and%20Help%20Manual/image-2023-7-5_17-58-15.png) | 将 *channelStatus \|= channelStatus_as[index].isOpen; 改为 *channelStatus = channelStatus_as[index].isOpen; |
