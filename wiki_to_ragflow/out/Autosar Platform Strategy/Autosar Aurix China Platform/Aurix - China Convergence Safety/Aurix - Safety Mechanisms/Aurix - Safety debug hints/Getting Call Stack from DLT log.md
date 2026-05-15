# Getting Call Stack from DLT log

> Source: /spaces/CARSFW/pages/3308952119/Getting+Call+Stack+from+DLT+log
> Last modified: 2023-08-02T05:11:03.000+02:00

---

### Overview

The below wiki page explains the overview of getting the call stack for issue anlaysis

Getting Complete Call stack - Aurix - XC-CT China - Docupedia (bosch.com)

Getting instruction address which caused NMI trap - XC-CT China - Docupedia (bosch.com)

Now this logic is implemented to log the call stack in case of WDG issues in Aurix China Convergence projects. Below wiki explains the log format

SM06_Error Log Format - GEN4 generic - Docupedia (bosch.com)

Now this wiki page is to explain how to re-create the call stack from DLT log using Lauterbach and Trace 32.

### Prerequisite

OUT binary - We need the out file of the binary in which the issue happens and log was stored

#### Steps:

Step 1: Connect Trace32 to the target

Step 2: Load the out file in which issue was reported by using the command

Data.LOAD.elf xyz.out /NoCODE

Step 3: Get the call stack information from DLT log as explained in SM06_Error Log Format - GEN4 generic - Docupedia (bosch.com)

For example,

114623 2023/08/01 14:23:02.164233 0.0246 23 ECU1 SSH_ SEH_ 4132 log info verbose 1 Fusa_GID_1_SID_1#51132A08004A808013656A801B0CAE801B0D7C8014308C801DE4EEAE#

The call stack information from above log is

8013656A 801B0CAE 801B0D7C 8014308C 801DE4EE

Step 4: Get the call stack information using Dump window.

- Open dump window - View → Dump
- Paste the address that we got from step 3

![](../../../../../_images/Getting%20Call%20Stack%20from%20DLT%20log/image-2023-8-2_10-55-20.png)

- Right click on the address and click on Display Memory → View

![](../../../../../_images/Getting%20Call%20Stack%20from%20DLT%20log/image-2023-8-2_10-56-6.png)

- View window will show the instruction and function details

![](../../../../../_images/Getting%20Call%20Stack%20from%20DLT%20log/image-2023-8-2_10-57-46.png)

- Repeat the same steps for remaining addresses that we got from step 3, we can get complete call stack information

![](../../../../../_images/Getting%20Call%20Stack%20from%20DLT%20log/image-2023-8-2_11-2-11.png)
