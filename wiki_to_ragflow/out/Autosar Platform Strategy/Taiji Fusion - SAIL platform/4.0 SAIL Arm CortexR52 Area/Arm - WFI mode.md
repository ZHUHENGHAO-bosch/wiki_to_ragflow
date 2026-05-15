# Arm - WFI mode

> Source: /spaces/CARSFW/pages/4862302094/Arm+-+WFI+mode
> Last modified: 2024-10-14T08:55:31.000+02:00

---

## Overview

This page is to explain the Arm WFI mode

### WFI (Wait for Interrupt):

Arm supports Wait For Interrupt through an instruction, WFI, that is provided in the ARM and Thumb instruction sets

Wait For Interrupt is a hint instruction that permits the processor to enter a low-power state until one of a number of asynchronous events occu

When a processor issues a WFI instruction it can suspend execution and enter a low-power state

The Virtualization Extensions provide a bit that traps to Hyp mode any attempt to enter a low-power state from a Non-secure PL1 or PL0 mode.

The processor can remain in the WFI low-power state until it is reset, or it detects one of the following WFI wake-up events :

- a physical IRQ interrupt, regardless of the value of the CPSR.I bit
- a physical FIQ interrupt, regardless of the value of the CPSR.F bit
- a physical asynchronous abort, regardless of the value of the CPSR.A bit
- in Non-secure state in any mode other than Hyp mode:
- an asynchronous debug event, when invasive debug is enabled and the debug event is permitted.

### Note:

- Because debug events are WFI wake-up events, ARM strongly recommends that Wait For Interrupt is used as part of an idle loop rather than waiting for a single specific interrupt event to occur and then moving forward. This ensures the intervention of debug while waiting does not significantly change the function of the program being debugged.

### Trapping use of the WFI and WFE instructions

An operating system can use the WFImechanism to signal to the processor that it can suspend operation until it receives an interrupt. In a virtualized system, the hypervisor might use this signal as an indication that it can switch to another Guest OS. Therefore, the HCR includes a bit that traps attempted execution of a WFI instruction to the Hyp Trap exception

Software can use the WFE mechanism to signal to the processor that it can suspend execution during polling of a variable, such as a spinlock. In a virtualized system, WFE might indicate an opportunity for the hypervisor to reschedule. However, WFE generally requires a shorter wait than WFI, and therefore there might be situations where rescheduling on WFE is not appropriate.
