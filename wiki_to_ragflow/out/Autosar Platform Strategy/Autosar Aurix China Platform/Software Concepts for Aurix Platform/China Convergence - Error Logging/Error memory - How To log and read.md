# Error memory - How To log and read

> Source: /spaces/CARSFW/pages/3197936222/Error+memory+-+How+To+log+and+read
> Last modified: 2023-06-30T10:55:25.000+02:00

---

Most function Modules in SCC side can call Error memory API to record error data, and those data will be transmitted to soc side through INC channel.

So we can get useful information from scc_errmem_dump.txt in soc qnx log files.

## 1. How to use error memory API to log

Here is an example about how to call error memory API:

![](../../../../_images/Error%20memory%20-%20How%20To%20log%20and%20read/image-2023-6-30_14-57-42.png)

Note:

1. Error data should be converted to ASCII format , unless error data can't be parsed to right format by error memory module  and we will see unreadable character.

We can use sprintf or snprintf function to convert data format, like below:

- ( void )sprintf(( char *)&SEH_DLT_Buffer[SEH_TotalErrSize], "Fusa_GID_%u_SID_%u#NULL#" ,groupErrId_en, subErrId_en);
- ( void )snprintf(errmem_msg_buf, sizeof (errmem_msg_buf), " INC-TP/AR: 9ms Main function consumes more CPU time" );

2. Return value is useful, because if INC is not ready at startup, and we do not judge return value, message will be missing.  Function module developer should decide if return value is not ok, the error message should be sent again or not after return is ok.

## 2. How to read scc_errmem_dump.txt in SOC side

Method 1: Read log in moba software

Find the path of error memory file by input command as below：

- cd /var/log
- ls
- cat scc_er +Tab key

Log message will be printed in moba and the picture below shows the information about each part:

![](../../../../_images/Error%20memory%20-%20How%20To%20log%20and%20read/image-2023-6-30_16-3-57.png)

Method 2: Find scc_errmem_dump.txt in nfs_log file

![](../../../../_images/Error%20memory%20-%20How%20To%20log%20and%20read/image-2023-6-30_16-8-2.png)
