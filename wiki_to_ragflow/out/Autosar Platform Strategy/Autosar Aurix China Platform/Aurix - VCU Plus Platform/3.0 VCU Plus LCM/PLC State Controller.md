# PLC State Controller

> Source: /spaces/CARSFW/pages/4605622731/PLC+State+Controller
> Last modified: 2025-09-02T04:32:43.000+02:00

---

## Overview

This page is to give an Overview of PLC State Controller

### Roles of PLC State Controller

- Monitoring whether RTOS has successfully booted during startup and take appropriate recovery actions
- Ensuring that RTOS is functional throughout the run-time of the VCU by monitoring state of health messages from it
- Interfacing with the System State Controller to provide shutdown permission to the VIP power state controller i.e. SUM_SUSD to indicate that SoC is ready for shutdown
- Interfacing with the EcuM/BswM components to receive requests for initiating SoC shutdown
- Co-coordinating shutdown/ suspend procedure of the SoC
- Interfacing with SysMgr to request cut-off/reset of power lines to the SoC after low level shutdown of RTOS in SoC is complete.
- Interfacing with SysMgr to accept request for initiating controlled SoC shutdown when temperature or voltage values exceed pre-defined thresholds

### States of PLC and State transition

![](../../../../_images/PLC%20State%20Controller/PlcStateController_statemachine.jpg)

Check SFS-107 which will give more information on PLC state controller state machine input, Output and events

| State | Description |
| --- | --- |
| VCU_Startup | Init state It remains in this state until RTOS is successfully up indicated by reception of ReportPowerLevel(2) message when SoC is in Normal mode after which it transitions to VCU_ON state RTOS is successfully up indicated by reception of Reflash message when SoC is in Normal mode after which it transitions to Reflash state Expiration of PLC_SoC_STARTUP_TIMER [interpreted as RTOS boot failure] VCU Reset |
| VCU_On | This is the state that is assumed by the SoC PLC State Controller when RTOS is successfully up and in a stable state It monitors the periodic state-of-health messages from the SoC to detect that it is operational, and to reset the VCU in case more than pre-configured number of state of health pings are detected to be lost contiguously. SoC PLC State Controller remains in this state till it receives shutdown events. |
| VCU_Shutdown | This state is assumed by the SoC PLC State Controller while performing shutdown or suspend operations. SoC PLC State Controller, when in this state, determines if the shutdown request should be interpreted as a suspend operation based on SUSPEND_TO_RAM_ENABLE calibration ShutdownP1 - This sub-state is assumed by the VCU_Shutdown state to wait for reception of ReportPowerLevel(1) message from SoC indicating that shutdown/suspend preparation at RTOS is complete On reception of ReportPowerLevel(1) message the VCU_Shutdown transitions to ShutdownP2 sub-state ShutdownP2 - On entry to this sub-state the SoC is requested to begin low level shutdown/suspend. This sub-state is retained till completion of low-level shutdown/suspend which is indicated via a GPIO signal from the SoC. On receiving this signal, the SoC PLC State Controller transitions to the VCU_Sleep state. If during the shutdown/suspend procedure a pullback is triggered, exit from VCU_Shutdown state triggers a restart of SoC and transition to VCU_StartUp state |
| VCU_Reflash | This state indicates that VCU is being re-flashed, with RTOS running in recovery mode The state is entered when Reflash message is received by the SoC PLC State Controller in the VCU_Startup state The Reflash message is sent by the SoC when it is in RTOS Recovery.. It remains in this state until shutdown or reset is triggered. Also, ShutdownRequest received from in this state from the System State Controller are never translated to Suspend irrespective of the value of calibration SUSPEND_TO_RAM enable as RTOS in recovery mode needn’t be suspended |
| VCU_Sleep | This state is acquired by the SoC PLC State Controller after receiving PL-0 notification as part of non- thermal/voltage range related shutdown |
| VCU_NoSoC | This state is acquired by the SoC PLC State Controller after receiving PL-0 notification as part of thermal/voltage range related shutdown. In this state the SoC is powered-off and VIP is active. It remains in this state until the VCU voltage/thermal measurements are within acceptable range or there is no remaining wakeup reason |
| VCU_EDL | This state is acquired by the SoC PLC State Controller after it detects entry of SoC in EDL mode, irrespective of which state it is in. |
| VCU_FACTORY_RESET | This state is acquired by the SoC PLC State Controller after it receives notification from SoC that factory reset has been initiated. Any Shutdown/Suspend/reset request received in this state is buffered and processed only after exiting the state. Also, no SOH monitoring takes place in this state The state machine can stay in this state for maximum of PLC_SoC_FACTORY_RESET_TIMEOUT duration |

### Reference

SFS_123_VCU_VIP_PowerLif…
