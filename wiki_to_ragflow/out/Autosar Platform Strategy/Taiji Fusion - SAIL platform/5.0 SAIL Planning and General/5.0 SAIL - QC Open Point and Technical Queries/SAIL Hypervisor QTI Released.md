# SAIL Hypervisor QTI Released

> Source: /spaces/CARSFW/pages/5042800855/SAIL+Hypervisor+QTI+Released
> Last modified: 2024-12-02T04:16:39.000+01:00

---

Qualcomm's hypervisor is a black box. We keep raising requirements, and they continuously update it.

Make a record of this here.

Sail flash package: flash_sail_via_PCAT.zip

| No | sailhyp.elf | Release Date | Comment |
| --- | --- | --- | --- |
| 0 | sailhyp.elf | ES06 | original ES06 SafeRTOS version |
| 1 | sailhyp.elf | 2024.10.4 | single-core |
| 2 | sailhyp.elf | 2024.10.23 | multi-core, side-load hypervisor can work properly in VCU Pro 8255（Need T32 debug and modify R0） |
| 3 | multi_os_sail.7z sailhyp dts: lemansau-sailhyp-autosar.dts.multi-core.workok.bak | 2024.11.21 | multi-core hypervisor.elf+ symbol .elf can work properly with bringup branch , VCU Pro 8255(little size elf，<200Kb） can work properly in Local 8775 Demo Hardware(large size elf, > 600Kb) can't work properly in Nessy 8775 board (large size elf, > 600Kb) can't work with bringup_dev branch，VCU Pro 8255 (large size elf, > 600Kb) |
| 4 | sailhyp.elf | 2024.11.22 | multi-core hypervisor, workaround(hypervisor delay 3s before load EL1 elf) can work properly , VCU Pro 8255, (large size elf, > 600Kb) |
|  |  |  |  |
|  |  |  |  |
