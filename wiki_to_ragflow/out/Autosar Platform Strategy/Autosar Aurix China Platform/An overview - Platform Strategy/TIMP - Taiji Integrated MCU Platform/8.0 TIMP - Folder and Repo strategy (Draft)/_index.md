# 8.0 TIMP - Folder and Repo strategy (Draft)

> Source: /spaces/CARSFW/pages/5156739042/8.0+TIMP+-+Folder+and+Repo+strategy+Draft
> Last modified: 2025-09-17T10:00:49.000+02:00

---

## Overview

This page is summarize the folder structure for TIMP

Check this page for CP and AS strategy: Repo Strategy between CP and AS - XC-CT China - Docupedia

Queries:

1. Whether to use flux for BSW platform modules
2. Whether to use Make or Ninja for Build system
3. Can we keep Mom and Vfc in Stdcore - dont care on these part since it belong to AS

We will try to reuse the existing repos which is in our control and create only required ones

### Folder structure

Top level Folder

Second level folder

Repo

fbl

hsm

autosar

application

idcAppl

timpPlatformbase

rbBsw

- Arch - Design artifacts test - UT and QAC reports xxIf xxCore

rbHsw

safetyApps

- AurixFusa J6EFusa SailFusa CommonFusa

stdcore

- bswStack CubasAurix/Cubas_2024 CubasJ6E -2024_04 - double check should be version base ...... VectorAurix mcal Ifx Tricore j6E qC .....

- rtaos tricore qc j6E ....

buildPlatform = TIMP Build environment

Sailconfig (similar structure for FusionCfg)

AutosarCfg

rbBsw

- xxCfg

rbHsw

- xxCfg

safetyApps

stdcoreCfg

- cubasCfg mcalCfg

buildCfg

- Build batch files and debug scripts Artifactory scripts and Json config file Cmake and Linker files

toolCfg

Thirdparty

custAppl - Modules that interact with AS application

platformTools

- better to keep common tools in Artifactory BtcTools Dlt parser Ramrom Core Abs Rtmo ...

#### Existing Repos which can be reused in TIMP

| Pf/Cfg | Repo | Existing | Description |
| --- | --- | --- | --- |
| Platform | rbBsw | cnconvbase/sail/platform/rbBsw |  |
| rbHsw | cnconvbase/sail/platform/rbHsw |  |
| SafetyApps-SailFuSa | cnconvbase/sail/platform/safetyApps |  |
| PlatformTools | cnconvbase/sail/sailtools |  |
| Stdcore-Sail Cubas | cnconvbase/sail/platform/stdcore/cubas |  |
| Stdcore-Sail RTAOS | cnconvbase/sail/platform/stdcore/rtaOs |  |
| Config | CustAppl | projects/ccufusion/sail/cust_apl/asw |  |
| buildCfg | projects/ccufusion/sail/cust_apl/build |  |
| Stdcore-SailCfg | projects/ccufusion/sail/cust_apl/config |  |
| Stdcore-IdcTaijiCfg | projects/taiji/cnconv/config/autosar/stdcore/Chery |  |
