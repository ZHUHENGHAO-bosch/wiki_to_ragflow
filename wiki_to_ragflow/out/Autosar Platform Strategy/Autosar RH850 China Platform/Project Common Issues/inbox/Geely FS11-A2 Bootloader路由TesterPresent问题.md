# Geely FS11-A2 Bootloader路由TesterPresent问题

> Source: /spaces/CARSFW/pages/3606988735/Geely+FS11-A2+Bootloader%E8%B7%AF%E7%94%B1TesterPresent%E9%97%AE%E9%A2%98
> Last modified: 2023-11-03T07:57:30.000+01:00

---

1. 问题描述

吉利FS11-A2产线电检流程报AUD刷写失败错误。分析DoIP报文和CAN报文，发现DHU未能路从DoIP路由功能寻址的TesterPresent诊断请求到0x7FF的CAN报文，导致AUD退出SWDL模式。失效发生概率为1/10。

2. 问题分析

由于以下原因：

a- 问题只在使用特定的DSA刷写流程中出现，该流程中包含持续120s以上对AUD转发DoIP功能寻址的023E80诊断请求的时间段。

b- 问题发生时，CAN总线能观察到DHU发出的，周期为400ms的用于保持AUD唤醒的0x53F报文NMCanFrame。

因此初步判断问题不是出在CAN输出端，而是从DoIP-PDUR-CanTP-CanIf-CAN的路由过程出现问题。

3. 临时措施

为了安抚产线抱怨，决定先采用以下临时补救措施在产线进行压测：

a- 定义类型为Can_PduType的TPCanFrame变量，ID为0x7FF，包含023E80诊断请求内容，设置为3000ms的发送周期，通过变量TPCanFrame开关使能或关闭发送。

b- 在CanIf_Transmit函数中，判断当收到来自CanTp转DoIP的，ID为0x7FF、包含SDU字节为023E80的Pdu发送请求时，使能定时发送TPCanFrame开关。

c- 在CanIf_Transmit函数中，判断当收到来自CanTp转DoIP的，ID为0x712，或者ID为0x7FF，但SDU字节为非023E80的Pdu发送请求时，关闭定时发送TPCanFrame开关。

d- 在FblCwInternalMainFunctionTimerTask函数调用中，以1ms的周期累加计时器，当计时器达到3000ms时发送TPCanFrame到CAN总线，用于补救由于缺失TesterPresent报文的路由而导致的AUD会话模式跳转。

该Workaround软件在产线压测100轮左右，只发生一起电检AUD刷写失败的报错，并且由于缺少必要的记录，这起失效暂时不能定位为DHU的原因。

4. 查找原因

由于BootLoader软件运行在RAM中，增加DLT打印需要调整软件模块在内存中的部署，风险和工作量较大，因此先采用以下方式用于查找根本原因：

a- 利用TPCanFrame中除了023E80外剩余字节中的四个字节，以累加路由路径中关键函数节点调用次数的方式，判断诊断报文路由转发事务时，造成路由失败的软件调用缺失环节。

b- 在每次从DoIP收到功能寻址的023E80诊断请求开始，至路由到CAN结束，整个事务发生的过程中，分别在以下位置记录累加值：

- DoIPInt_Rx_CopyHeader，记录DoIP接收到功能寻址TesterPresent调用的次数。

- PduR_RmTp_CopyRxData，记录DoIP路由到CanTp的调用次数。

- CanTp_Transmit，记录CanTp请求发送到CanIf的调用次数。

- Can_Write，记录请求发往Can总线的调用次数

c- 理论上当路由失效发生时，可以通过以上四个累加值来判断路由过程中丢失的调用节点，如果四个值完全一样，则认为DoIP的接收端未能识别功能寻址TesterPresent请求。

d- 将发送TPCanFrame的周期设置为5100ms，故意使产线电检流程发生可识别的报错，以分析问题原因。

该RootCause软件在产线复测10次左右成功复现了问题，但是观察到CAN总线上有连续8s未出现应转发的0x7FF的TesterPresent报文。这意味着应该在转发一次TesterPresent后的5100ms时间点上发出的包含函数调用累加信息的报文没有按软件的设计发出。

同时发现由于代码设计错误，在Workaround软件中，FblCwInternalMainFunctionTimerTask对发送TPCanFrame的计时器被错误的以5倍的速度累加，即实际Workaround软件发送TPCanFrame的周期为600ms，而非定义的3000ms。所以用Workaround程序压测时只出现一起疑似DHU导致的电检AUD刷写失败的报错。

分析代码发现，用于和AUD保持唤醒功能的0x53F报文并不是吉利SDB中定义的PDU，而是AUD私下要求DHU外发的报文，Bootloader的Davinci工程中没有此PDU。在运行时通过直接调用Can_Write函数发送0x53F的NMCanFrame，所以无法在CanIf中给它分配CanIfBuffer的空间。因此推测在持续运行了120s以上的工况下偶发了连续几次占用了0x7FF报文的TxBuffer的情况。

根据上述推测，决定在持续转发DoIP功能寻址的TesterPresent诊断请求时，暂停发送0x53F的NMCanFrame的方式加以验证。在本节用于查找根本原因的软件修改基础上，增加以下措施：

e- 定义用于使能和关闭NMCanFrame发送的开关，U8型变量NMCanEnabled。

f- 在CanIf_Transmit函数中，判断当收到来自CanTp转DoIP的，ID为0x7FF、包含SDU字节为023E80的Pdu发送请求时，使能定时发送TPCanFrame开关，并置NMCanEnabled为0。

g- 在CanIf_Transmit函数中，判断当收到来自CanTp转DoIP的，ID为0x712，或者ID为0x7FF，但SDU字节为非023E80的Pdu发送请求时，关闭定时发送TPCanFrame开关，并置NMCanEnabled为1。

h- 在FblCwInternalMainFunctionTimerTask函数调用中，以1ms的周期累加计时器，当计时器达到5100ms时发送TPCanFrame到CAN总线，用于观察路由路径中函数调用节点累加数值。并且判断在NMCanEnabled为1时，发送0x53F的NMCanFrame，在NMCanEnabled为0时，不发送0x53F的NMCanFrame。

该软件在产线压测100轮以上，未发生电检AUD刷写失败的失效，因此认为在路由TesterPresent过程中停止发送0x53F的NMCanFrame是解决本问题的有效手段。

5. 解决方案

由于该失效和产线DSA刷写流程有关，一方面需要推动吉利产线优化DSA流程，另一方面需要将解决方案横展到所有车型分支上。

结合Workaround软件和RootCause软件的实施措施，将以下变更投入到正式代码中：

a- 定义类型为Can_PduType的TPCanFrame变量，ID为0x7FF，包含023E80诊断请求内容，设置为2100ms的发送周期。

b- 定义用于使能和关闭NMCanFrame发送的开关，U8型变量NMCanEnabled。

c- 在CanIf_Transmit函数中，判断当收到来自CanTp转DoIP的，ID为0x7FF、包含SDU字节为023E80的Pdu发送请求时，使能定时发送TPCanFrame开关，并置NMCanEnabled为0。

d- 在CanIf_Transmit函数中，判断当收到来自CanTp转DoIP的，ID为0x712，或者ID为0x7FF，但SDU字节为非023E80的Pdu发送请求时，关闭定时发送TPCanFrame开关，并置NMCanEnabled为1。

e- 在FblCwInternalMainFunctionTimerTask函数调用中，以1ms的周期累加计时器，当计时器达到2100ms时发送TPCanFrame到CAN总线，用于补救由于缺失TesterPresent报文的路由而导致的AUD会话模式跳转。并且判断在NMCanEnabled为1时，发送0x53F的NMCanFrame，在NMCanEnabled为0时，不发送0x53F的NMCanFrame。

f- 删除用于查找原因的函数调用节点累加代码。

6. 代码提交

请参考：

[MAIN_DEV]Solution of tester present gateway on CAN in BL (I82ae7b07) · Gerrit Code Review (bosch.com)
