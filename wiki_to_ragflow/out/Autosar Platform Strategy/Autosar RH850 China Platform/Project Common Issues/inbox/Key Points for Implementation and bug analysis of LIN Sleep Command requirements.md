# Key Points for Implementation and bug analysis of LIN Sleep Command requirements

> Source: /spaces/CARSFW/pages/2960167379/Key+Points+for+Implementation+and+bug+analysis+of+LIN+Sleep+Command+requirements
> Last modified: 2023-04-19T08:46:43.000+02:00

---

The Geely ECARX DHU project requires sending a Sleep Command to the LIN bus before the MCU enters sleep.

The implementation strategy of the Geely project is in the "Lin_GoToSleep" function in file "Lin.c", define a local variable type "Lin_PduType", and sent to LIN bus through "Lin_Fp_StartTxFrame" function. At the same time, it is important to note that in the AutoSAR ComM module, the "Nm Variant" of this LIN in "ComMChannels" should be configured as "LIGHT".

![](../../../../_images/Key%20Points%20for%20Implementation%20and%20bug%20analysis%20of%20LIN%20Sleep%20Command%20requirements/image-2023-4-19_14-40-38.png)

![](../../../../_images/Key%20Points%20for%20Implementation%20and%20bug%20analysis%20of%20LIN%20Sleep%20Command%20requirements/image-2023-4-19_14-41-11.png)

After implementing the change in power down requirements by LCM, it was found that the previously sent LIN Sleep Command was not sent to the LIN bus.

Debugging code found that the following functions for implementing Lin_Trcv power-off are called in "PowerM_VIPPeripheralPowerDownCallback" function, which is executing before the "Lin_GoToSleep" function called, so when LinTrcv  is turned off, LIN Sleep Command cannot be sent to the bus.

IoHwAb_DioWrite_LINx_TR_EN(STD_LOW); IoHwAb_DioWrite_LIN2_TR_EN(STD_LOW);

![](../../../../_images/Key%20Points%20for%20Implementation%20and%20bug%20analysis%20of%20LIN%20Sleep%20Command%20requirements/image-2023-4-19_14-42-15.png)

Adjust the call position of the LinTrcv power-off functions above, call them in "PowerM_VipPeripheralPowerDown_LastAction" function, which is executed after the "Lin_GoToSleep" function.  Thus, LIN Sleep commands can be sent to the LIN bus before MCU sleep as requirements .

The Zeekr project adopts the same bus topology architecture and BaseTech test cases as the Geely ECARX DHU project, so it is also necessary to pay attention to the issue of sending LIN Sleep commands.

Reference submission https://rbcm-gerrit.de.bosch.com/c/projects/gwm/v35/autosar/autosar/bosch/+/598239
