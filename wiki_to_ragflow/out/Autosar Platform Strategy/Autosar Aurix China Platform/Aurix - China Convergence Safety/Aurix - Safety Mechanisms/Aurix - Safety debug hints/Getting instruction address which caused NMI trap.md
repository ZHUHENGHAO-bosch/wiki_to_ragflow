# Getting instruction address which caused NMI trap

> Source: /spaces/CARSFW/pages/3251704619/Getting+instruction+address+which+caused+NMI+trap
> Last modified: 2023-07-18T12:37:05.000+02:00

---

### Overview

It is very difficult to find the root cause in case of issues like internal WDG Reset since we cannot get any proper information.

Below summary explains how to get the instruction address which caused NMI trap. This will help us to get some information on the code which cause issue like WDG Reset etc..,

So before going to the steps we need to know about CSA (Context Save Area) in detail

### CSA (Context Save Area)

The Aurix architecture uses linked lists of fixed-size Context Save Areas. A CSA is 16 words of memory storage, aligned on a 16-word boundary. Each CSA can hold exactly one upper or one lower context. CSAs are linked together through a Link Word

When an interrupt or trap (for example NMI or SYSTRAP) occurs, the processor saves the upper context of the current task in memory, suspends execution of the current task and then starts execution of the interrupt or trap handler.

Now we are going to use this information in CSA to get the exception address that caused trap

### How can we get the CSA address of previous call stack (Before NMI occurred)

PCXI (Previous Context Information) gives the CSA address where the previous call stack information is stored in memory.

![](../../../../../_images/Getting%20instruction%20address%20which%20caused%20NMI%20trap/image-2023-7-18_18-36-44.png)

## Steps to get Exception instruction address from PCXI

Step 1: In the NMI handler, read the PCXI address value

Step 2: Calculate the CSA address from PCXI

![](../../../../../_images/Getting%20instruction%20address%20which%20caused%20NMI%20trap/image-2023-7-17_13-43-38.png)

Step 3: Read the third byte from the CSA address which is calculated in step 2 (This byte has the RA (Return address))

![](../../../../../_images/Getting%20instruction%20address%20which%20caused%20NMI%20trap/image-2023-7-17_13-55-50.png)

### Demo example

Example Macro to get CSA address as in Step 2

![](../../../../../_images/Getting%20instruction%20address%20which%20caused%20NMI%20trap/image-2023-7-17_13-45-55.png)

Example code which gives CSA address and mapping to instruction address which caused WDG

![](../../../../../_images/Getting%20instruction%20address%20which%20caused%20NMI%20trap/image-2023-7-17_13-54-57.png)

![](../../../../../_images/Getting%20instruction%20address%20which%20caused%20NMI%20trap/image-2023-7-17_15-45-24.png)
