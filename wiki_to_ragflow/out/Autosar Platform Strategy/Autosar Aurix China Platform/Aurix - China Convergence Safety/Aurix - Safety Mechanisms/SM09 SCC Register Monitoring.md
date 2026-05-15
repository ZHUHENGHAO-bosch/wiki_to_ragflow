# SM09 SCC Register Monitoring

> Source: /spaces/CARSFW/pages/2699331193/SM09+SCC+Register+Monitoring
> Last modified: 2023-01-29T06:56:22.000+01:00

---

The safety mechanism - SM09 Register Supervision performs the monitoring activity in two ways.

1. Software Monitoring.
2. Hardware Monitoring.

Software Monitoring:

In Software Monitoring, the SW shall Monitor all safety related peripheral' registers at every periodic runnable. If fault counter exceeds the limit, SSH shall be triggered to perform the reset after error logging.

Hardware Monitoring:

In Hardware Monitoring, the AURIX have the internal HW monitoring for all the peripherals which reports SMU different alarms such as SPB Bus error event alarm, Safety Flip-Flop uncorrectable and correctable alarms

Safety Flip flop is taken care by SM14 SCC Self Test - XC-CT China - Docupedia (bosch.com)

![](../../../../_images/SM09%20SCC%20Register%20Monitoring/SM09%20RegisterProtection.bmp)
