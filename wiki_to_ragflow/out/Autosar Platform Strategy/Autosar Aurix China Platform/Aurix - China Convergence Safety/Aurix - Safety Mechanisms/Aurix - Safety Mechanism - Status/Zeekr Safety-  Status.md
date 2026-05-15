# Zeekr Safety-  Status

> Source: /spaces/CARSFW/pages/2952320756/Zeekr+Safety-+Status
> Last modified: 2023-11-17T05:21:07.000+01:00

---

## 1. Platform SM Status

|   |   |   |   |   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S.NO | SM | Integration to Zeekr | SWRS Cfg | Unit Test Cfg | QAC Cfg | Int. Test (FIT) | Inspection Reviews | WorkON Review(SWRS Cfg) | WorkON Review (SWCDD) | L1L2 Test Spec Review | Open points/Defects | Remarks |
| 1 | Voltage Monitoring (Int) | Completed | Completed | NA | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
|  | Voltage Monitoring (Ext) | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 2 | RAM Monitoring (AuSM) | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 3 | Clock Monitoring | Completed | Completed | NA | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 4 | SM20-Safe State Handler | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 5 | Safe ADC - ADCP | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 6 | Self-Test-AuSS/Safe Startup | Completed | Completed | Completed | Completed | Manual test | Completed | Completed | Completed | Completed |  |  |
| 7 | Temperature Monitoring | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 8 | WDG (Int) | Completed | Completed | NA | NA | Completed | Completed | Completed | Completed | Completed |  |  |
|  | WDG (Ext) | Completed | Completed | NA | Completed | Manual test | Completed | Completed | Completed |  |  |
|  | Alive Supervision | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 9 | ROM Monitoring | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 10 | SM09 -Register Monitoring | Completed | Completed | NA | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 11 | SM04-Peripheral Protection | Completed | Completed | NA | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
|  | SM04 -Memory Protection | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |
| 12 | Safe DLT | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |  |  |

## 2. Project SM Status

| S.No | SM | SWRS | SWCDD | Safety Analysis | SW Construction - Code | SW Construction - UT | QAC | SW Construction- UDS | Integration Testing (FIT) | Inspection Reviews | WorkON Review (SWRS Cfg) | WorkON Review (SWRCDD) | L1L2 Test Spec Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SM16 - Safe Config | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |
| 2 | SM53 - Safe Tell-tale handler | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed | Completed |

## 3. FIT Status

|   |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SM | NAME | TC's | Total Failed | CART FAILURE | CART-BUG ID | PROJECT FAILURE | PROJECT-BUG ID | Status |
| 1 | RAM | 40 | 0 | 0 | NA | 0 | NA |  |
| 2 | ROM | 28 | 0 | 0 | NA | 0 | NA |  |
| 4 | MPU | 21 | 0 | 0 | NA | 0 | NA |  |
| Peripheral Protection | 44 | 0 | 0 | NA | 0 | NA |  |
| 6 | WDG_ALIVE | 14 | 0 | 0 | NA | 0 | NA |  |
| EXT_WDG | 2 | 0 | NA | NA | 0 | 0 |  |
| WDG_INTERNAL | 10 | 0 | 0 | NA | 0 | NA |  |
| 9 | REGM | 343 | 0 | 0 | NA | 0 | NA |  |
| 12 | IVM | 12 | 0 | 0 | NA | 0 | NA |  |
| EVM | 7 | 0 | 0 | NA | 0 | NA |  |
| 13 | TEMP | 4 | 0 | 0 | NA | 0 | NA |  |
| 16 | Safe Config | 5 | 0 | NA | NA | 0 | - |  |
| 18 | CLK | 10 | 0 | 0 | NA | 0 | NA |  |
| 23 | ADCP | 8 | 0 | 0 | NA | 0 | NA |  |
| 20 | Safe State Handler | 9 | 0 | 0 | NA | 0 | NA |  |
| 53 | Safe Telltale | 91 | 0 | NA | NA | 0 | NA |  |
| Functionality test |  |  |  |  |  |  |  |  |
| 14 | Aurix Startup SelfTest | 40 |  |  |  | 0 | 0 | CN Team |
| 15 | Safe DLT | 3 | 0 | 0 | 0 | 0 | 0 |  |

## 4. UT Status

|   |   |   |
| --- | --- | --- |
| Module Name | UT enabled/disabled | Status |
| MCAL.Startup | Yes |  |
| McAL.Stmr | Yes |  |
| Service.SystemTimer | Yes |  |
| Service.ContextSwitcher | Yes |  |
| Service.TimeStampLogger | Yes |  |
| Service.Time.ActiveWaitTime | Yes |  |
| Service.Time.PassiveWaitTime | Yes |  |
| Service.ContextSwitcher.Config | Yes |  |
| Service.ContextAbstractionMcal | Yes |  |
| # Cerberus Autosar Component |  |  |
| Service.BootManager | Yes |  |
| Service.CRC.CRC16 | Yes |  |
| Service.CRC.Crc8 | Yes |  |
| Service.Signum | Yes |  |
| Service.NVAbstraction | Yes |  |
| Service.FatalErrorLogger | Yes |  |
| Service.RealTimeMeasurement | Yes |  |
| Service.OsHooks | Yes |  |
| Service.ExceptionHandling | Yes |  |
| Service.OsHooks.Config |  |  |
| Service.IsrHandler.Config |  |  |
| EcuAL.UARTBufferHandler | Yes |  |
| EcuAL.AudioAmpDriver | Yes |  |
| Service.AudioAmpHandler | Yes |  |
| Service.VariantHandler | Yes |  |
| CDD_ErrorMemory | Yes |  |
| ECUAL.RTC | Yes |  |
| Service.AdcController | Yes |  |
| Service.AdcController.Config | Yes |  |
| EcuAL.I2cHandler | Yes |  |
| McAL.TempSensor_Aurix.Config | Yes |  |
| # Safety Application |  |  |
| SWC.SafeTelltale_SWC | Yes |  |
| SWC.SafetyAppsINCDispatcher | Yes |  |
| SWC.BoschSafetyMonitor | Yes |  |
| SWC.Service.SVHTelltales | Yes |  |
| SWC.SafeSoCStateMonitor | Yes |  |
| SWC.Service.SerializerDiagnostic | Yes |  |
| # Lifecycle Management components |  |  |
| Service.Interpolation |  |  |
| # SwcBacklightController |  |  |
| SwcBacklightController | Yes |  |
| # FUSA |  |  |
| Aurix.SafetyManager.Config | Yes |  |
| Aurix.RegisterMonitor.Config | Yes |  |
| Aurix.Clocksupervision | Yes |  |
| Aurix.Clocksupervision.Config | Yes |  |
| SafeStateHandler.SSH.Config | Yes |  |
| SafeStateHandler.SEH.Config | Yes |  |
| SafeStateHandler.SSH | Yes |  |
| SafeStateHandler.SEH | Yes |  |
| EcuAL.ExtWdg | Yes |  |
| EcuAL.ExtWdg.Config | Yes |  |
| CDD_KDS |  |  |
| SafeVoltageMonitor | Yes |  |
| SafeVoltageMonitor.Config | Yes |  |
| Aurix.SafetyStartup | Yes |  |
| Aurix.SafetyStartup.Config | Yes |  |
| Aurix.ADCPlausibility | Yes |  |
| Aurix.ADCPlausibility.Config | Yes |  |
| Aurix.PflashCrcChecker | Yes |  |
| Aurix.PflashCrcChecker.Config | Yes |  |
| AliveSupervisionInterface | Yes |  |
| AliveSupervisionInterface.Config | Yes |  |
| AliveSupervisionInterface.Callout | Yes |  |
| PeripheralProtection | Yes |  |
| PeripheralProtection.Config | Yes |  |
| SafeDltLogging.Config | Yes |  |
| SafeDLTLogging | Yes |  |
| AUTOSAR |  |  |
| MCAL.Startup.Config | NO |  |
| Service.SystemTimer.Config |  |  |
| Service.TimeStampLogger.Config |  |  |
| Service.ContextSwitcher.Config | Yes |  |
| Service.ContextAbstractionMcal.Config |  |  |
| Service.BootManager.Config |  |  |
| Service.NVAbstraction.Config |  |  |
| Service.FatalErrorLogger.Config |  |  |
| Service.RealTimeMeasurement.Config |  |  |
| Service.ExceptionHandling.Config |  |  |
| Service.OsHooks.Config |  |  |
| CDD_ThermalHandler |  |  |
| SafeStartup.Config | Yes |  |
| McAL.McuExtensions.Config |  |  |
| McAL.AurixCoreDriver |  |  |
| McAL.TempSensor_Aurix.Config |  |  |
| SWC.SafeTelltale_SWC | Yes |  |
| CDD.SafeConfig | Yes |  |
| Aurix.SafetyManager | Yes |  |
| Aurix.InternalVoltageMonitor.Config | NA |  |
| Aurix.InternalVoltageMonitor | Yes |  |
| Aurix.RegisterMonitor | Yes |  |
| Aurix.SafetyStartup.Config | Yes |  |
| Aurix.ADCPlausibility | Yes |  |
| Aurix.ADCPlausibility.Config | Yes |  |
| CA_Dlt |  |  |

### 4.1. OVER ALL UT REPORT

| ModuleName (UnitTest Name) | Build Succesful (MinGW) | Amount Testcases | Testcases failed | Function Hit | Function Total | Function Cov | Line Hit | Line Total | Line Cov | Branches Hit | Branches Total | Branches Cov |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ClockSupervision | TRUE | 8 | 0 | 3 | 3 | 100% | 13 | 13 | 100% | 4 | 4 | 100% |
| SVM | TRUE | 7 | 0 | 2 | 2 | 100% | 31 | 31 | 100% | 26 | 26 | 100% |
| AUSS | TRUE | 53 | 0 | 23 | 23 | 100% | 257 | 259 | 99% | 79 | 82 | 96% |
| SSH_UnitTest | TRUE |  |  | 3 | 3 | 100% | 17 | 17 | 100% | 8 | 8 | 100% |
| ASIF | TRUE | 11 | 0 | 5 | 5 | 100% | 27 | 27 | 100% | 8 | 8 | 100% |
| SHE | TRUE |  |  | 11 | 11 | 100% | 80 | 80 | 100% | 26 | 26 | 100% |
| Aurix_RegM | TRUE | 5 | 0 | 1 | 1 | 100% | 6 | 6 | 100% | 8 | 8 | 100% |
| PFCC | TRUE |  |  | 16 | 16 | 100% | 149 | 149 | 100% | 53 | 53 | 100% |
| SVMConfig | TRUE | 12 | 1 | 4 | 4 | 100% | 41 | 45 | 91% | 17 | 22 | 77% |
| Pflash | TRUE |  |  |  |  |  |  |  |  |  |  |  |
| ASIF_Callout | TRUE | 1 | 0 | 1 | 1 | 100% | 11 | 11 | 100% | 0 | 0 | 0 |
| PeriProt | TRUE | 9 | 0 | 4 | 4 | 100% | 26 | 26 | 100% | 10 | 10 | 100% |
| ASIF_Config | TRUE | 28 | 0 | 28 | 28 | 100% | 84 | 84 | 100% | 0 | 0 | 0 |
| SafeDltLogging | TRUE | 1 | 0 | 1 | 1 | 100% | 2 | 2 | 100% | 0 | 0 | 0 |
| AuSMCallout | TRUE | 112 | 0 | 1 | 1 | 100% | 64 | 64 | 100% | 30 | 30 | 100% |

## 5. QAC Warning list

Zeekr_QAC.xls
