# SAIL - CDD

> Source: /spaces/CARSFW/pages/4884496546/SAIL+-+CDD
> Last modified: 2024-10-17T07:42:54.000+02:00

---

## CDDs delivered by QC

| Module | Description | ASIL/QM | Priority |
| --- | --- | --- | --- |
| CDD_Acmu | Automotive clock monitoring unit (ACMU) Driver for Clock monitoring Unit (On-chip clock monitors) ![](../../../../../_images/SAIL%20-%20CDD/image-2024-8-27_18-53-48.png) | ASIL | FuSa - 2 |
| CDD_BootLogger | Gives interface to store Boot message In cyclic task, send the boot message to VIP/SCC | ASIL | FuSa - 2 |
| CDD_DebugLog | CDD module to send log message via UART | QM | AR - 1 May be we will replace by DLT in future |
| CDD_Dispatcher | Receives UART message and call respective callback based on Command ID | QM | AR - 3 |
| CDD_Fusa | Centralized module to handle the Main domain Fatal Sail Fatal Warning and Error It is similar to Ausm and SMU in Aurix | ASIL | FuSa - 1 |
| CDD_I2c | I2C Device driver | QM | AR - 1 PMIC is via I2C |
| CDD_Icb | SAIL NOC error handling implementation | ASIL | FuSa - 2 |
| CDD_Ipcc | Driver for IPCC (Inter-processor communication controller) | ASIL | AR - 1 |
| CDD_Isd | Driver for Island State Detector. This driver supports isolating SAIL subsystem from the entire SoC whenever main domain fatal errors occurs | ASIL | Fusa - 2 |
| CDD_Mailbox | Safety SW library for Mailbox communication Safe mailbox communication between SAIL and main domain safety monitor is made safe using data integrity checks, BCS mechanism Mailbox used Ipcc as low level driver | ASIL | AR - 1 |
| CDD_Monitor | Module which start, stop and update different monitor modules | ASIL | FuSa - 1 |
| CDD_Pmic | Driver for external ASIL-D PMIC for SAIL | ASIL | AR - 1 |
| CDD_Psail | Driver for monitoring the Main Domain PMIC | ASIL | FuSa - 2 |
| CDD_Ssm | SAIL safety monitor ![](../../../../../_images/SAIL%20-%20CDD/image-2024-8-27_17-46-39.png) | ASIL | FuSa - 1 |
| CDD_Uart | Driver for UART interface | QM | AR - 1 |
| CDD_Vsens | Voltage monitoring driver | ASIL | FuSa - 2 |
| CDD_CRC | CRC module | ASIL | FuSa - 2 |
| CDD_Qfprom | This component takes care of SW fuses related SSRs (Qualcomm fuse-programmable read-only memory) | ASIL | FuSa - 3 |
| CDD_Tsens | Temperature sensor driver | ASIL | FuSa - 2 |
| CDD_Xbl | eXtensible bootloader |  | AR - 2 |
