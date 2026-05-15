# CRC generation and verification using GHS Libraries

> Source: /spaces/CARSFW/pages/2910196806/CRC+generation+and+verification+using+GHS+Libraries
> Last modified: 2023-04-02T09:38:32.000+02:00

---

## Introduction

This page describes the CRC calculation and comparison aspects of the PFLASH CRC check module part of the SM02 - ROM monitoring,

PFlash monitoring has two step validation,

1. Scanning - ECC trigger
2. CRC validation as per IFX Safety recommendation requirements,

![](../../../../../_images/CRC%20generation%20and%20verification%20using%20GHS%20Libraries/SM02%20%20ROM%20Monitoring.bmp)

## CRC computation during runtime

The runtime CRC computation functionality is provided by CART PF SM - SM09 - PFlash monitoring, it makes use of the IFX CRC module with DMA.

## CRC computation during build

CRC shall be computed for each ASIL section of Flash memory and shall be binary shall be generated with CRC embedded part of the binary.

The following solutions from different projects considered to decide on the approach for China Convergence,

### Volvo Cluster project reference

CRC generation done for complete binary image using Tool (Volvo provided)

BL verifies complete binaries.

Storing of CRC and BL integration in project scope - BL/BM

Two validation steps - Flashing cycle(BM-CCC) + Run cycle(PFlash Checker)

### BR214 reference

ASIL qualified tool used for binary generation and flashing - Monaco

PFLASH CRC not done (ASIL A)

### FCA/Hydra reference

GHS libraries used compiler flag options provide possiblity to generate CRC for Flash sections and embed in the binary.

### Zeekr

Decision to go ahead with GHS solution as compiler support is available and satisfies IFX safety requirements, without requiring additional tool development. ASIL qualification for flashing tool is also not required in this solution.

## GHS solution

### Compile time

CRC is computed for each section by adding the compiler flag, '-checksum'. CRC is embedded at the end of each section with additional 4 bytes extended for CRC.

|   |   |   |   |
| --- | --- | --- | --- |
| Build variant | Section | Address(Example) | Size |
| Normal Build |  |  |  |
|  | .ASIL_SECTION_TEXT_CORE0 | 0x80275068 | 0x0000cd10 |
|  |  | 0x80281D78 |  |
| Check sum enabled Build |  |  |  |
|  | ASIL_SECTION_TEXT_CORE0 | 0x80275068 | 0x0000cd14 |
|  | __ghschecksum_.ASIL_SECTION_TEXT_CORE0 | 0x80281D78+000004 |  |

### Run time

The same CRC shall be extracted at run time using the data structure, ' __secinfo ', this is a linked list containing details of each section and its properties(reference below),

```
typedef struct secinfo_t {
    struct secinfo_t*   next; /* NULL for no next section */
    const char*		name; /* nul-terminated section name */
    void*		addr; /* Address of section in memory */
    uint32_t		size; /* length of section (bytes) */
    uint32_t		flags; /* flags, see below */
    struct secinfo_t*   romcopyof; /* this section is a ROM copy of 'romcopyof' */

 /* Future fields go here */

} *secinfo_ptr;
```

```
PFCC_LogicalBlockRecords_s pfcc_logicalBlockTable[PFCC_MAX_LOGICAL_BLOCK_COUNT] = {
  /*Pflash Record 0*/
    {
     .blockIndex           = 0x01,
     .blockStartAddress_u  = PFCC_PFLASH_BLOCK0_START_ADDR,
     .blockEndAddress_u    = PFCC_PFLASH_BLOCK0_END_ADDR,
     .expectedCRCAddress_u = PFCC_BLOCK0_EXPECTED_CRC_ADDR,
     .isCrcCheckEnabled_b  = FALSE,
     },
 /*Add Pflash Records here*/
};  

void InitSectionCRCs()
{
    secinfo_ptr flashSections_ptr;
    for (flashSections_ptr = &__secinfo; flashSections_ptr != NULL; flashSections_ptr=flashSections_ptr->next;) 
    {
        pfcc_logicalBlockTable[i].blockStartAddress_u = (uintptr_t)flashSections_ptr->addr;
        pfcc_logicalBlockTable[i].blockEndAddress_u = (uintptr_t)flashSections_ptr->addr+flashSections_ptr->size-4;
        pfcc_logicalBlockTable[i].expectedCRCAddress_u = (uintptr_t)flashSections_ptr->addr + flashSections_ptr->size -3;    
    }
}
```
