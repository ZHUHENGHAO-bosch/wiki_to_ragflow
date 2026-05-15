# Aurix - How to Update UCB-BMHD

> Source: /spaces/CARSFW/pages/3057790138/Aurix+-+How+to+Update+UCB-BMHD
> Last modified: 2024-12-31T07:06:17.000+01:00

---

## Introduction

UCB (User configuration Block) has very important configuration based on which Aurix chip acts. This wiki page explains how to update the BMHD in UCB binary

### BMHD information

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2023-5-22_11-22-11.png)

### Steps to update BMHD:

If you update wrong information in BMHD and flash there is a high chance the board can go into unrecoverable error state (After which we need to erase using Memtool and miniwiggler)

Make sure the changes are updated in both Original and Copy of BMHD. As shown in below table, If BMHD0_ORIG is in Error state than firmware will check the BMHD0_COPY

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2023-5-22_11-33-44.png)

Repo path where the BMHD binary shall be placed: Project\Config\Autosar\laut-tc3xx\UCB\BMHD

Since we don't have any script to write the UCB, below is one of the workarounds to update BMHD

Step 1:

Flash the current binary using Lauterbach Change the required value in Trace32 → Follow below steps

1. Click on Check
2. Click on edit
3. Change the required value
4. Click on update
5. Check the BMI, CRCBMHD, CRCBMHD_N

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2023-5-22_13-6-57.png)

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2023-5-22_13-7-17.png)

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2023-5-22_13-7-31.png)

Step 2:

We can update UCB srec in two ways

1. Dump the UCB block from Trace32 (Easy way)
2. Change the existing UCB via HEX view or

1. Dump the UCB block from Trace32

After updating the UCB in Trace32, Now dump the UCB into a file

Data.save.IntelHex Dflash_ucb 0xAF402200–0xAF4023FF

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2024-12-31_14-2-13.png)

Now the UCB will be in the name of Dflash_ucb in Build folder

Now open the UCB in hexview. We can see the start address is not correct.

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2024-12-31_14-3-12.png)

Now double clock in start address and give the proper start address in new address

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2024-12-31_14-5-6.png)

After this start address will be ok and we can use this UCB hex file for project

2. Change the existing UCB via HEX view

UCB binary Path: Project\Zeekr_May20\Config\Autosar\laut-tc3xx\UCB

BMHD binary path: Project\Config\Autosar\laut-tc3xx\UCB\BMHD

Make sure both UCB.SREC and BMHD (ORIG and COPY) binaries are modified

Open the UCB from Repo in Hexview

Below picture shows the mapping

Now Edit the values in Hex view and save it (Make sure CRCBMHD and CRCBMHD_N is updated as well)

Careful on the Endianness

![](../../../_images/Aurix%20-%20How%20to%20Update%20UCB-BMHD/image-2023-5-22_13-8-34.png)

Step 3:

Flash the new UCB and make sure the data is updated properly in UCB Trace 32 window

Step 4:

Deliver the BMHD binary to repo and inform all stakeholders
