# 06_Jump to bootloader mistakenly due to Abnormal Ubat Voltage

> Source: /spaces/CARSFW/pages/2451723175/06_Jump+to+bootloader+mistakenly+due+to+Abnormal+Ubat+Voltage
> Last modified: 2023-08-09T08:16:19.000+02:00

---

## Information

1. Fusa will monitor Ubat Voltage (e.g. normal value is 6~30v). Fusa will reset SCC when Ubat is abnormal.
2. Fusa have a requirement, SCC should jump to Boot after APP resets 25 times continuously.

GEELY Project have K30 Voltage Test in base tech: Set K30 voltage ramp-up from 5v - 30v. During the 5v, SCC will reset continuously due to fusa safety voltage monitor and jump to boot eventually. This cause test case to fail.

From another perspective,  if K30 is really under-voltage in the car, SCC jumped to the boot.  Driver have to disconnect the battery or upgrade the DHU to recover. This is unreasonable.

## Analysis

We don't count when reset caused by abnormal ubat voltage .

## Solution

When abnormal voltage is detected , c all  Startup_clrResetCounter(STARTUP_APPL_RESETCOUNTER) before  reset.

### Fix Status

| Affected project | FixStatus | RTC/Gerrit Linkage |
| --- | --- | --- |
| GEELY | COMPLETED | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/477525 |
| GAC | COMPLETED | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/531605 |
| BYD | COMPLETED | 已横展，已复测 |
