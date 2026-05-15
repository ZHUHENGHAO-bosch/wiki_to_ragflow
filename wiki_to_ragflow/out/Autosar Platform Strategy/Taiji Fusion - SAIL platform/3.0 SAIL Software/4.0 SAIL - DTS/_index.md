# 4.0 SAIL - DTS

> Source: /spaces/CARSFW/pages/4925610374/4.0+SAIL+-+DTS
> Last modified: 2024-10-31T08:53:59.000+01:00

---

## Overview

A Device Tree Source (DTS) is a text file used in Linux to describe hardware information, aiming to reduce coupling between the kernel and platform-specific code.

A DTS file contains static hardware configurations and does not support dynamic changes. It is compiled into a Device Tree Blob (DTB), a binary file that the kernel parses at boot to understand the hardware layout. The device tree addresses the complexity of maintaining ARM architecture code by achieving vendor modification independence and enabling a common binary target.

linux use DTS for three major purposes:

1 platform identification

2 runtime configuration

3 device population

![](../../../../_images/4.0%20SAIL%20-%20DTS/dts.png)

## QC SAIL DTS

QC hypervisor is black box to us.

Although we can modify dts ( as discription in 80-42846-147_REV_AA_SAIL_EL2_Reference), f or some uncertain DTS configurations, we still need to raise cases and consult Qualcomm.

The path of sailhyp's dts is sail_autosar\sail_proc\BSP\scripts\lemansau-sailhyp-autosar.dts.

In this sailhyp dts, can configure:

- EL2 boot configuration, e.g. SMP enable; el2 wdt enable
- MPU configuration
- QUP(Qualcomm Universal Peripheral (UART/I2C/SPI)
- others

EL2 boot configuration, e.g. SMP enable; el2 wdt enable

```
	/*EL2 boot configuration*/
	EL2_boot_configuration{
		initSMP_enable = <0x1>; // enable init SMP
 		wdt_enable = <0x0>; // enable el2 wdt
		secondarycore_wfi_enable = <0x1>; // For Autosar - Put secondary cores in WFI
		warminit_loadelf_enable = <0x0>; // Disable EL1 image load for Autosar
		icb_el2_init_core = <0x0>; // Icb init core
	};
```

MPU configuration. e.g. memory section, permission

```
el1_mem_map {
		sailsw1_mem_map {			
			Node_1 {
				start-addr = <0x080D3800>;
				size = <0x202C00>;
				non-executable = <0>; // disable // enable
				access-permission = <1>; // read/write EL2 // read/write any // read only EL2 // read only
				shareable = <2>; // 0 non shareable // 2 outer shareable // 3 inner shareable
				attribute = <3>; // nGnRnE // nGnRE // GRE // normal // normal non cache
			};
			Node_2 {
				start-addr = <0x2000000>;
				size = <0x10000>;
				non-executable = <0>; // disable
				access-permission = <1>; // read/write any
				shareable = <0>; // 0 non shareable
				attribute = <3>; // normal
			};
			Node_3 {
				start-addr = <0x2100000>;
				size = <0x8000>;
				non-executable = <0>; // disable
				access-permission = <1>; // read/write any
				shareable = <0>; // 0 non shareable
				attribute = <3>; // normal
			};
			Node_4 {
				start-addr = <0x2200000>;
				size = <0x8000>;
				non-executable = <0>; // disable
				access-permission = <1>; // read/write any
				shareable = <0>; // 0 non shareable
				attribute = <3>; // normal
			};
		};
```

QUP((UART/I2C/SPI)

```
	qup {
		common-addr = <0xf1900000>;

		/*I2C*/
		se0_i2c: qupv3_se0_i2c {
			reg-base = <0xF1900000>;
			slave-addr = <0x28 0x29 0x12 0x11 0x13 0x15 0x17>;
			clock-name = "sailss_cc_qupv3_wrap0_s0_clk";
			clock-frequency = <19200000>;
			interrupt = <402>;
			pinctrl = &se0_i2c_pinctrl;
			i2c-mode = <2>;
 			addressing-mode = <1 1 1 2 2 2 2>;
 			timestamp = <0 0 0 0 0 0 0>;
			precmd-delay = <0 0 0 0 0 0 0>;
			access-mode = <0>;
			status = <1>;
		};

        ...

		/*UART*/
		se0_uart: qupv3_se0_uart {
			reg-base = <0xF1900000>;
			clock-name = "sailss_cc_qupv3_wrap0_s0_clk";
			clock-frequency = <100000000>;
			baudrate = <115200>;
			interrupt = <402>;
			pinctrl = &se0_uart_pinctrl;
			parity = <4>;
			stop-bit = <0>;
			access-mode= <2>;
			loopback  = <0>;
			status = <1>;
		};

		...

		/*SPI*/	
		se0_spi: qupv3_se0_spi {
			reg-base = <0xF1900000>;
			clock-name = "sailss_cc_qupv3_wrap0_s0_clk";
			clock-frequency = <100000000>;
			interrupt = <402>;
			pinctrl = &se0_spi_pinctrl;
			slave = <1>;
			no-of-channels = <1>;
			loopback  = <0>;
			access-mode= <2>;
			status = <1>;
		};

	...
```

Others

```
   imageLoadToDDR {
        wait-for-DDR = <0>;
    };

	/*BIST execution core config*/
	BistExecutionCore {
		SAIL_CORE0 = <1>;
	};

	/* Set desired EL2 UART log level,supported log levels are below  
		LOG_NONE        = 0,
		LOG_ERROR       = 1,
		LOG_WARNING     = 2,
		LOG_INFO        = 3,
		LOG_DEBUG       = 4,
		LOG_NOUART      = 5
	Default log level is LOG_WARNING */
	
	setUARTloglevel {
		newUARTloglevel = <2>;
	};
```
