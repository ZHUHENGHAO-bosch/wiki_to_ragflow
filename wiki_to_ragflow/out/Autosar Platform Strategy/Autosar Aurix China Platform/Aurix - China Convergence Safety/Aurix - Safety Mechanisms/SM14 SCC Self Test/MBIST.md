# MBIST

> Source: /spaces/CARSFW/pages/2816372241/MBIST
> Last modified: 2023-03-13T07:12:54.000+01:00

---

### Overview

MBIST is a safety mechanism which detects structural problems and checks SRAM to detect permanent random hardware faults in memory cells and memory controller.If MBIST is not run permanent random fault could remain latent in memory cells and memory controller.

|   |   |
| --- | --- |
| M[HW]:VMT:MBIST | MBIST is a safety mechanism which detects structural problems and checks SRAM to detect permanent random hardware faults in memory cells and memory controller.If MBIST is not run permanent random fault could remain latent in memory cells and memory controller. |
| SMC[SW]:VMT:MBIST | Application SW shall configure the MTU for performing MBIST by setting MCx_CONFIG0, MCx_CONFIG1 and MCx_MCONTROL registers, where x identifiesthe SRAM instance |
| ESM[SW]:VMT:MBIST | MBIST shall be executed at least once per driving cycle on all SRAM that are used by Application SW. The MBIST result shall be read by Application SW in MCx_ECCD and MCx_ETRR registers. |
