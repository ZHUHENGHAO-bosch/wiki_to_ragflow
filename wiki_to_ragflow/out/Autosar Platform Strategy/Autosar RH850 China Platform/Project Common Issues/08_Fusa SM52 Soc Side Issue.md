# 08_Fusa SM52 Soc Side Issue

> Source: /spaces/CARSFW/pages/2799708905/08_Fusa+SM52+Soc+Side+Issue
> Last modified: 2023-05-06T04:28:36.000+02:00

---

### Information

Fusa SM52 Safe HMI, SCC request TT CRC From SOC Open WFD  and get the CRC value over a long link, as below picture. Now Geely project have some issue, and some improve method. Other project can refer it.

![](../../../_images/08_Fusa%20SM52%20Soc%20Side%20Issue/image2023-3-1_20-53-58.png)

1 QNX aps issue

Fusa process (inc-dispatcher, signature-unit-controller, system-info-handler)should run in System partition. But occasionally, we found fusa process run in other partition.(It is a QNX issue)

It is high probability that SM52 Safe HMI - BSM(SCC side) received CRC  timeout from SOC when qnx aps issue.

We met two case now:

a, signature-unit-controller run in pAudio

b, inc-dispatcher run in pAndriod

![](../../../_images/08_Fusa%20SM52%20Soc%20Side%20Issue/image2023-3-1_20-54-24.png)

Work around method:  After fusa process startup, pull back it  to system partition

2 Inc-Dispatcher issue

When inc-dispatcher run in other partition,  Inc-Dispatcher will never receive SCC message and is block by select() API; When Inc-dispatcher run in system partition, it also have block issue.

there are two issue here:

a, Misuse QNX API select().  Should reset select() parameters before using it. (QNX API Request).

b, No notification to Inc-Dispatcher when safety channel buffer full.  INC-TP need also update the code.

3 Ongoing: improve Fusa process priority

Need improve Fusa process priority with ESA team

GEELY ongoing, will select one from below after test.

| fusa process | priority | partition |
| --- | --- | --- |
| inc-dispatcher/suc/sih | 30r | System |
| inc-dispatcher/suc/sih | 45r | System |
| inc-dispatcher/suc/sih | 80r | System |
| inc-dispatcher/suc/sih | 30r | pSafety |

4 others/improve ( add useful log)

SCC:

user-1419f adds lots of useful information in SCC side. When error raised, below information will be recorded by SafeStateHandler.

typedef struct { BSM_Component_ID_e Component_ID ; BSM_ROI_ID_e ROI_ID ; BSM_ReturnStatus_e status ; uint8 AddInfo ; uint8 bsmTxIncTimeoutCnt ; uint16 bsmRxIncTimeoutCnt ; uint32 bsmCrc ; uint16 BsmRoistatus ; uint16 ssmIncTimeoutCnt ; uint32 ErrOutState ; uint32 deltTime ; uint32 TxTime ; } svh_TellTale_CallbackData_s ;

SOC:

need to add

1 snapshot cluster hmi and save when checked crc error

2 show system information( cpu loading etc)

3 show fusa process in which partition

4 other detail infor in each fusa module, help to identify  where the issue occured. ( need discuss with other project )

### Solution

| Affected Project | Variant | FixStatus | RTC/Gerrit |
| --- | --- | --- | --- |
| GEELY |  | COMPLETED | 1 QNX aps issue https://rbcm-gerrit.de.bosch.com/c/external/qualcomm/qnx/snapdragon-auto-gen3-hqx-1-2-1_hlos_dev_qnx/+/569823 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/signature-unit-controller/+/569831 (SUC) please check inc-dispacter/sih etc. 2 Inc-Dispatcher issue a inc-dispatcher https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/inc-dispatcher/+/569594 b inc-tp: https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/platform/inc_tp/+/569478 |
| GWM | GWM-B07 Main | COMPLETED | 1 QNX aps issue https://rbcm-gerrit.de.bosch.com/c/external/qualcomm/qnx/snapdragon-auto-gen3-hqx-1-0_hlos_dev_qnx/+/584687 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/signature-unit-controller/+/584694 2 Inc-Dispatcher issue a inc-dispatcher https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/inc-dispatcher/+/584692 b inc-tp: https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/platform/inc_tp/+/570079 |
| GWM-SOP10_OverSea | COMPLETED | 1 QNX aps issue https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/signature-unit-controller/+/585136 https://rbcm-gerrit.de.bosch.com/c/external/qualcomm/qnx/snapdragon-auto-gen3-hqx-1-0_hlos_dev_qnx/+/585137 2 Inc-Dispatcher issue a inc-dispatcher https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/inc-dispatcher/+/585125 b inc-tp: https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/platform/inc_tp/+/584658 |
| GWM-SOP15 | COMPLETED | 1 QNX aps issue https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/signature-unit-controller/+/585140 https://rbcm-gerrit.de.bosch.com/c/external/qualcomm/qnx/snapdragon-auto-gen3-hqx-1-0_hlos_dev_qnx/+/585141 2 Inc-Dispatcher issue a inc-dispatcher https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/inc-dispatcher/+/585128 b inc-tp: 之前就有了 |
| BYD |  | COMPLETED | [BYD][DX][SOC]put process into system partition for aps issue (I7766e79f) · Gerrit Code Review (bosch.com) [BYD][DX][SOC]reset select() parameters before call it everytime (Iaf077316) · Gerrit Code Review (bosch.com) [BYD][DX][SOC]Inc_tp: code robust for inc_tp (I8f5bbe1b) · Gerrit Code Review (bosch.com) |
| GAC |  | COMPLETED | 1 QNX aps issue https://rbcm-gerrit.de.bosch.com/c/projects/taiji/qnx/bosch/housekeeping/qcom_qnx/+/576216 https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/signature-unit-controller/+/576221 2 Inc-Dispatcher issue a inc-dispatcher https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/cluster/safetyapps/inc-dispatcher/+/570086 b inc-tp: https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/qnx/bosch/platform/inc_tp/+/570114 |
