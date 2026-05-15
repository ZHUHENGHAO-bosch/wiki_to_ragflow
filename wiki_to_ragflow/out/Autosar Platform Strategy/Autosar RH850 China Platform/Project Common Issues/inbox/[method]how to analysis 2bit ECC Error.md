# [method]how to analysis 2bit ECC Error

> Source: /spaces/CARSFW/pages/2451722762/method+how+to+analysis+2bit+ECC+Error
> Last modified: 2023-03-31T07:05:05.000+02:00

---

## Information

If the ECC mechanism is enabled during initialization, the action that read data from RAM address before writing this address will cause ECC Error .

For ROM(Code Flash,e.g configuration data in Ccode Flash), if an address is erased but not flashed, Accessed this address also will cause 2 bit ECC error.

2 bit ECC Error will raise System Error Exception( call SYSERR_Handler() in code)， and then reset.

Scenarios in the past:

- some shared flag in Retention Ram,  used by BM/BL/APP.  APP read the flag but the flag no initialized in BM/BL/APP.
- some shared data in Global Ram, used by HSM/APP. APP read the shared data but the data no initialized in HSM. GWM
- Local Config in Code Flash.  OTA erased Local config but no flashed data cause by some other issue. After jumping to APP, App read the data in local config.

## Analysis

1. set a break point in void Seg_SysErrHandler(void)
2. check error address from the variable seg_ErrorInfo_str.seg_Ecc_ErrorInfo.

![](../../../../_images/%5Bmethod%5Dhow%20to%20analysis%202bit%20ECC%20Error/image2022-10-8_16-36-18.png)

## Solution

Initialize the data from error address.
