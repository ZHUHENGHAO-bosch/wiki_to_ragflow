# How to generate sailhyp.elf with local *.dts

> Source: /spaces/CARSFW/pages/4918261390/How+to+generate+sailhyp.elf+with+local+.dts
> Last modified: 2024-11-21T06:47:56.000+01:00

---

Qualcomm don't release hypervisor source code to us. We can only modify limited configurations of hypervisor by *.dts.

![](../../../_images/How%20to%20generate%20sailhyp.elf%20with%20local%20_.dts/make%20sailhypdts.png)

The currently released versions of sailhyp_nosym.elf are for single-core, and the multi-core versions still need to be released by Qualcomm in the future.

## 1. Prepareration

Please make sure you can build and generate autosarsailbaremetal.elf refer to How to setup QC SAIL build environment

## 2. generate sailhyp.elf

Take r00010.1 ES08 for example, because it can find autosar version sailhyp_nosym.elf since the ES08.

### 2.1. download sailhyp_nosym.elf

Download sailhyp_nosym.elf from snapdragon-auto-hqx-4-5-6-0_test_device_autosar /sail_autosar / sail_proc  /build / ms / bin  /SAIL_CASAR / DEBUG / lemans

https://chipcode.qti.qualcomm.com/robert-bosch-gmbh/snapdragon-auto-hqx-4-5-6-0_test_device_autosar/tree/r00010.1

![](../../../_images/How%20to%20generate%20sailhyp.elf%20with%20local%20_.dts/image-2024-10-25_10-38-49.png)

### 2.2. copy sailhyp_nosym.elf

Copy sailhyp_nosym.elf to  sail_autosar\sail_proc\build\ms\bin\SAIL_CASAR\DEBUG\lemans

### 2.3. modify  lemansau-sailhyp-autosar.dts

Modify dts as your requirement. dts located in sail_autosar/sail_proc/BSP/scripts/lemansau-sailhyp-autosar.dts

### 2.4. generate sailhyp.elf

ES06 and ES08 makefile script is different, please follow as below.

ES08 Project （r00010.1 ES08）:

![](../../../_images/How%20to%20generate%20sailhyp.elf%20with%20local%20_.dts/image-2024-10-25_10-46-31.png)

ES06 Project （r00008.1 ES06）:

![](../../../_images/How%20to%20generate%20sailhyp.elf%20with%20local%20_.dts/image-2024-11-21_13-5-51.png)

After finish, sailhyp.elf will generate

![](../../../_images/How%20to%20generate%20sailhyp.elf%20with%20local%20_.dts/image-2024-10-25_10-49-23.png)

we should use signed/sailhyp.elf

attachments：

given by Case 07529936

multi-core sailhyp_nosym.elf : sailhyp_nosym.elf

multi-core  DTS                      : lemansau-sailhyp-autosar.dts.multi-core.workok.bak
