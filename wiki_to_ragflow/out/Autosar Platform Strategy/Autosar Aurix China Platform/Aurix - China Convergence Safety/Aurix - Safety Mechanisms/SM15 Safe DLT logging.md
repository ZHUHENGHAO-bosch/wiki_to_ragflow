# SM15 Safe DLT logging

> Source: /spaces/CARSFW/pages/2719913176/SM15+Safe+DLT+logging
> Last modified: 2023-02-06T03:05:21.000+01:00

---

## Overview

Since the DLT module is an QM module we cannot call the log interface directly from ASIL modules. Hence SafeDltLogging module will help the Safety modules to log the DLT module in a Safe context

Whenever Safe module calls the Safe DLT module to log the message, first the message will be stored in Safe Queue, then in next QM context runnable the DLT message from Safe Queue will be pushed to QM Dlt module

![](../../../../_images/SM15%20Safe%20DLT%20logging/SM15%20Safe%20DLT%20Logging.bmp)
