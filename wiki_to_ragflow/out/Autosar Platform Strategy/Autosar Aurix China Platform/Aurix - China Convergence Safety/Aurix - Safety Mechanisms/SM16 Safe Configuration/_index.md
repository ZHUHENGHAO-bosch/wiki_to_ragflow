# SM16 Safe Configuration

> Source: /spaces/CARSFW/pages/2615955936/SM16+Safe+Configuration
> Last modified: 2023-02-03T12:18:59.000+01:00

---

For ZEEKR, we are going to reuse this SM from GEELY. Since CART has no plan for this SM as of now

Safe Configuration provides

- From KDS memory - OTP section
- Car configuration (Application will read Car Config from other ECU via FR and store it in NVM) - needed by SW Tell tales and Safe output signals. Below are the examples,
- Local Configuration data (Calibration data via SW update process - This data also will be stored in DFLASH considering SWAP A/B feature) - needed by SW Tell tales and Safe output signals

![](../../../../../_images/SM16%20Safe%20Configuration/SM16%20Safe%20Configuration.bmp)
