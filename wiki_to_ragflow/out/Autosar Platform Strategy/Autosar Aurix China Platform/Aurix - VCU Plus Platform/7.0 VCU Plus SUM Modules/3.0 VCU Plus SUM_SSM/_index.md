# 3.0 VCU Plus SUM_SSM

> Source: /spaces/CARSFW/pages/4600750877/3.0+VCU+Plus+SUM_SSM
> Last modified: 2024-08-14T10:21:52.000+02:00

---

## Overview

This page is to give an overview of SUM SSM

### SSM - Signal Status Monitor

The scope of SUM_SSM is for handling status information related to the Signal Integrity and Source Integrity for received signals, and for handling of generating/checking safety signals transmitted/received with in a protected signal group

Signal Integrity status is determined by interpreting a "flag" or special value which indicates whether signals that were successfully received can be used by local SW-C.

Source Integrity status is determined by detecting transmission errors from senders due to physical layer fault conditions (e.g.: shorts to battery/ground, bus off). These errors may use ECU specific or function specific fault handling strategies

The "status" signals are:

- Source Integrity
- Security Status: For secure messages, security assessment may determine integrity of signal
- Loss of Communication with ECUx
- Uninitialized Value

### SSM functionalities

- Consolidate ECU internal conditions to determine signal status for use by functional software
- Use Security notification from SUM_SSC to notify on security authentication of signal value for secure signals to receivers
- Use initialization and startup conditions to define signal status before serial communication is active/reception of signals
- Integrate relevant status monitor signals to the received signal to calculate status information
- Aggregate signal supervision status from a source to determine Node Loss conditions
- Use safety notification (e.g.: Alive rolling counter (ARC), protection value (PV), checksum (CS), CRC…) to notify safety status associated with signal/s at the receiver
- Generate safety signals (ARC, PV, CS & CRC) associated with signals/signal groups at the transmitter
- Disable the transmission of PDUs for variant handling

![](../../../../../_images/3.0%20VCU%20Plus%20SUM_SSM/image-2024-8-14_15-25-57.png)

![](../../../../../_images/3.0%20VCU%20Plus%20SUM_SSM/image-2024-8-14_15-27-25.png)

### SWC SSM Signal naming convention

![](../../../../../_images/3.0%20VCU%20Plus%20SUM_SSM/image-2024-8-14_16-21-36.png)
