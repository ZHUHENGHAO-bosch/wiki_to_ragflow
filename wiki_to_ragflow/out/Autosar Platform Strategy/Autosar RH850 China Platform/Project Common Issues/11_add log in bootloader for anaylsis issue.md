# 11_add log in bootloader for anaylsis issue

> Source: /spaces/CARSFW/pages/3053624291/11_add+log+in+bootloader+for+anaylsis+issue
> Last modified: 2023-07-24T07:43:53.000+02:00

---

## 优化bootloader下fusa log打印(不限制长度)

背景：

1. 很早前，在bootloader下没有打印 fusa 的safe errmem里的数据，如果出现在app里因fusa检查出异常 reset 25次进boot后没有log，不知道reset的原因。
2. 所以做了优化，可以打印len<80byte的 fusa 错误数据
3. 但像MPU，FEINT, SYSERR等错误类型，所需log字节数比较多的，就不能打印全，从而不能精确定位问题，比如 2bit ECC Error 地址等。

为了解决3. 优化了代码，去掉了80 Byte字节长度限制；打印了进bootloader的reset次数

注意：

用while(not tail) { 每次打印80byte，直到打印完 }；这种方式不可行。因为对应300+byte打印所需耗时较长，会导致升级功能失败（wang forest 已测试验证）。

所以用了每500ms打印80byte的方式打印，直到打印完成。

### Fix Status

| Affected project | FixStatus | RTC/Gerrit Linkage |
| --- | --- | --- |
| BYD |  |  |
| GEELY | COMPLETED | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/vector/vector-fbl/+/615549 |
| GWM | COMPLETED | https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/vector/vector-fbl/+/597208 |
| GAC | COMPLETED | https://rb-alm-20-p.de.bosch.com/ccm/web/projects/GAC_IDC#action=com.ibm.team.workitem.viewWorkItem&id=1725501 |

## print QM Log in bootloader

![](../../../_images/11_add%20log%20in%20bootloader%20for%20anaylsis%20issue/image-2023-5-19_19-8-47.png)

### Fix Status

| Affected project | FixStatus | RTC/Gerrit Linkage |
| --- | --- | --- |
| BYD | COMPLETED | https://rbcm-gerrit.de.bosch.com/q/topic:qm_log https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/bootloader-rh850/vector/vector-fbl/+/613183 |
| GEELY |  | https://rbcm-gerrit.de.bosch.com/q/topic:qm_error_log |
| GWM |  |  |
| GAC | COMPLETED | https://rbcm-gerrit.de.bosch.com/q/topic:RTC1-1834797_printbootlog https://rbcm-gerrit.de.bosch.com/q/topic:7987err |
