# Aurix Taiji platform lesson learnt

> Source: /spaces/CARSFW/pages/6461296714/Aurix+Taiji+platform+lesson+learnt
> Last modified: 2025-11-10T03:45:27.000+01:00

---

## Overview

Thia page is to list the issue in aurix based projects and make sure this is not followed in next project.

Focus on configuration repo, since it varies from project to project.

### Lesson Leant

| S/No | Issue overview | Issue root case | Who to check | Found in | How to fix or how to make sure issue not happens |
| --- | --- | --- | --- | --- | --- |
| 1 | CSA Area out of DSPR region We found the CSA region size exceeds the DSPR region and when we flash it ends up in Class 4 TIN 2 (Data Synchronous) trap | CSA is kept at the end of DSPR region in LD file Since we use. += 16384, the linker will not throw an error even the memory exceeds the allocated DSPR in common LD file ![](../../_images/Aurix%20Taiji%20platform%20lesson%20learnt/image-2025-11-10_9-25-2.png) | FOs and who do LD changes | VCU plus, GHAC | Don't keep CSA or the startup stack at the end of DSPR region Keep some section below CSA like .SYS_FAST_RAM_DATA_CORE2          :>. So that linker can identify the limit exceeded and it can throw error during build |
| 2 | 1101 multiple retries SCC enters into bootloader | LCM has not clear the reset counter for 11 01 reset request | LCM and Diag developers | VCU plus | LCM to clear the reset counter for 11 01 reset request |
| 3 | The Lbist  check failed into bootloader | when startup phase voltage instability，random occurrence libst check  termination  due to the occurrence of a Power On Reset，and the PBPORST bit set. ![](../../_images/Aurix%20Taiji%20platform%20lesson%20learnt/image-2025-11-10_10-36-2.png) | Fusa developer | VCU plus, CCU | add lbist retrigger once at after startup, when the cold startup LBIST termination due to PORST |
