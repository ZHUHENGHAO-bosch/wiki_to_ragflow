# 12_bootloader下先拉pin通知再给SOC上电

> Source: /spaces/CARSFW/pages/3117068981/12_bootloader%E4%B8%8B%E5%85%88%E6%8B%89pin%E9%80%9A%E7%9F%A5%E5%86%8D%E7%BB%99SOC%E4%B8%8A%E7%94%B5
> Last modified: 2023-07-07T04:28:31.000+02:00

---

从抓到的时序可以看到，soc先上电，OPT1后拉起，需要scc端调整时序，在soc上电前拉起OPT1.

RTC Bug Ticket: https://rb-alm-20-p.de.bosch.com/ccm/web/projects/BYD%20DX#action=com.ibm.team.workitem.viewWorkItem&id=1783490

| Affected Project | Fix Status | Gerrit/RTC linkage |
| --- | --- | --- |
| BYD | COMPLETE | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/vector/vector-fbl/+/624531 |
| GEELY |  |  |
