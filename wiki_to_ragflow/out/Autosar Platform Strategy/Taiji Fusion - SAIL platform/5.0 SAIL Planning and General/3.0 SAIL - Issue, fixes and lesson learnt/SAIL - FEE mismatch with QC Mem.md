# SAIL - FEE mismatch with QC Mem

> Source: /spaces/CARSFW/pages/4988269439/SAIL+-+FEE+mismatch+with+QC+Mem
> Last modified: 2024-11-14T06:56:19.000+01:00

---

## Issue 1: QC MemAcc not supporting couple of AR standard APIs which is needed bu Cubas FEE

### Autosar MemAcc overview (R21-11)

![](../../../../_images/SAIL%20-%20FEE%20mismatch%20with%20QC%20Mem/image-2024-11-14_13-35-45.png)

- The dependency relationship between MemAcc and FEE.

The MemAcc module follow the Autosar R22-11 specification, but currently missing two standard interfaces implementation:

1. MemAcc_Compare() - Triggers a job to compare the passed data to the memory content of the provided address area. The job terminates, if all bytes matched or a difference was detected. The result of this service can be retrieved using the MemAcc_GetJobResult() API. If the compare operation determined a mismatch, the result code is MEMACCIssuy_MEM_INCONSISTENT

2. MemAcc_BlankCheck() - Checks if the passed address space is blank, i.e. erased and writeable. The result of this service can be retrieved using the MemAcc_GetJobResult API. If the address area defined by targetAddress and length is blank, the result is MEMACC_MEM_OK, otherwise the result is MEMACC_MEM_INCONSISTENT

![](../../../../_images/SAIL%20-%20FEE%20mismatch%20with%20QC%20Mem/image-2024-11-13_17-47-11.png)

NVM should be up and running by end of November

### Solution 1: (Temporary Workaround)

Write a dummy APIs for these two and try to return the value to proceed further

We will try to go with solution 1

### Solution 2:

Bypass NVM and directly access MemAcc - May need lot of clean up again because PATAC SWC is a Autosar module and they connect SWC via NVSWC

### Solution 3: Official QC

Qualcomm ticket status:

We have a sync today afternoon → QC need Bosch to raise a feature request.

Dezhi to discuss with QC asking why we need to raise a new feature request since it is a part of AR standard

Dezhi still push QC to deliver these APIs

## Issue 2: PCAT erasing whole SNOR

When we flash via PCAT it erases whole SNOR, we need to know how to not erase few sectors in SNOR
