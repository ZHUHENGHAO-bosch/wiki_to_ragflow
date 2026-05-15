# SAIL GPT

> Source: /spaces/CARSFW/pages/5155534901/SAIL+GPT
> Last modified: 2024-12-31T04:24:06.000+01:00

---

Raised Case to QTI: Number:  07600959

What partitions need in SAIL Nor Flash?

refer to J6E

https://inside-docupedia.bosch.com/confluence2/display/XCJ6EHW/MCU+domain+Memory+Layout+for+J6E

| Partition name | Secondary partition | Size | Img Name | OTA support? | Usage | 8775 SAIL Need? | Comment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fpt |  | 256K | fpt.img | yes | 包含多个分区：hsm、xspi、key以及ivt_host等 | No | 存储各分区信息,8775 SAIL 有自己的对应的分区 |
|  | IVT_HSM | 128B |  |  | 放置ivt for hsm | No |  |
|  | IVT_HSM_bak | 128B |  |  | 放置ivt for hsm的备份 | No |  |
|  | XSPICP_a | 512B |  |  | 放置xspi参数 | No |  |
|  | XSPICP_b | 512B |  |  |  | No |  |
|  | flash_key | 256B |  |  | 放置flash烧写验签公钥 | No |  |
|  | flash_key_bak | 256B |  |  | 放置flash烧写验签公钥的后备分区 | No |  |
|  | IVT_HOST_a | 512B |  |  | Host的ivt分区镜像信息 | No |  |
|  | IVT_HOST_b | 512B |  |  |  | No |  |
|  | IVT_HOST_r | 512B |  |  | Host的ivt recovery分区镜像信息 | No |  |
| recovery |  | 5.75M |  |  |  | No | A/B面都失效的情况下，会使用这里的最小系统 |
| misc |  | 256K | misc.img | yes | 存储slot A/B状态机 | No | 上电时，通过这里的flag，来确定从A还是B启动,8775 高通自己考虑 |
| HB_APDP |  | 256K |  |  | 调试使用 | No |  |
| keystorage |  | 512K |  |  | DDR Quick boot | No | 存储用户密钥 |
| HSM_FW |  | 512K | HSM_FW.img | yes | 硬件安全模块固件 | No | Checked with ESS xuzhiyuan, no need consider HSM partition  now |
| HSM_FW_bak |  | 512K |  |  |  | No |  |
| HSM_RCA_a |  | 256K | HSM_RCA.img | yes | 放置根证书 | No |  |
| HSM_RCA_b |  | 256K |  |  |  | No |  |
| keyimage |  | 256K | keyimage.img | yes | 存储key image | No |  |
| keyimage_bak |  | 256K |  |  |  | No |  |
| SBL |  | 512K | SBL.img | yes | Secondary  bootloader, boot program of RCore | No | SAIL have no SBL |
| SBL_bak |  | 512K |  |  |  | No | SAIL have no SBL |
| scp_a |  | 512K | scp.img | yes | 对acore时钟/电源等初始化 | No | A核供电程序(DSP核拉A核，R核不使用该分区） |
| scp_b |  | 512K |  |  |  | No |  |
| spl_a |  | 768K | spl.img | yes | Secondary program Loader, boot program of ACore | No | 起A核的代码 |
| spl_b |  | 768K |  |  |  | No |  |
| MCU_a |  | 6.5M | MCU_J6E_Midtrim_A.img | yes | MCU APP partition | Yes | sailautosar.elf |
| MCU_b |  | 6.5M |  |  |  | Yes | sailautosar.elf_backup |
| nvm |  | 5.75M |  |  | 预留 | Yes |  |
| kds |  | 256K | kds_brdid_xx.img | no | Board ID info | No | No, Board info will be stored in MCU side |

Does QTI support?

issues:

1. Does QTI support  add a calibration partition for config data?
2. How SWC use this partition data? copy this data to SRAM/DDR when startup?

Informations:

1. gpt_main0.bin and gpt_backup0.bin , seems store information of each partition
2. How PBL detects a bootable GPT partition
3. generating GPT with ptools.py

NOTE: GPT is autodetected if GUIDs are present in partition.xml.

input partition.xml → output

The following files are output: gpt_main0.bin – Primary GPT header and partition tables gpt_backup0.bin – Backup GPT header and partition tables rawprogram0.xml – How to program files to the device patch0.xml – How to patch zeros in the partition tables

Reference:

https://docs.qualcomm.com/bundle/KBA-240307123058/resource/KBA-240307123058_REV_1_Resizing_SAIL_Boot_Partitions.pdf

https://docs.qualcomm.com/bundle/80-N7350-1/resource/80-N7350-1_REV_C_Guid_Partition_Tables_and_Programming.pdf

https://docs.qualcomm.com/bundle/resource/topics/80-42846-145/nor-flash.html
