# SAIL - Queries and anlaysis

> Source: /spaces/CARSFW/pages/4948533137/SAIL+-+Queries+and+anlaysis
> Last modified: 2024-12-10T07:38:06.000+01:00

---

## Overview

This page is to analyze the queries from PATAC

#### Does Sail refresh require recovery mode?

SAIL binary is located in SNOR and SAIL software supports OTA.

When to perform OTA either during normal mode or recovery mode depends on System Flash concept. But flashing in normal or recovery mode is supported by SAIL domain

How to deal with Sail UDS independent refresh (calibration + software), and does it depend on A-core?

Do we need UDS flashing of SAIL via CAN? Because current SAIL support OTA via Main domain no FBL planned in SAIL

The current Update Architecture in SAIL is shown below

Can Sail USB independent refresh be supported?

Need to check

![](../../../../_images/SAIL%20-%20Queries%20and%20anlaysis/SAIL_OTA_Update.jpg)

#### Sail and A check whether there are any requirements for power mode synchronization?

#### How to connect the AP to LCM/susd?

There should be synchronization between SAIL and MD during startup and shutdown

The synchronization shall be via mailbox between SAIL and MD

![](../../../../_images/SAIL%20-%20Queries%20and%20anlaysis/SAIL_Mode_Synchronization.jpg)

#### What is the working state of Sail when the A-core enters/exits STR?

First we need to decide whether we will enter STR or deep sleep state

### STR state:

> **INFO: SAIL state in STR**
> SAIL on chip memory will be in retention state SAIO IOs are in keeper state SAIL PMIC turns OFF most of the regulator program certain regulators at a lower voltage level based on pre-defined configurat ion

To achieve a low power state while being able to wake up quickly, Suspend to RAM (STR) is supported from hardware perspective in the QAM8775P

SoC in retention mode from both MD and SAIL domains

- On-chip memories are in retention state
- GPIOs and SAIL_IOs are in keeper state
- Most of the subsystems inside SoC are powered OFF except for Always-on Subsystem (AOSS
- XO shutdown

STR entry:

- SoC initiates STR entry sequence in PMM8650AUs through SPMI interface and SAIL PMIC by asserting SAIL_IO_66 (SAILSS_SLP_EN)
- PMM8650AU_A turns OFF CXO outputs and SAIL PMIC disables SAIL_CXO oscillator output
- PMM8650AUs and SAIL PMIC turn OFF most of the regulators and program certain regulators at a lower voltage level based on pre-defined configuration
- PMM8650AU_A asserts AOSS_SLEEP_ENTRY_EXIT (active high) and SAIL PMIC de-asserts SAIL_IO_65 (SAILSS_PWR_READY )

STR exit:

- If wake up interrupt is sent to SoC through GPIO, SAIL_IO, CAN or ethernet
- If wake up interrupt is sent to SAIL PMIC by asserting PMS_GPIO_3 (WAKEUP, active low)

### Deep sleep state:

> **INFO: Deep sleep state**
> SoC Main Domain in deep state while SAIL domain in OFF state All power rails will be off except for LPDDR5 related rails remain ON to keep the memory in self refresh state

To achieve ultra lower power consumption requirement while still able to meet boot KPI requirements, a new concept called Deep Sleep is introduced in QAM8775P

- It allows the SoC Main Domain in deep state while SAIL domain in OFF state
- All power rails will be off except for LPDDR5 related rails remain ON to keep the memory in self refresh state

Deep Sleep Entry:

- SoC initiates deep sleep entry sequence
- PMM8650AU_A asserts AOSS_SLEEP_ENTRY_EXIT (active high)
- PMM8650AU_A asserts SOC_RESIN_N to put SoC MD in reset stage
- MD regulators except Deep Sleep regulators disabled and CXO buffer turned off
- PMM8650AU_A asserts POFF_COMPLETE_N to VIP
- SoC SAIL software will force ENABLE_DRV to LOW and initiate SAIL PMIC shutdown
- SAIL PMIC asserts SAIL_RESIN_N to put SoC SAIL in reset stage
- VIP de-asserts SAIL PMIC PMS_ENABLE and all SAIL regulators are turned off

Deep Sleep Exit:

- VIP triggers PMS_ENABLE to power on SAIL PMIC and PM_PWR_EN_N to power on PMM8650AUs
- SAIL PMIC enables SAIL power rails, releases SAIL_RESIN_N and asserts PON_DONE to PMM8650AU to indicate SAIL PON sequence completed
- PMIC de-asserts AOSS_SLEEP_ENTRY_EXIT
- PMIC enables PON regulators (XO buffer is turned on)
- PMIC de-asserts POFF_COMPLETE_N to VIP
- PMIC de-asserts SOC_RESIN_N/SAIL_RESIN_N and waits for PS_HOLD to go high

## SAIL STR

(refer to 80-PG469-7 Rev. R QNX Power Management Software Architecture Reference Manual )

![](../../../../_images/SAIL%20-%20Queries%20and%20anlaysis/image-2024-12-10_14-30-45.png)

![](../../../../_images/SAIL%20-%20Queries%20and%20anlaysis/image-2024-12-10_14-31-5.png)

![](../../../../_images/SAIL%20-%20Queries%20and%20anlaysis/image-2024-12-10_14-37-39.png)
