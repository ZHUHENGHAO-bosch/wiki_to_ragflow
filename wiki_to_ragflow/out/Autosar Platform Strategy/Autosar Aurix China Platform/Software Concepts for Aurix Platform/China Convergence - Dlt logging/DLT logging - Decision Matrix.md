# DLT logging - Decision Matrix

> Source: /spaces/CARSFW/pages/2417034372/DLT+logging+-+Decision+Matrix
> Last modified: 2024-01-26T03:32:09.000+01:00

---

|   |   |
| --- | --- |
| Status | COMPLETED |
| Owner | Jayaraj Praveen (BCSC/ENG1) |
| Stakeholders | user-1f19a GAO Carven (XC-CP/ESW2-CN) NIU Newton (XC-CP/ESW2-CN) Mohan Kishor K B (MS/ENE-HP-EP1-XC) user-14275 Senthil Rajan Arunachalam (MS/EMC1-SWC) |
| Decision | China Convergence Projects will use Vector DLT for DLT logging |
| Due Date | 23 Sep 2022 |

## Introduction

We have three architectural modules to do DLT logging

1. Vector Dlt over PduR
2. CAP Dlt
3. Service.DebugTrace

| Attribute | Vector Dlt over PduR | CAP Dlt | Service.DebugTrace |
| --- | --- | --- | --- |
| Cost | Company wide licensed | No Cost | Bosch Module |
| Integration effort | High | Moderate | Low |
| SWC usage | Supported | Via the Wrapper | Via the Wrapper |
| INC Support | DltIf module available in VCU | DltIf module available in China local projects | Supports only CI2 IPC |
| Non-Verbose logging mode | Yes | Yes | Yes |
| early startup dlt logs | Available only after Dlt_Mainfunction is called But Workaround was made by ESO | Supports logging early message | Supports |
| Wrapper availability Service.DltWrapper | Yes | Yes | No |
| Support and Maintainability | Yes (On Every SIP) | No/ Old Version of CAP. If we need new then we need to purchase from CAP | We need to give requirement to Cerberus |
| ESO Logging Architecture | Yes | No | No |

Decision Matrix by Cerberus team

Diagnostic Log and Trace (DLT) - XC-CT Cerberus Platform - Docupedia (bosch.com)
