# Threshold/Parameter Config Checklist

> Source: /spaces/CARSFW/pages/6856956715/Threshold+Parameter+Config+Checklist
> Last modified: 2026-03-04T11:29:43.000+01:00

---

| Category | Sub- Category | Description | Owner（Draft） | SGM 8X97 | SGM CCU | SGM VCU Plus | SGM VCU Pro | GEELY3.0 | Chery 8255 | Chery 8155 | Zeekr CX1 | GWM |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PinMux | PinMux | PIN的配置信息，包括下面的信息 Pin Function ：选择引脚功能（GPIO、UART、SPI、I2C 等） Drive Strength ：设置输出电流能力 Pull Config ：选择上拉、下拉或无 Output Type ：推挽或开漏 Direction ：输入或输出 包括正常运行时的Port状态，Sleep/STR前要切换的Port状态 | EPE |  |  |  |  |  |  |  |  |  |
| IoHwAb | IoHwAb接口根据PinMux信息更新 | ESW |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |
| Voltage - QM | PowerM | Configuration for Over, Critical Over, Under, Critical Under voltages Threshold time to stay in critical levels | ESR |  |  |  |  |  |  |  |  |  |
| Thermal | Temperature Sense | NTC温度阻值对照曲线： THERMALMONITOR_DEVICE_ID_TEMP_SIP_SOC THERMALMONITOR_DEVICE_ID_TEMP_EFUSE_DIODE THERMALMONITOR_DEVICE_ID_TEMP_PWR_MAIN THERMALMONITOR_DEVICE_ID_TEMP_NAND_DEV THERMALMONITOR_DEVICE_ID_TEMP_HEATSINK THERMALMONITOR_DEVICE_ID_TEMP_PHTM_MPQ THERMALMONITOR_DEVICE_ID_TEMP_DB_CAM THERMALMONITOR_DEVICE_ID_TEMP_BTLAN THERMALMONITOR_DEVICE_ID_TEMP_RESERVED 以上只是部分功能， 具体需要按照项目要求 | EHW |  |  |  |  |  |  |  |  |  |
| NTC温度曲线的阈值信息LOW/CRITICAL_LOW/HIGH/CRITICAL__HIGH/EMERGENCY_HIGH | ESR |  |  |  |  |  |  |  |  |  |
| FAN Control | PWM频率，最大风速占空比，最小风速占空比，停止占空比 | EHW |  |  |  |  |  |  |  |  |  |
| Power | Power Sequence | Power Up/Down sequence （主要关注电源先后级以及时间间隔，是否有PGood需要判断 MCU Power Sequence (UxxS_PERI, U50S_CAN, UxxS_PHTM...) SoC Power Sequence (U33R_CPU, UxxS_CPU_PERI, U50S_USB, Display...) | EHW |  |  |  |  |  |  |  |  |  |
| STR/Sleep sequence 电源前后级关机顺序依赖，哪些GPIO是否需要保留 |  |  |  |  |  |  |  |  |  |  |
| Reset SoC Reset INC消息通知 拉RESET_REQ中断通知 拉KPD/FastPoff PSHOLD/POFFCOMPLETE的检查 MCU Reset Only 需要切成Input保留电的Pin MCU自己需要重新使能的电 Graceful Reset 关机到开机之间，电容是否能释放干净，关掉到开启之间的最小时间间隔确认 |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |
| MPQ4232电源芯片 | MFR_CTRL1寄存器，Rsens[0,0]位的配置信息； Select external current sense resistor value 0: 5mohm 1: 10mohm | EHW |  |  |  |  |  |  |  |  |  |
| MPQ2022电源芯片 | 寄存器值与工作电流转换公式； 外设短路、开路状态的电流阈值； | EHW |  |  |  |  |  |  |  |  |  |
| MPQ5864电源芯片 | Channel Current Limit Setup (0x02)的电流限制要求 00: Current limit = 1.2A 01: Current limit = 0.9A 10: Current limit = 0.6A 11: Current limit = 0.3A | EHW |  |  |  |  |  |  |  |  |  |
| 诊断硬件短路开路电流阈值： 寄存器值与工作电流转换公式； 外设短路、开路状态的电流阈值； | EHW |  |  |  |  |  |  |  |  |  |
| MPQ8875电源芯片 | 需要提供关于寄存器Register 00h  reference voltage配置信息 Sets the reference voltage, calculated with the following equation: In normal input mode: 00h to 31h: Reserved 32h to C8h: VREF = REF[7:0] x 10mV (resolution: 10mV) C9h to FFh: Reserved In low input mode: 00h to 31h: Reserved 32h to 78h: VREF = REF[6:0] x 10mV (resolution: 10mV) 79h to FFh: Reserved In low input mode REF7 bit is invalid. | EHW |  |  |  |  |  |  |  |  |  |
| MAX20087电源芯片 | 寄存器值(ADCx)与工作电流转换公式； 外设短路、开路状态的电流阈值； | EHW |  |  |  |  |  |  |  |  |  |
| TPS55289电源芯片 | BuckBooster，输出13V/12.5V |  |  |  |  |  |  |  |  |  |  |
| ADC 检测 | 各个电源的ADC采集，分压比，计算公式 |  |  |  |  |  |  |  |  |  |  |
| UBAT Sense | 需要提供关于UBAT电压电阻计算公式，以及低压、欠压、正常、过压、高压的阈值信息，滞回区间 | ESR |  |  |  |  |  |  |  |  |  |
|  | Sleep Mode | 瑞萨： 睡眠之前的中断ICU捕获激活配置 SleepCurrent优化配置 唤醒之后get当前的唤醒原因 英飞凌 SCR的GPIO配置 SCR中中断配置，唤醒源适配 进SCR前的准备，关闭所有中断，是否优化了静态电流 |  |  |  |  |  |  |  |  |  |  |
|  | SystemM & PowerM | To be updated for Power Supplies |  |  |  |  |  |  |  |  |  |  |
| Others | INC配置 | SPI主从, 一路两路 |  |  |  |  |  |  |  |  |  |  |
| Fuel tank sensor | 燃油传感器电阻的电压阻值转换公式，并提供浮子电阻与main、main_calibration之间的计算关系 | EHW |  |  |  |  |  |  |  |  |  |
| 油箱浮子传感器开路短路阈值 | ESR |  |  |  |  |  |  |  |  |  |
| FuSa | WDG Timeout | Timeout to be configured for Internal Watchdog ![warning](https://inside-docupedia.bosch.com/confluence/plugins/servlet/twitterEmojiRedirector?id=26a0) The value should be less that External WDG OTP timeout value | ESS (TSR) & EHW (HSI) |  |  |  |  |  |  |  |  |  |
|  | Safe voltage | Off, Min and Max threshold in ADC counts | ESS (TSR) & EHW (HSI) |  |  |  |  |  |  |  |  |  |
|  | Debounce time for each voltage channel | ESS (TSR) & EHW (HSI) |  |  |  |  |  |  |  |  |  |
|  | Internal Voltage | Over and under voltage threshold for VDD, V DDPD, VDDP3, VEXT, VDDM, VEVRSB | ESS (TSR) & EHW (HSI) |  |  |  |  |  |  |  |  |  |
|  | Safe ADC compensation | Not applicable for Aurix Taiji platform. For Renesas platform, Safe ADC compensation calculation values | ESS (TSR) & EHW (HSI) |  |  |  |  |  |  |  |  |  |
|  | Safe Temperature monitor | Not applicable for Aurix Taiji platform. For Renesas platform, the threshold and ADC values have to be in HSI | ESS (TSR) & EHW (HSI) |  |  |  |  |  |  |  |  |  |
|  | Peripheral and Register Protection | The classification of peripherals as ASIL and QM Based on this SW team to configure RegM and MPU | ESS (TSR) & EHW (HSI) |  |  |  |  |  |  |  |  |  |
