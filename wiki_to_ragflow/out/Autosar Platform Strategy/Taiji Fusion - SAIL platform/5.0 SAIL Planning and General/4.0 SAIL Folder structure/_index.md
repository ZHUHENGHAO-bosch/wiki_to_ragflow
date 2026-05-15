# 4.0 SAIL Folder structure

> Source: /spaces/CARSFW/pages/4704583139/4.0+SAIL+Folder+structure
> Last modified: 2024-12-02T08:02:57.000+01:00

---

## Overview

This page is to create folder and repo structure for SAIL platform

Follow J6E structure, Keep config inside the component folder itself

> **INFO: Repo command for SAIL Platform**
> repo init -u cm_gerrit:projects/taiji/manifests -b rb-ccufusion_main_dev -m rb-patac-ccufusion.xml -g sail

## 0602-[SGM CCU]Source Code download and build

#### Legend:

means repo

First level folder

Second level folder

Third level folder

#### Folder structure for SAIL platform

c ust_apl

lib

patac_lib

platform_lib

asw

asw_as

build

config

cubas

mcalQc

qccfg

platform

rbBsw - Service layer components

rbHsw - CDDs and Own MCAL components

safetyApps

stdcore - Core stack

cubas

qcbase

rtaOs

.......

sailtools

discussed with integration team LU Weihua (XC-CP/ESA2-CN)

- path /tools  folder already exists in ccufusion project, should modify  → sailtools
- repo name have rules

![](../../../../_images/4.0%20SAIL%20Folder%20structure/image-2024-11-13_16-29-43.png)

| Repo | path | description |
| --- | --- | --- |
| projects/ccufusion/sail/cust_apl/asw | cust_apl/asw | All application relevant components LIU Dezhi (XC-CP/ESW2-CN) Check with AS once |
| projects/ccufusion/sail/cust_apl/lib/patac_lib | cust_apl/lib/patac_lib | Library from PATAC |
| projects/ccufusion/sail/cust_apl/lib/plaform_lib | cust_apl/lib/plaform_lib | Sail bosch platform lib |
| projects/ccufusion/sail/cust_apl/build | cust_apl/build | Build out folder, cmake and relevant folder and files |
| projects/ccufusion/sail/cust_apl/config | cust_apl/config | Config for stdcore components liek Cubas, Rta-os, QcMcal |
| cnconvbase/sail/platform/rbBsw | platform/rbBsw | All BSW and service layer components like com. lcm, diag,.... |
| cnconvbase/sail/platform/rbHsw | platform/rbHsw | All CDD and own Mcal related modules |
| cnconvbase/sail/platform/stdcore/cubas | platform/stdcore/cubas | Cubas stack |
| cnconvbase/sail/platform/stdcore/qcbase | platform/stdcore/qcbase | QC CDD and MCAL modules |
| cnconvbase/sail/platform/stdcore/rtaOs | platform/stdcore/rtaOs | RTA-OS from ETAS |
| cnconvbase/sail/platform/safetyApps | platform/safetyApps | All FuSa related components |
| cnconvbase/sail/sailtools | sailtools | All tools can be kept here ![warning](https://inside-docupedia.bosch.com/confluence/plugins/servlet/twitterEmojiRedirector?id=26a0) If the tools size is big, better to use antifactory → not to deliver in this repo |
