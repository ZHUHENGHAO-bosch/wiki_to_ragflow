# SCC Safe Temperature monitoring Configuration

> Source: /spaces/CARSFW/pages/2865697758/SCC+Safe+Temperature+monitoring+Configuration
> Last modified: 2023-03-21T09:01:42.000+01:00

---

### McAL.TempSensor_Aurix

Repo path: Config/Autosar/bsp-tc377tp/platform

Configuration Steps:

Configure Upper and Lower limit for DTS and DTSC sensors

We can refer the China Convergence Platform configuration for threshold values

### Service.TempMon

Repo path: ??

Step 1 (TempMon_cfg.h) : Configure tempMonSensorCfg with Sensor ID, lowerLimit, UpperLimit, and Ministep (To be done for DTS and DTSC sensors)

Step 2 (TempMon_cfg.c): Configure Temperature sensors configuration parameters for each sensor in TempMon_cfg_init API

- sensorId
- mcalSensorId
- sensorTemperature
- dampingCfg.initialValue
- dampingCfg.dampingValue
- dampingCfg.samplingInterval
- dampingData.filteredValue_ui32
- getTemepatureFunc

Step 3 (TempMon_SensorHandler.c): Implement TempMon_SensorRegistration API inside which we need to call TempMon_RegisterForNotification with

- SensorID
- Callback API
- Lower limit
- Upper limit and
- Min Step

Step 4(TempMon_SensorHandler.c): Implement callback API in Step3 and inside check the temperature threshold value configured in McAL.TempSensor_Aurix, if the value is not inside the threshold call Safe State Handler

Step 5 Init APIs: Below API has to be called in EcuModeManagerEcuM_Callout_DriverInitOne (in the same order)

- TempMon_SensorRegistration
- TempMon_Init
