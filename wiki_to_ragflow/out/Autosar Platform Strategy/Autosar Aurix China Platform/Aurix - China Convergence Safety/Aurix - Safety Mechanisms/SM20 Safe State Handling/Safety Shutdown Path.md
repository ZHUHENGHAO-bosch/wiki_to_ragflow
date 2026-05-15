# Safety Shutdown Path

> Source: /spaces/CARSFW/pages/2923239587/Safety+Shutdown+Path
> Last modified: 2023-04-06T10:12:06.000+02:00

---

### Introduction

In Aurix Convergence projects, we have a safety shutdown path

- UC1; In case of Safety issues, SMU will make FSP0 (P33.0 - SCC_CSS_ERRn) to high which is turn will TURN OFF backlight (via External WDG)
- UC2: In case of External WDG detects Aurix is not responding, it will Reset the Aurix and also TURN OFF the backlight via RESET2 pin
- UC3: Where SM52 detects any issues based on infromation from SM19 SoC State monitor and other INC message , we will turn OFF the backlight via SCC_CSS_ERRn_3v3 and when the issue disappears, we need to switch ON the backlight again
- UC4: Sleep - we will disable WDG using SCC_CSS_ERRn (which will also TURN OFF backlight)
- UC5: Reset - During Reset case, inorder to avvoid double Reset, we will TURN OFF External WDG monitoring using SCC_CSS_ERRn
- UC6: Diagnostic - Security UCB update

So when the Safety Shutdown path is active, the external WDG will not monitor Aurix

![](../../../../../_images/Safety%20Shutdown%20Path/image-2023-4-6_14-52-51.png)
