# SMU Recovery Timer

> Source: /spaces/CARSFW/pages/2825338462/SMU+Recovery+Timer
> Last modified: 2023-03-10T03:15:33.000+01:00

---

### Overview - Recovery timer

A recovery timer (RT) is available to enable the monitoring of the duration or internal error handlers activated by an alarm, NMI or Interrupt action.

In the current SMU_core implementation two independent instances (RT0 and RT1) are available.

The recovery timer duration (identical for all instances) is configured in the register RTC. It is possible to enable or disable each instance, however both instances are enabled by default as it is required for the operation of the CPU watchdogs

Once a recovery timer event has occurred, the recovery timer starts and counts until software stops it with the SMU_RTStop(). If the timer expires, an internal SMU alarm (Recovery Timer Timeout) is issued

### Watchdog alarms

The watchdogs (WDT) timeout alarms require a special processing in order to ensure a correct microcontroller behavior if the watchdogs are not serviced by software or firmware. It shall be ensured that the microcontroller is reset after a pre-warning phase, where software can still perform some critical actions

Every timeout alarm shall activate an NMI

Recovery Timer 0 shall be configured to service WDT timeout alarms for Safety WDT, CPU0 WDT, CPU1 WDT and CPU2 WDT

Recovery Timer 1 shall be configured to service WDT timeout alarms for CPU3 WDT, CPU4 WDT and CPU5 WDT

Recovery Timer 0 and Recovery Timer 1 timeout alarms shall be configured to issue a reset request and activate the Fault Signaling Protocol

![](../../../../../_images/SMU%20Recovery%20Timer/image2023-3-10_10-12-45.png)
