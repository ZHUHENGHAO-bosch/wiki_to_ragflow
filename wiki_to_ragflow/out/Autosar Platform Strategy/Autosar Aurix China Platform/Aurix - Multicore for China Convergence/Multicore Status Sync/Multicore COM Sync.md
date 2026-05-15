# Multicore COM Sync

> Source: /spaces/CARSFW/pages/2480373915/Multicore+COM+Sync
> Last modified: 2023-01-04T12:19:52.000+01:00

---

Plan for Communication stack relocation in Zeekr:

Current status: FR, CAN and LIN along with vDataHandler is in Core 0

Goal: Move FR complete stack to Core 1

Limitations:

- We cannot use RTE between COM and Application SWCs (Third party), which means complete application will be in Core 1

Step 1: FR stack to Core 1 and let vDataHandler and Com in Core 0

![](../../../../_images/Multicore%20COM%20Sync/image2022-10-27_17-10-40.png)

Step 2: Move Com to Core 1, also the vDataHandler and application

Prerequisite: INC multi core capability should be available

Note:

For Diagnostic data from SoC we need a CDD in Core 0
