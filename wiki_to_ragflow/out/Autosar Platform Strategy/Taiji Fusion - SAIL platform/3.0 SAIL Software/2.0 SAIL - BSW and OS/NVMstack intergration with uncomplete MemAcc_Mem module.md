# NVMstack intergration with uncomplete MemAcc/Mem module

> Source: /spaces/CARSFW/pages/5025892197/NVMstack+intergration+with+uncomplete+MemAcc+Mem+module
> Last modified: 2024-11-26T02:30:00.000+01:00

---

## 1. Overview

This page is to introduce current issue when integrated cubas MemStack. Creat the branch for validation:

Download source code:

git clone --recurse-submodules ssh://git@sourcecode01.de.bosch.com:7999/pjw3/temp_j6e_mcu.git

cd temp_j6e_mcu

git lfs pull

git checkout sail_bringup_nvmstack_validation

### 1.1. module used on CUBAS Memstack

- NVM
- FEE (fs2)

### 1.2. module used for MCAL

- MemAcc
- Mem

Currently, the memory driver missing some interface implementation,

1. MemAcc_BlankCheck().

2.MemAcc_Compare();

3. Mem_BlankCheck();

### 1.3. module  cfg  for MemAcc and Fee

![](../../../../_images/NVMstack%20intergration%20with%20uncomplete%20MemAcc_Mem%20module/image-2024-11-20_17-22-41.png)

### MemAcc cfg:

![](../../../../_images/NVMstack%20intergration%20with%20uncomplete%20MemAcc_Mem%20module/image-2024-11-20_17-32-19.png)

FEE cfg:

logical sector start address:0x40000 ---》Corresponding to MemAcc physical address is 0x1B6E000 (why set logical sector start address start with 0x40000,

because cubas cfg remind the  sector start address  can not start with 0,Recommend using a value greater than 0x400(1024bytes)),

so we assign the NVM used flash size with 2MB, but actual used (0x200000-0x4000), Of course, sector start address value can be reduced， but should greater than 0x400)

![](../../../../_images/NVMstack%20intergration%20with%20uncomplete%20MemAcc_Mem%20module/image-2024-11-20_17-25-11.png)

### 1.4. Current issue

1. after intergration MemStack, after FEE init work unproperly with Dummy interface for MemAcc_BlankCheck()/MemAcc_Compare()

FEE_init will do all fee cfg sector init, and do FAT/DAT with active slot, assured that there is at least one FAT-ACTIVE and one data sector, this operation will call MemAcc_BlankCheck()/MemAcc_Compare() do validation

2. MemAcc interface limitation: (Test with Released MemAcc test code)

- MemAcc_Write (MemAcc_AddressAreaIdType addressAreaId, MemAcc_AddressType targetAddress, const MemAcc_DataType *sourceDataPtr, MemAcc_LengthType length)  , targetAddress and length should 16 byte alignment, otherwise mem driver will feedback error status: SPINOR_DEVICE_INVALID_PARAMETER
- MemAcc_Read (MemAcc_AddressAreaIdType addressAreaId, MemAcc_AddressType sourceAddress, MemAcc_DataType *destinationDataPtr, MemAcc_LengthType length)  , sourceAddress and length should 16 byte alignment, otherwise mem driver will feedback error status: SPINOR_DEVICE_INVALID_PARAMETER

Even i change the mcal driver cfg, the problem also, i guess there are restrictions on SNOR driver running on Hyper side.

![](../../../../_images/NVMstack%20intergration%20with%20uncomplete%20MemAcc_Mem%20module/image-2024-11-25_13-41-36.png)
