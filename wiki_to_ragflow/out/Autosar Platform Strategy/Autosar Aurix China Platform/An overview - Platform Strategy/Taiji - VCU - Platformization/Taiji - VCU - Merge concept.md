# Taiji - VCU - Merge concept

> Source: /spaces/CARSFW/pages/6989451061/Taiji+-+VCU+-+Merge+concept
> Last modified: 2026-05-08T12:00:54.000+02:00

---

## Overview Repo strategy Variant Matrix

## Overview

This page is to summarize how to make common repos for VCU and Taiji

## Repo strategy

- Too many repos in Taiji (145 repos) - Taiji - Current VCU Repo and Folder structure - XC-CT China - Docupedia
- We can go with VCU repo and folder structure - (41 repos)

![](../../../../_images/Taiji%20-%20VCU%20-%20Merge%20concept/Taiji_Vcu_Strategy.png)

| Folder | Repos | Comment | Discussion |
| --- | --- | --- | --- |
| Restricted | VCU repos | Can we reuse the CCU repos?? We can create a special branch like Taiji_Vcu_Maindev |  |
| BswPlatform | Branch can be restricted to PATAC |  |
| BswPlatform_CFG |  |  |
| Vector_bsw |  |  |
| Vector_bsw_cfg |  |  |
| Tools |  |  |
| Build |  |  |

## Variant Matrix

| Variant | Target Board | Stack |
| --- | --- | --- |
| TC37x | Chery/Maxus | Vector |
| TC37x | Chery/Maxus | Cubas |
| TC38x | CCU | Vector |
| TC39x | VCUplus | Vector |
