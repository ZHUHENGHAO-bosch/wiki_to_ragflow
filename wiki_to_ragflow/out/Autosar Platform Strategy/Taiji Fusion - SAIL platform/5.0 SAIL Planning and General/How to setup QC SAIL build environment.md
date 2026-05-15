# How to setup QC SAIL build environment

> Source: /spaces/CARSFW/pages/4918257815/How+to+setup+QC+SAIL+build+environment
> Last modified: 2024-11-21T09:21:41.000+01:00

---

1. Build environment preparation 1.1. Install Cygwin with the make and gccmakedep packages. (you can download Cygwin here: Cygwin setup-x86_64.exe) 1.2. Install the Qualcomm Package Manager (QPM) (qpm3) desktop application. 1.3. Use QPM to install LLVM Arm Snapdragon 17.0. 1.4. copy dtc.exe to C:\cygwin64\bin (cygwin path you just installed ) 1.5. Add Cygwin, Python to environment variable. 2. Source code preparation 2.1. download code 2.2. modify script 2.3. copy toolchain 2.3.1. create "toolchain"folder \sail_autosar\sail_proc 2.3.2. copy \temp_j6e_mcu\Tools\ArmCompilerforEmbeddedFuSa_6.16.2 to \sail_autosar\sail_proc\toolchain ( you should have access of temp_j6e_mcu repo) 2.3.3. rename ArmCompilerforEmbeddedFuSa_6.16.2 to 6.16.2_win 3. build & generate 3.1. setupenv.bat 3.2. make autosarsailbaremetal 4. Trouble Shoot 4.1. If python3 not found in your cmd window when "setupenv.bat"

This wiki help to setup the build environment of Qualcomm SA8775/SA8255 SAIL , and build & generate sailbaremetal.elf based on QC sail source code.

## 1. Build environment preparation

We refered to Chapter 2.2 in SAIL MCAL User Guide( 80-42846-146 Rev . AC) but not followed it completely.

### 1.1. Install Cygwin with the make  and gccmakedep packages. (you can download Cygwin here: Cygwin setup-x86_64.exe )

Please ingore step 2,3 in Chapter 2.2.1.1 in SAIL MCAL User Guide

### 1.2. Install the Qualcomm Package Manager (QPM) (qpm3) desktop application.

### 1.3. Use QPM to install LLVM Arm Snapdragon 17.0.

### 1.4. copy dtc.exe to C:\cygwin64\bin (cygwin path you just installed )

### 1.5. Add Cygwin, Python to environment variable.

my PATH environment for reference.

![](../../../_images/How%20to%20setup%20QC%20SAIL%20build%20environment/image-2024-10-24_21-1-24.png)

## 2. Source code preparation

### 2.1. download code

Take r000010.1 ES08 version for example

- ES08  can generate sailhyp.elf with local dts

1. QC chipcode: https://chipcode.qti.qualcomm.com/robert-bosch-gmbh/snapdragon-auto-hqx-4-5-6-0_hlos_dev_autosar/tree/r00010.1
2. Bosch Gerrit： https://rbcm-gerrit.de.bosch.com/plugins/gitiles/external/qualcomm/qnx/snapdragon-auto-hqx-4-5-6-0_hlos_dev_autosar/

### 2.2. modify script

replace below two files locate in \sail_autosar\sail_proc\build\ms

CreatePackFile.py

setupwin.py

### 2.3. copy toolchain

#### 2.3.1. create "toolchain"folder \sail_autosar\sail_proc

#### 2.3.2. copy \temp_j6e_mcu\Tools\ArmCompilerforEmbeddedFuSa_6.16.2 to \sail_autosar\sail_proc\toolchain ( you should have access of temp_j6e_mcu repo)

#### 2.3.3. rename ArmCompilerforEmbeddedFuSa_6.16.2 to 6.16.2_win

![](../../../_images/How%20to%20setup%20QC%20SAIL%20build%20environment/image-2024-10-24_20-20-56.png)

## 3. build & generate

move to \sail_autosar\sail_proc\build\ms, put commands in CMD

### 3.1. setupenv.bat

![](../../../_images/How%20to%20setup%20QC%20SAIL%20build%20environment/image-2024-10-24_20-28-52.png)

### 3.2. make autosarsailbaremetal

![](../../../_images/How%20to%20setup%20QC%20SAIL%20build%20environment/image-2024-10-24_20-31-38.png)

after build complete, will print log like this

![](../../../_images/How%20to%20setup%20QC%20SAIL%20build%20environment/image-2024-10-24_20-43-12.png)

and generate  files in \sail_autosar\sail_proc\build\ms\bin

![](../../../_images/How%20to%20setup%20QC%20SAIL%20build%20environment/image-2024-10-24_20-44-43.png)

## 4. Trouble Shoot

### 4.1. If python3 not found in your cmd window when "setupenv.bat"

Try to use this CMD  " mklink python3.exe C:\toolbase\python\3.6.6.2.6\python-3.6.6.amd64\python.exe "
