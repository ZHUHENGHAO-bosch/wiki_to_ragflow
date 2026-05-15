# Sleep Current with SCR

> Source: /spaces/CARSFW/pages/2832081688/Sleep+Current+with+SCR
> Last modified: 2023-11-10T03:21:18.000+01:00

---

![](../../../../_images/Sleep%20Current%20with%20SCR/image-2023-6-28_10-22-27.png)

Zeekr project

| Board variant | Sleep type | Sleep current | Comment |
| --- | --- | --- | --- |
| A0 | SCR | 210uA |  |
| A2 | SCR | 1.02mA (2023.03.13) | With U33S_SCC_ON high |
| A3 | SCR | 1.2mA | STR power mode, could be optimized later |
| B1 | SCR | 370uA | SCR sleep mode |
| STR | 12mA | STR mode |

Chery project

| Board variant | Sleep type | Sleep current | Comment |
| --- | --- | --- | --- |
| A0 | SCR | 160uA |  |
| B1 | SCR | 150uA | SCR sleep mode, turn off U33S_SCC |
| STR | 55mA | STR mode, do not turn off U33S_SCC |
| STR | 4.8mA | STR mode, after HW changing and turn off U33S_SCC |
