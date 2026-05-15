# Getting OS Hook Error from SSH

> Source: /spaces/CARSFW/pages/3340222989/Getting+OS+Hook+Error+from+SSH
> Last modified: 2023-08-16T10:24:41.000+02:00

---

### 1.1. Overview

If the system occurs some errors for example the MPU exception or stack overflow, it shall enter to os hook function to record the error information.

The OS hooks are implemented by the Platform team, and they create some callout functions in the hooks, we could save the detailed error information in these functions.

Currently, use the SSH interface to save the log and trigger the reactions.

This wiki is used to explain how to analysis the error log recorded in the SSH.

To analysis the os error log, first to check the SSH ID and find the exact hook called, and then go to the detailed functions and check the record log's meaning.

### 1.2. OS Hooks Callout Functions

In current version there are four callout functions, list them under below.  As the input parameters are different for each function, the error log layout differs.

OsHooks_Callout_Shutdown_ErrorHandling

OsHooks_Callout_ProtectionHook_ReportError

OsHooks_Callout_ProtectionHook_Handling

ExceptionHandling_ErrorCallout

OsHooks_Callout_ProtectionHook_ReportError

This function is called in error hook and protection hook. For the error hook,there are critical error and warning error two types.  The critical error shares the same SSH ID with the protection hook error.

For the warning error , the SSH group ID is 16 and the suberror id is 74 .

For the critical error, the SSH group ID is 16 and the suberror id is 75 .

The only difference between the two type is that critical one would trigger a reset while the warning one won't.

For error hook log,the first 15 bytes differ for different Autosar version, the below chart shows the layout for Autosar 4.3 version.

Because the protection hook and error hook share the same callout function, the same log may be recorded in two locations.

Hint:

Below chart lists the SSH error log except the first and last checking byte. So do other charts.

And the byte 6 to byte 14 stand for various meaning for different error, should refer to the code for detail information.

| Byte | Log Information |
| --- | --- |
| Byte 0 | OS service ID type |
| Byte 1 | OS error type |
| Byte 2 | OS status type forth byte |
| Byte 3 | OS status type third byte |
| Byte 4 | OS status type second byte |
| Byte 5 | OS status type first byte |
| Byte 15 | module ID first byte |
| Byte 16 | module ID second byte |
| Byte 17 | OS error type |
| Byte 18 | task ID |
| Byte 19 | core ID |
| Byte 20 | ISR ID |

OsHooks_Callout_ProtectionHook_Handling

This function is called by OS protection hook.  The SSH group ID is 16 , the suberror id is 76.

| Byte | Log Information |
| --- | --- |
| Byte 0 | task ID |
| Byte 1 | ISR ID |
| Byte 2 | exception address first byte |
| Byte 3 | exception address second byte |
| Byte 4 | exception address third byte |
| Byte 5 | exception address forth byte |
| Byte 6 | OS error type |
| Byte 7 | data error address first byte |
| Byte 8 | data error address second byte |
| Byte 9 | data error address third byte |
| Byte 10 | data error address forth byte |

ExceptionHandling_ErrorCallout

The function is called in os protection hook, use this function to record the exception information.

The SSH group ID is 16 , the suberror id is 77 .

Hints:

The byte 0 could contains different information based on OS error type.

If the os type is IRQ, which means byte 14 is 0xFB,the byte 0 stands for interrupt source type;

if the os type is SYSCALL, which means byte 14 is 0xFA, the byte 0 stands for OS service ID;

in other cases, which means os exception 0x12 or protection memory 0xE, the byte0 stands for exception source, the high four bits stand for trap class ID, the low four bits stand for TIN ID.

For the PSW only three byte log stored, the second byte always be zero.

| Byte | Log Information |
| --- | --- |
| Byte 0 | Interrupt source ID, service ID or exception source |
| Byte 1 | PSW forth byte |
| Byte 2 | PSW third byte |
| Byte 3 | PSW first byte |
| Byte 4 | Return address forth byte |
| Byte 5 | Return address third byte |
| Byte 6 | Return address second byte |
| Byte 7 | Return address first byte |
| Byte 8 | task ID |
| Byte 9 | ISR ID |
| Byte 10 | data error address first byte |
| Byte 11 | data error address second byte |
| Byte 12 | data error address third byte |
| Byte 13 | data error address forth byte |
| Byte 14 | OS error type |

OsHooks_Callout_Shutdown_ErrorHandling

This callout is called in shutdown hook and panic hook. It will trigger SSH reset.

For the panic hook, the SSH group ID is 16 and the suberror id is 78 .

For the shutdown hook, the SSH group ID is 16 and the suberror id is 79 .

Hints :

The exception hook address shall be zero if the error is not a exception.

| Byte | Log Information |
| --- | --- |
| Byte 0 | OS task ID |
| Byte 1 | OS error type |
| Byte 2 | OS exception address first byte |
| Byte 3 | OS exception address second byte |
| Byte 4 | OS exception address third byte |
| Byte 5 | OS exception address forth byte |

### 1.3. OS SSH Error Log Analysis Example

Create a MPU reset error and after the SOC starts up, go to /Var/Log/scc_errmem_dump.txt, then find the latest SSH log. At the same time, the below log could be also found in the SCC side.

Fusa_GID_16_SID_76#21 42 851608 7CF12280 0C 36 F003C204 12 DE

The GID is 16 and SID is 76, that log is recorded in function ExceptionHandling_ErrorCallout .

The OS error type is 12, the 0x42 stands for exception source, that is Trap Class 4 TIN 2.

Detailed information is under below.

| Ignored | Group id | Ignored | Sub id | Ignored | ISR id/service id/exception source | PSW | RA address | task id | ISR id | data error address | os error type | Ignored |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fusa_GID_ | 16 | _SID_ | 76 | #21 | 42 | 08001685 | 8022F17C | 0C | 36 | F003C204 | 12 | DE |
