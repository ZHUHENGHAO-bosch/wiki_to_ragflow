# SMU FSP Protocol

> Source: /spaces/CARSFW/pages/2825339403/SMU+FSP+Protocol
> Last modified: 2023-03-10T06:26:14.000+01:00

---

The fault signaling protocol is configured via the FSP command register.

The FSP has three states

- The power-on reset state. After warm power-on reset the SMU is disconnected from the ports. After warm power-on reset the SMU FSP output shall be the Fault State
- The Fault-free State
- The Fault State. The timing of the fault state is controlled by the FSP register. The minimum active fault state time is called TFSP_FS

The Fault-free and fault state behavior can be configured with the following protocols:

- Bi-stable protocol (default)
- Dynamic dual-rail protocol
- Time-switching protocol

The FSP can be controlled by

- Software using the SMU_ActivateFSP() and SMU_ReleaseFSP() commands using the CMD register
- Hardware based on the AGiFSP (i=0-11) configuration registers.

In China Convergence Platform and project, we will use FSP as Bi Stable protocol to Turn OFF Display backlight as Safety Shutdown Path .

![](../../../../../_images/SMU%20FSP%20Protocol/image2023-3-10_13-23-13.png)

### FSP and SMU state machine Sync

![](../../../../../_images/SMU%20FSP%20Protocol/image2023-3-10_13-25-55.png)
