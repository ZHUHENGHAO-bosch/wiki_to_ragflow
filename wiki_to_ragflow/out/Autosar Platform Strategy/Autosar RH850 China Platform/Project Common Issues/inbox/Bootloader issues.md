# Bootloader issues

> Source: /spaces/CARSFW/pages/2480260170/Bootloader+issues
> Last modified: 2023-03-31T07:42:38.000+02:00

---

Issue 1 - Trigger reset during app flash erasing

Analysis

1. Reset during the app flash erasing process, and the following breakpoints are triggered

void __UnhandledException(void) { /* try to recover the system by a reset */ Startup_TriggerMcuHwReset(); }

2. Check callstack and exception triggered in EthIf_MainFunctionTx function 3. Check the .map file, EthIf_MainFunctionTx in .text section 4. During the flash erasing or writing process, the rom cannot be accessed, the code in the rom cannot be executed, otherwise the reset will be triggered

Solution

In EthIf_ MemMap.h file, redefine the complication section of ETHIF_START_SEC_CODE/ETHIF_STOP_SEC_CODE, and then recompile,  EthIf_MainFunctionTx function is mapped to .ramremap section.

Issue 2 - Bootloader may fail to run, when Ethernet code is mapped to the RAM section

Analysis

1. Check the memmap file and place the SOAD_START_SEC_CODE in .REMAPCODE_1 section 2. REMAPCODE_1 mapped in the localRAM section 3. lowinit initialed localRAM_iFlashDrv ~ localRAM_iCodeRam sections, but localRAM for SOAD code is not initalized. 4. RAM section needs to be initialized.

Solution

Modify ___ghs_cm_localram_start, initialize localRAM in lowinit ___ghs_cm_localram_start    = MEMADDR(localRAM); ___ghs_cm_localram_end      = MEMENADDR(localRAM_iCodeRam) - address_offset;

Issue 3 - During flash erase, IpV4_Arp_VSendMessage function is called, and reset is triggered

Analysis

1. Check IpV4_Arp_VSendMessage function maps the address in the RAM section, there is no problem 2. The code of Arp packet message header is as follows

/* #20 Build the ARP packet. */ TCPIP_PUT_UINT16(ethIfBufferPtr, IPV4_ARP_HW_ADDR_TYPE_OFS, IPV4_ARP_HW_ADDR_TYPE_ETHERNET); TCPIP_PUT_UINT16(ethIfBufferPtr, IPV4_ARP_PR_ADDR_TYPE_OFS, IPV4_ARP_PORT_ADDR_TYPE_IPV4); TCPIP_PUT_UINT8(ethIfBufferPtr, IPV4_ARP_HW_ADDR_SIZE_OFS, IPV4_ARP_HW_ADDR_SIZE_ETHERNET); TCPIP_PUT_UINT8(ethIfBufferPtr, IPV4_ARP_PR_ADDR_SIZE_OFS, IPV4_ARP_PORT_ADDR_SIZE_IPV4); TCPIP_PUT_UINT16(ethIfBufferPtr, IPV4_ARP_OP_OFS, Operation);

3. Check the function assembly. The Arp message header packet code is optimized to mem_cpy by the compiler

0xfebf2592 IpV4_Arp_VSendMessag+0x68:  ff801186    jarl    _ghscallpatch__13064_.text__memcpy (0xfebf3718), lp

4. In the function IpV4_Arp_VSendMessage, the code that packet the Arp message header is assembled into the mem_cpy mapped in .text section, which causes the function call to trigger reset during the flash erase or write process.  To modify the Arp message header packet order to avoid the compiler's automatic optimization.

Solution

Modify the packet order of Arp message header as follows to avoid automatic optimization by the compiler

/* #20 Build the ARP packet. */ TCPIP_PUT_UINT16(ethIfBufferPtr, IPV4_ARP_HW_ADDR_TYPE_OFS, IPV4_ARP_HW_ADDR_TYPE_ETHERNET); TCPIP_PUT_UINT8(ethIfBufferPtr, IPV4_ARP_HW_ADDR_SIZE_OFS, IPV4_ARP_HW_ADDR_SIZE_ETHERNET); TCPIP_PUT_UINT16(ethIfBufferPtr, IPV4_ARP_OP_OFS, Operation); TCPIP_PUT_UINT16(ethIfBufferPtr, IPV4_ARP_PR_ADDR_TYPE_OFS, IPV4_ARP_PORT_ADDR_TYPE_IPV4); TCPIP_PUT_UINT8(ethIfBufferPtr, IPV4_ARP_PR_ADDR_SIZE_OFS, IPV4_ARP_PORT_ADDR_SIZE_IPV4);

After modification, the assembly code no longer calls memcpy.

Issue 4 - After modifying the flash driver RAM address, the flash erasing fails.

Analysis

1. Modify localRAM_iFlashDrv address as 0xFEBCF000

From: localRAM_iFlashDrv  : ORIGIN = 0xFEBD0000, LENGTH = 0x003000

To: localRAM_iFlashDrv  : ORIGIN = 0xFEBCF000, LENGTH = 0x003000

2. In flashrom.c/flashrom.h, the compilation script is different from the new address, modify the link file as follows

From: FlsDrvArea : ORIGIN = 0xFEBD0000, LENGTH = 0x00004000 /* 16 KiB */

To: FlsDrvArea : ORIGIN = 0xFEBCF000, LENGTH = 0x00004000 /* 16 KiB */

3. In the path \autosar\VIP_ Bootloader\vector_fbl\vector_Bsw\BSW\Flash\Build, and run the following compilation command to generate a new flashrom.c/flashrom.h. Also replace the flashrom.c/flashrom.h in the blu code. - j.bat - _MkFlashRom.bat FlashDrv.hex

Solution

After modifying the ram address in the flash driver, it is also need to modify the address in flash_rom link file.

Issue 5 - In the Bootloader, triggering the det error when CAN busoff, entering the endlessloop.

Analysis

1. In the Bootloader, when CAN busoff, Det_ReportError is triggered enter Det_EndlessLoop, as Bootloader does not enable the watchdog, the Bootloader is stuck.

Solution

Disable the DET of CAN in the Bootloader

Issue 6 - OTA update LCFG, and fails to start after reset

Analysis

1. Read all SCC code flash data out, and find that data on LCFG addresses are all 0xFF

2. Check the QNX log, it is found that the last powerup cycle is cycle697, and cycle698 is in normal. It is speculated that after the SOC sends the request to erase the LCFG, it reset the SCC to APP and without sending the new LCFG data

3. After LCFG is erased, no new LCFG data is writtern. Triggering an ecc error that causes the APP reset, when LCFG data is read, after reset from Bootloader to APP

Solution

To avoid continuous reset due to ecc error in the APP, the BM reset to Bootloader when APP reset for 25 times.

Issue 7 - If a RAM section does not specify a section in LD file, the RAM section will be randomly mapped into the ROM section bye complier, and causing reset.

Analysis

1. Warning prompt in compilation windows as follows:

[elxr] (warning #283) section .data_GENERAL_PURPOSE_RAM from libService.inc_tp.a(inc_tp.c.obj) isn't included by the section map; [exlr] (warning #283) section .noburam from libAutolink.a(Tacho.c.o) isn't included by the section map;

2. Check the .map file. The 2 ram section .noburam and .data_GENERAL_PURPOSE_RAM do not specify a section in the ld file. As a result, the compiler compiles the 2 ram section into the rom. The app access these ram sections to trigger reset

3. The ram sections need to be explicitly declare to a ram section to avoid random allocation by the compiler

Solution

Assign these 2 ram section to RamGlobalB section to solve the problem of random allocation by the compiler
