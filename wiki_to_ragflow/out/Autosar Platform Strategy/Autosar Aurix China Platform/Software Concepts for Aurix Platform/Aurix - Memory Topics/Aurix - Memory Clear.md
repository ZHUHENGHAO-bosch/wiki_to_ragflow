# Aurix - Memory Clear

> Source: /spaces/CARSFW/pages/2768207844/Aurix+-+Memory+Clear
> Last modified: 2023-02-21T04:30:09.000+01:00

---

Below tables summarizes the Memory clear use cases

|   |   |   |   |
| --- | --- | --- | --- |
| Reset Type | RAM | Cleared By | Comments |
| Cold PORST | DSPR, PSPR, DLMU | Firmware | Configured in UCB |
| Warm PORST | DSPR, PSPR | SSW (Configurable) | MBIST (Startup phase 4), in current configuration DPSR0 and DLMU0 is not cleared |
| DLMU_NoInit (DLMU0) | Not cleared | MBIST will be configured as no clear |
| DLMU_Others | SSW (Configurable) | MBIST (Startup phase 4) |
| System Reset | DSPR, PSPR, DLMU | No Clear | Global Variables will be Initialized by C Init |
| Application Reset | DSPR, PSPR, DLMU | No Clear | Global Variables will be Initialized by C Init |
| Diagnostic reset (11 10) | DSPR, PSPR, DLMU | SSW | MTU (StartupPhase1) |
| Wakeup from SCR | DSPR, PSPR | SSW (Configurable) | MTU Open point: We see wakup from SCR as Cold PORST and firmware is clearing the RAM. Newton is about to Send mail to IFX |
| DLMU_NoInit | Not cleared |
| DLMU_Others | SSW (Configurable) |
| Safety Reset (??) | DSPR, PSPR, DLMU | TBD | TBD |
