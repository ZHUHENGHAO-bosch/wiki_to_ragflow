# CCU SAIL OPL

> Source: /spaces/CARSFW/pages/4966965070/CCU+SAIL+OPL
> Last modified: 2024-12-30T07:19:11.000+01:00

---

used for syncing information

![](../../../../_images/CCU%20SAIL%20OPL/image-2024-11-11_11-24-46.png)

| NO | Description | Status | Raised by | Responsible | Comment |
| --- | --- | --- | --- | --- | --- |
| 1 | SAIL Repo create , need discuss before 15 Nov 2024 | CLOSE | liu dezhi |  | 12.20 sail basic function ready to PATAC 4.0 SAIL Folder structure |
| 2 | Cubas related information sync SUM HSM ... | CLOSE | liu dezhi |  | HSM, no hardware HSM, need security team take care. BSW, reuse J6E OS, we already have SUM, need project kickoff, then PO to ETAS(already highlight PATAC) |
| 3 | Need NVM feature? or Data stored in MD and sync to SAIL after startup? | CLOSE | liu dezhi |  | 2024.12.16 AutoRFI has been raised. 07557017/07488998：AutoRFI for SAIL MemAcc featur 2024.11.8 conformed with QC: MEM_ACC now not standard API available. If need this , Need Bosch raise feature & Which Partition can use for NVM 2024.11.11 PATAC conformed, need store data in SAIL. try to raise new feature to QC, now consult Zhu jia the process. highlight to TPM in meetings |
| 4 | What function and which team will develop on SAIL? Confirmed: ESW2(Autosar&Fusa)，ESW1(Ethernet), ESS(security), PATAC AS? Need Daddy? | CLOSE | liu dezhi |  | 2024.11.11 There will be Bosch CP , Bosch AS, PATAC co-dev on SAIL. Patac use lib, AS use source code CP’s repo no need consider Daddy and Flux. |
| 5 | Need SAIL support wakeup? | CLOSE | liu dezhi |  | No need. conformed with HW |
| 6 | Do we need Flux and Daddy Cmake setup | CLOSE | Praveen |  | Current SAIL environment is based on J6E environment. Need confirmation to clean the environment 2024.11.11 ldz no need. please refer to No. 4. |
| 7 | R-Core ASW and A-Core ASW IPC protocol & port definition shall be clarified, info about protection mechanism (ETH frame level? CAN msg level?) is unclear. | PENDING | yan eason |  | 2024.12.2 Paused the development of sail |
| 8 | R-Core CUBAS RTE port definition & protection mechanism (SUM?) shall be determined. | PENDING | yan eason |  | 2024.12.2 Paused the development of sail |
| 9 | Depending on item 4, we need daddy port definitions & protection mechanism (use SUM as well or E2E? ) if daddy & ASWs are going to be deployment in SAIL. | CLOSE | yan eason |  | DADDY is not under consideration. |
| 10 | Timesync system arch design shall be determined. | CLOSE | yan eason |  | Timesync mechanism & design between SAIL & Main domain. - Gptp, i.e. EthTsync is selected. |
