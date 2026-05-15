# Improve OS ErrorHook log

> Source: /spaces/CARSFW/pages/3223111526/Improve+OS+ErrorHook+log
> Last modified: 2023-07-28T07:07:23.000+02:00

---

Backgroud：GEELY  has OS ErrorHook issue Occasionally, only once.

After Analysis：

Wed Jun 14 08:52:14 2023

0D0204010730390001

Wed Jun 14 08:52:14 2023

0D020401073039000C0107E5070701F3 -> 0x39 -> Vector OS ErrorHook error OSServiceId_SetRelAlarm , E_OS_STATE

![](../../../../_images/Improve%20OS%20ErrorHook%20log/image-2023-7-28_13-0-26.png)

Most likely one of the three below：

SetRelAlarm(evtCfg->eventList[evID].osAlarm, waitTime, 0);

SetRelAlarm(EventPropertiesPtr->eventConfig[evID].osAlarm,EventPropertiesPtr→eventConfig[evID].osWaitingTime_ms,0);

SetRelAlarm(ALR_SystemM_CommonSequencer, SYSTEMMNGR_CYCLE_TIME, 0);

But have no more information to Identify which one is.

So add more information in ErrorHook(), to print which Task, ISR, and Alarm if  OSServiceId_SetRelAlarm.

RTC:

https://rb-alm-20-p.de.bosch.com/ccm/web/projects/ECARX#action=com.ibm.team.workitem.viewWorkItem&id=1808774

Reference（SetRelAlarm issue in GW VCU）:

GM-VCU shutdown pullback issue:

FW Shutdown pullback during NvM_WriteAll.msg
