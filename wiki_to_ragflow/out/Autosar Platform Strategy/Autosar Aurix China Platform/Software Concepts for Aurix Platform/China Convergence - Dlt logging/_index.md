# China Convergence - Dlt logging

> Source: /spaces/CARSFW/pages/2403658546/China+Convergence+-+Dlt+logging
> Last modified: 2023-02-23T07:38:40.000+01:00

---

## Overview

Diagnostic Log and Trace (DLT) is an important feature which enables logging of important information into DLT via UART and INC

![](../../../../_images/China%20Convergence%20-%20Dlt%20logging/CN%20Conv%20PF%20-%20DLT%20logging%20overview.bmp)

## Log types

1. FATAL - Fatal system error
2. ERROR - Errors occurring in a module with impact to correct functionality
3. WARN - Log messages where a correct behavior can not be ensured
4. INFO - Log messages providing information for better understanding of the internal behavior of a software
5. DEBUG - Log messages, which are usable only for debugging of a software
6. VERBOSE - Log messages with the highest communicative level, here all possible states, information and everything else can be logged

Decision matrix by Cerberus team for DLT logging
