# Taiji  Cubas Update

> Source: /spaces/CARSFW/pages/5155552736/Taiji+Cubas+Update
> Last modified: 2024-12-17T10:14:55.000+01:00

---

|  | Question |  |  |
| --- | --- | --- | --- |
| 1 | C:\Repo\taiji\Autosar\CnConvBase\OsServices_RtaOS\Service.ContextSwitcher\ContextSwitcher_Os.c 24,9: #ifndef CUBAS_STACK_EN 42,8: #ifdef CUBAS_STACK_EN 44,11: #endif /* CUBAS_STACK_EN */ 144,9:     #ifdef CUBAS_STACK_EN 276,11:         #ifndef CUBAS_STACK_EN 278,13:         #endif /* CUBAS_STACK_EN */ 406,11:         #ifndef CUBAS_STACK_EN ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_15-18-21.png) |  |  |
| 2 | ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_15-18-38.png) |  |  |
| 3 | How to fix ErrorHook ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-45-31.png) |  |  |
| 4 | ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-26-57.png) |  |  |
| 5 | ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-28-47.png) |  |  |
| 6 | C:\Repo\taiji\Config\FuSa\SafeStartup\SafeStartup.Config\src\SafeStartup_Callout.c ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-30-42.png) |  |  |
| 7 | ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-32-5.png) |  |  |
| 8 | C:\Repo\taiji\Config\FuSa\Aurix\FITManager\FIT_MPU.Config\FIT_MPU_Cfg.c ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-35-54.png) |  |  |
| 9 | C:\Repo\taiji\Config\FuSa\Aurix\FITManager\Au_FITM.Config\Au_FITM_Cfg.c ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-37-47.png) |  |  |
| 10 | C:\Repo\taiji\Config\Autosar\stdcore\Cubas\CubasBSWCfgTemp\BswStubs\ContextSwitcher_SafeTag.h ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-41-47.png) |  |  |
| 11 | C:\Repo\taiji\Config\Autosar\os-services\Service.ExceptionHandling\ExceptionHandling_Callout.c ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-42-49.png) |  |  |
| 12 | C:\Repo\taiji\Config\Autosar\os-services\Service.ContextSwitcher\ContextSwitcher_Callouts.c 45,9: #ifndef CUBAS_STACK_EN 301,9: #ifndef CUBAS_STACK_EN C:\Repo\taiji\Config\Autosar\os-services\Service.ContextSwitcher\ContextSwitcher_if_cfg.h 114,9: #ifndef CUBAS_STACK_EN 124,9: #ifndef CUBAS_STACK_EN |  |  |
| 13 | C:\Repo\taiji\Config\Autosar\lifecycle\Service.EcuModeManagerEcuM\EcuModeManagerEcuM_ProjectCallouts_Trusted.c |  |  |
| 14 | C:\Repo\taiji\Config\Autosar\bsp-tc377tp\startup\MCAL.Startup\Startup_Core0.c 357,8: #ifdef CUBAS_STACK_EN |  |  |
| 15 | ![](../../../_images/Taiji%20%20Cubas%20Update/image-2024-12-17_16-51-31.png) |  |  |
| 16 | C:\Repo\taiji\Config\Autosar\bsp-tc377tp\platform\CNCONVBASE\chery\EcuAL.ExtWdg\ExtWdg_Cfg.h 48,9: #ifndef CUBAS_STACK_EN |  |  |
| 17 | C:\Repo\taiji\Autosar\CnConvBase\lifecycle\Service.EcuModeManagerEcuM\EcuManager_OsInitTask_Core0_Asil.c 34,9: #ifndef CUBAS_STACK_EN /* Only Vector stack need this file */ 137,18: #endif /*#ifndef CUBAS_STACK_EN*/ |  |  |
