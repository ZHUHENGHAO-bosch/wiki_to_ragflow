# Arm Scatter file - How To

> Source: /spaces/CARSFW/pages/4677107607/Arm+Scatter+file+-+How+To
> Last modified: 2024-09-05T04:14:05.000+02:00

---

## Overview

This page is to summarize how to define regions in Scatter file. Since Arm compiler use Scatter files to link the regions it is important to understand how the scatter file works

## Scatter file

#### How to specify the scatter file in cmake file

Use the below command to set the scatter file in cmake

--scatter=filename

SET(CMAKE_EXE_LINKER_FLAGS         "--scatter=${SCAT_FILE} --map --entry=EL2_Reset_Handler ${CMAKE_LINKER_FLAGS} CACHE STRING "Flags" FORCE)

#### Common link option in Arm

#### What the linker does to create an image?

The linker takes object files that a compiler or assembler produces and combines them into an executable image. The linker also uses a memory description to assign the input code and data from the object files to the required addresses in the image

#### What we can control with a scatter file?

A scatter file gives us the ability to control where the linker places different parts of our image for your particular target

Interaction of OVERLAY and PROTECTED attributes with armlink merge options"

The OVERLAY and PROTECTED scatter-loading attributes modify the behavior of the armlink options --merge and --merge_litpools.

![](../../../_images/Arm%20Scatter%20file%20-%20How%20To/image-2024-9-4_19-34-11.png)

### Hints for Creating Scatter file (scatter.scat):

Syntax for Creating memory region

![](../../../_images/Arm%20Scatter%20file%20-%20How%20To/image-2024-9-4_19-36-57.png)

### Load and Execute region

Scatter-loading defines two types of memory regions

- Load regions containing application code and data at reset and load-time
- Execution regions containing code and data when the application is executing. One or more execution regions are created from each load region during application startup

A single code or data section can only be placed in a single execution region. It cannot be split.

During startup, the C library initialization code in __main carries out the necessary copying of code/ data and zeroing of data to move from the image load view to the execute view

In a typical embedded system, all the program & data is stored in some Non-volatile memory when the system is powered off. However some of the data or code may be moved into system SRAM (volatile mem), before it is executed (if code) or before it is used (if data), when the system is powered-ON.

Sections of code can have different address at 'load' time, which is in NVM than at 'execution' time, which is typically somewhere in the SRAM.

So the program image can have parts for which the 'Load Region = Execute Region', and this part of the code is 'Executed-In-Place' XIP. For certain other parts of the code the 'Load Region is not equal to Execute Region', and this part of the code is not executed-in-place

### Root region

A root region is a region with the same load and execution address. The initial entry point of an image must be in a root region

If the initial entry point is not in a root region, the link fails and the linker gives an error message

### Load and Execute Region - Same address

To make the execution region address the same as the load region address, either:

- Specify the same numeric value for both the base address for the execution region and the base address for the load region Or
- Specify a +0 offset for the first execution region in the load region.

![](../../../_images/Arm%20Scatter%20file%20-%20How%20To/image-2024-9-5_10-14-0.png)

### Effect of the FIXED attribute on a root region

We can use the FIXED attribute for an execution region in a scatter file to create root regions that load and execute at fixed addresses. Use the FIXED execution region attribute to ensure that the load address and execution address of a specific region are the same. We can use the FIXED attribute to place any execution region at a specific address in ROM.

![](../../../_images/Arm%20Scatter%20file%20-%20How%20To/image-2024-9-4_20-11-52.png)

![](../../../_images/Arm%20Scatter%20file%20-%20How%20To/image-2024-9-4_20-13-33.png)

### The vector table

All Arm systems have a vector table. It does not form part of the initialization sequence, but it must be present for an exception to be serviced. It must be placed at a specific address, usually 0x0. To do this you can use the scatter-loading +FIRST
