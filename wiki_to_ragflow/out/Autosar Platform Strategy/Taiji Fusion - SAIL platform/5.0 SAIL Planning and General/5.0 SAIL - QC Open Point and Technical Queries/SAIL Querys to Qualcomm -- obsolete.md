# SAIL Querys to Qualcomm -- obsolete

> Source: /spaces/CARSFW/pages/4713728394/SAIL+Querys+to+Qualcomm+--+obsolete
> Last modified: 2024-12-02T04:15:20.000+01:00

---

## 1. Case 07428192 How to 8255 SAIL flash & debug via lauterbach

## 2. Case 07426640 8255 SAIL Code Related Querys

3. Hypervisor Case

QC gave two hypervisor on 18-OCT-2024. The anlaysis as follows

| S.NO | Hypervisor | ELA start address | Behavior |
| --- | --- | --- | --- |
| 1 | EL1_start_0x080D3800 | 0x080D3800 | Changed the start address to 0x080D3800. This hypervisor supports Sideloading. Which means we need to change the register r1 to 0 in hypervisor , then they hypervisor will jump to EL1 SW But the hypervisor jumps in Supervisor mode → not un system mode. We expect the hypervisor will jump in System mode |
|  |  |  |  |
|  |  |  |  |
