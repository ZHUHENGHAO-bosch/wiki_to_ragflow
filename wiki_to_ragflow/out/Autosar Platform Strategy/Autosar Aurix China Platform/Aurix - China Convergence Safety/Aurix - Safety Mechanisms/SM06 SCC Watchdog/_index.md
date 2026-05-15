# SM06 SCC Watchdog

> Source: /spaces/CARSFW/pages/2658504005/SM06+SCC+Watchdog
> Last modified: 2023-01-28T09:13:45.000+01:00

---

### Internal Hardware watchdog:

Aurix TC3xx supports two types of Watch dog

- Safety Watchdog (System level watchdog)
- CPU watchdog (Each CPU has its own watchdog)

### External Watchdog handling

Since we have ASIL-B requirement, it is necessary to monitor Aurix using external watchdog

- MAX20479A

We will not use safety Watchdog, Since External Watch dog covers the system level watchdog monitoring

![](../../../../../_images/SM06%20SCC%20Watchdog/SM7%20SCC%20Watchdog.bmp)

### Startup operation:

CPU0 Watchdog are active immediately after Reset/PowerOn.
