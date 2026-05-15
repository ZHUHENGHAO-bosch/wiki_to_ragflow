# China Convergence Logging - Architectural Guideline

> Source: /spaces/CARSFW/pages/2425246980/China+Convergence+Logging+-+Architectural+Guideline
> Last modified: 2023-03-13T06:27:55.000+01:00

---

## Overview

All modules in SCC shall log

- Useful information via DLT
- Error/Fatal information via FEL/EM

Since the module used for Dlt and EM may change from project to project, it is recommended to use Wrapper APIs for both Dlt and Error logging by the User modules

And this Wrapper shall be in Configuration repo.

Below diagram shows the example,

![](../../../../_images/China%20Convergence%20Logging%20-%20Architectural%20Guideline/LcmLogging.bmp)

.
