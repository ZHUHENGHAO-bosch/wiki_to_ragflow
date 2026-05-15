# 1.0 TC4x FuSa - ADC - Safety analysis

> Source: /spaces/CARSFW/pages/6355321163/1.0+TC4x+FuSa+-+ADC+-+Safety+analysis
> Last modified: 2025-11-07T06:16:20.000+01:00

---

## Overview

Safe ADC acquisition

### ADC Overview

ADC consists of three sub functional blocks

- TM-ADC (Time Multiplexed ADC)
- DS-ADC (Delta-sigma)
- FCC (Fast capture compare)

TM-ADC: TM-ADC is based on successive approximation register (SAR) based architecture. It is mainly used for measurement of low bandwidth signals or for periodical measuring of sensor outputs

DS-ADC: DS-ADC is based on 2nd order delta-sigma modulator architecture. DS-ADC is used primarily to observe the AC characteristics of the input analog signal

FCC: FCC is a single bit analog comparator producing one bit digital output by comparing the input analog voltage against the programmed by the user 10-bit equivalent analog voltage. It is mainly used for peak current control applications

| Functional Block | TC4xx |
| --- | --- |
| ADC | General: In TC4XX we have ESADC, TMADC and FCC HW SMs : SM[HW]:ADC:RESULT_PLAUSIBILITY : The ADC functional block implements a check on the ADC and post processing channel results in hardware. The results are compared to a configurable threshold by comparator logic. If the ADC detects unexpected results outside the thresholds, it notifies the system. Each ADC module of TMADC, DSADC, EXMOD, FCC and CDSP provides an independent digital comparator. For TMADC, DSADC, EXMOD and CDSP a lower and an upper boundary value can get set. FCC allows just one threshold. Threshold values can be updated during run time via a hardware trigger in a deterministic way External SW SMs: ESM[SW]:ADC:MODULE_REDUNDANCY : Faults in the functions of ADC can be detected by implementing analog to digital conversion by two independent channels. Independent channels could be homogeneous or heterogeneous ESM[SW]:ADC:RESULT_PLAUSIBILITY: Consistency monitoring is required to detect faults in the analog to digital conversion. The Application Software shall compare the ADC and post processed channel results against application constraints. For example, against the physically possible changes of the sensed values between measurements. If the Application Software detects unexpected results during these checks, it shall notify the system about the presence of a fault ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) When we implement SM[HW]:ADC:RESULT_PLAUSIBILITY then we don't need to implement ESM[SW]:ADC:RESULT_PLAUSIBILITY ESM[SW]:ADC:VAREF_PLAUSIBILITY: To allow Application Software to enable independent ADC operation, Application Software shall perform plausibility check on VAREF as independent ADC module can be connected to one common VAREF pin. The Application Software shall implement a check of the ADC reference voltage (VAREF) either by an external monitor or by internally converting a known signal and compare the result with expected value. This check shall be executed periodically after a predefined number of conversions or time interval, for example once per Fault Tolerant Time Interval (FTTI). If the Application Software detects unexpected results during these checks, it shall notify the system about the presence of a fault ESM[SW]:ADC:BROKEN_WIRE_DETECTION: The Application Software shall implement broken wire detection diagnostics on all single physical inputs used for ADC conversion. This is single package pins that are not covered by a redundancy safety claim. If the Application Software detects unexpected results during these checks, it shall notify the system about the presence of a fault. ![(plus)](https://inside-docupedia.bosch.com/confluence/s/-3dmz00/9114/1yg1r0c/_/images/icons/emoticons/add.svg) If we use single input, then this is ESM is needed, if we use redundant input source then this is not needed. ESM[SW]:ADC:ISR_MONITOR: This ESM shall detect missing or unintended interrupts originating from the ADC module ESM[SW]:ADC:CHANNEL_CORE_SELF_DIAGNOSIS: The Application Software shall activate the Channel-core Self Diagnosis (CSD) on TMADC input channels periodically, for example once per FTTI, by sampling at least two of the known voltages provided in the TMADCx_CSDn.SEL register and evaluating the conversion result against the predefined configuration, Functional details of the CSD feature are described in the TMADC section of the User Manual |
