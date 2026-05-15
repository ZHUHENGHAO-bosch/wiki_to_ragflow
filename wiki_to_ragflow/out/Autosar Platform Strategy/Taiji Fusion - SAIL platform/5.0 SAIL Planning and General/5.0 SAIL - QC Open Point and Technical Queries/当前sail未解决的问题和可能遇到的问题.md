# 当前sail未解决的问题和可能遇到的问题

> Source: /spaces/CARSFW/pages/5269457147/%E5%BD%93%E5%89%8Dsail%E6%9C%AA%E8%A7%A3%E5%86%B3%E7%9A%84%E9%97%AE%E9%A2%98%E5%92%8C%E5%8F%AF%E8%83%BD%E9%81%87%E5%88%B0%E7%9A%84%E9%97%AE%E9%A2%98
> Last modified: 2025-03-10T10:15:03.000+01:00

---

## 1. 现状

BOSCH开发SAIL有很多限制，根据跟高通的沟通，SAIL的定位不是普通的外部MCU，而是做一些功能安全机制，使SOC整体达到ASIL B。

1. 高通不提供SAIL的完整的芯片手册。仅根据某些功能，提某些供功能的文档介绍；不开放sail hypervisor。
2. 高通支持力度不够。给高通提的3个CR，高通都拒绝掉了。
3. 高通支持SAIL的CE能力不够。在开发SAIL的过程中，通过Case沟通遇到的问题，高通CE经常回复前后矛盾，可信度不高。经常需要bosch根据文档/代码提出质疑后，CE才能给出可信的回复，沟通效率低。

## 2. 当前识别到的限制

1. SAIL MCAL不支持PWM。 相关寄存器受到EL2保护，bosch手动改会导致系统crash。
2. SAIL MCAL不支持ICU(Interrupt Capture Unit)。
3. SAIL NorFlash 驱动有8字节对齐限制。该驱动在EL2, bosch没办法修改。影响NVM。
4. SAIL 总共3M  SRAM+ 3*128K TCM。高通介绍 SAIL Application支持运行在DDR上，目前我们还做过测试。
5. SAIL 需要用Arm Clang 编译器 ，版本ArmCompilerforEmbeddedFuSa_6.16.2。
6. SAIL和TC387只有uart，不支持高带宽数据的传输。

## 3. 当前识别到的问题

1. EL1的MPU权限问题。EL1的地址空间的权限是在sail hypervisor里定义的，hypervisor是黑盒，bosch唯一可配置的途径是dts文件。当前dts文件中显式定义的地址空间有限，经测试和跟高通CE沟通，bosch只能修改dts显式定义的地址段的权限；不能新增地址段并赋予权限，会reset。 —- 建议高通提供芯片手册和hypervisor代码
2. 当配置不当或者其他原因会进sail hypervisor，然后reset。hypervisor是黑盒，我们不知道reset原因，不知道问题如何分析。只能跟高通提case —  建议高通提供芯片手册和hypervisor代码
3. SAIL和MD之前需要哪些数据交互,虽然现在sail bringup后，SAIL暂时工作正常，MD也没出现reset。但不知道如何检查通信完整性。 — 建议高通资深工程师参与bosch的问题回复
4. SAIL计划用ETAS Autosar。目前了解到ETAS Autosar对于PATAC 特有模块 SUM模块，并没有现成的软件。ETAS开发SUM也需要时间。-- 需要项目确定要开发SAIL后，给ETAS提需求，ETAS才开始开发SUM

## 4. 还没开发，将来可能遇到的问题

1. Application 跑在DDR上时，可能会有坑，需要高通支持。当前软件小，所有软件都跑在SAIL内部的SRAM上，随着后续AS等应用程序的集成，SRAM空间不够用，会把AS等应用程序搬到DDR上运行，可能会遇到一些问题
2. STR，现在bosch开发的sail还没做STR功能，进／退STR会有很多关监控逻辑以及跟MD的通信。可能会遇到一些问题需要高通支持。
3. 升级，MD升级sail功能还没开发。据了解，MD会调用一些指令来跟SAIL通信，刷写对应的sail分区和backup分区，可能会遇到一些问题，需要高通支持。
4. 后续集成功能安全机制时，可能会遇到各种报错，需要高通支持。
5. 多核的使用。当前启用了3个核，但只在其中一个核上开发程序。将来在3个核上同时运行时，核间通信等等，可能会遇到一些问题需要高通支持。
6. security开发可能会遇到一些问题，需要高通支持
