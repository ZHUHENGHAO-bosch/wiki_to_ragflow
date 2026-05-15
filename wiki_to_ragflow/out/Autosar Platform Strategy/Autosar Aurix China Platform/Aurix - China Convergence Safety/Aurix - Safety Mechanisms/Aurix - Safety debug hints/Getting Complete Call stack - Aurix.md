# Getting Complete Call stack - Aurix

> Source: /spaces/CARSFW/pages/3260200303/Getting+Complete+Call+stack+-+Aurix
> Last modified: 2023-07-19T08:59:20.000+02:00

---

### Overview

Below steps explain how to get complete call stack and store into memory which can be used for issue analysis

Step 1: Get the Current PCXI and calculate the CSA address. Below link explain more on this step on how to calculate CSA address

Getting instruction address which caused NMI trap - XC-CT China - Docupedia (bosch.com)

Step 2: To get the next level call stack we need to use the link word in the CSA  area

Context lists are stored as in below picture

### 

Step 3: Get the Link word and store into a temp variable. Now calculate the next CSA address with this link word.

Now we need to check the UL bit of the link word which is stored in temp variable (from previous CSA). If the UL is 1, then RA is stored in fourth byte in current CSA. If UL is 0 then RA will be stored in second byte.

Store this RA.

Step 4: Repeat this step for the n time to get n times RA.

![](../../../../../_images/Getting%20Complete%20Call%20stack%20-%20Aurix/image-2023-7-19_14-48-16.png)

Example of ISR call stack

![](../../../../../_images/Getting%20Complete%20Call%20stack%20-%20Aurix/image-2023-7-19_14-48-56.png)

### Demo code used for above step

The code is purely implemented for Demo purpose

![](../../../../../_images/Getting%20Complete%20Call%20stack%20-%20Aurix/image-2023-7-19_14-54-29.png)

![](../../../../../_images/Getting%20Complete%20Call%20stack%20-%20Aurix/image-2023-7-19_14-55-38.png)
