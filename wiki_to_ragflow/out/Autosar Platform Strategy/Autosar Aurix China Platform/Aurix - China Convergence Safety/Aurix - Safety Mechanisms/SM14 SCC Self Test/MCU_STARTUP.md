# MCU_STARTUP

> Source: /spaces/CARSFW/pages/2832083790/MCU_STARTUP
> Last modified: 2023-03-13T07:10:16.000+01:00

---

## Overview

Before entering the run mode, the Application SW shall monitor the corruption of data stored in the safety relevant registers.

Safety-relevant registers are to be checked are:

- DMU_HP_PROCONPpx (p,x=0..5)
- DMU_HF_PROCONPF.RPRO
- DMU_HF_PROCONUSR
- DMU_HF_PROCONDF
- DMU_HF_PROCONRAM
- DMU_HF_PROCONDBG (if used)
- DMU_SP_PROCONHSM (if used)
- DMU_SF_PROCONUSR
- DMU_SP_PROCONHSMCBS (if used)
- DMU_SP_PROCONHSMCX0/1 (if used)
- DMU_SP_PROCONHSMCOTP0/1 (if used)
- DMU_SP_PROCONHSMCFG (if used)
- DMU_HP_PROCONOTPpx (p,x=0..5)
- DMU_HP_PROCONWOPpx (p,x=0..5)
- DMU_HF_PROCONTP
- RIFx_LVDSCON1.RTERM (x=0..1)
- STSTAT.HWCFG
