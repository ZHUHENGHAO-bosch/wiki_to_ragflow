# Multicore Status -12-2022

> Source: /spaces/CARSFW/pages/2602606385/Multicore+Status+-12-2022
> Last modified: 2022-12-23T07:40:02.000+01:00

---

### Participants: Praveen, Santhosh, Priyanga, Preethica, Ravindar

### Date: 19 Dec 2022

### Meeting Minutes:

- [ZEEKR][MC]  Enable SC3 in OS – Sprint 1 – Santhosh – need to change to sprint 2
- [CNCONVPF][MC] WDG Handling – Sprint 1 - Preethica

1. MCAL configuration - all three cores COMPLETED WDGM and WDGIf configuration COMPLETED Test in all core (With Test Spec) - with and without lauterbach COMPLETED QM low priority task monitoring - Master core 0 Task priority change INPROGRESS Init task INPROGRESS Logging - Localstatuscallback - log into FEL - Reset will happen via FEL not via SMU Atleast core 0 FEL Core 1 and Core 2 → to be done once FEL is ready Create .c and .h files inside CnConvPF Autosar repo External WDG handling in Core 0 - SP2 Tested locally, problem with manifest Wiki page and test spec

- [CNCONVPF][MC] Error logging – FEL – Sprint 2-  Priyanga Started from mid of Sprint 1
- [CNCONVPF][MC]  Memory Stack Handling - Retention RAM – Sprint 1 - Priyanga

Status of Multicore INC

Completed tasks:

1. Porting INC stack( Inc_Tp SPI DMA ICU) from core0 to core2
2. Add two spinlock to protect the Ring Buffer
3. Design core0 and core1 satellite INC stack.
4. Test INC communication works fine with SOC
5. Push INC codes to zeekr repository.

To be done:

1. Allocate INC RAM from core0 to core2
2. Current design core0,1 can only process rx message successively, to process more efficiency
3. Fix bugs from test team.

### Participants: Praveen, Santhosh, Priyanga, Preethica, Ravindar

### Date: 20 Dec 2022

### Meeting Minutes:

- [ZEEKR][MC]  Enable SC3 in OS – Sprint 1 – Santhosh – need to change to sprint 2
- [CNCONVPF][MC] WDG Handling – Sprint 1 - Preethica

1. MCAL configuration - all three cores COMPLETED WDGM and WDGIf configuration COMPLETED Test in all core (With Test Spec) - with and without lauterbach COMPLETED QM low priority task monitoring - Master core 0 INPROGRESS Create a sperate task for Inita and map all Init runnable to this task Change priority for 5ms and 10ms and monitor the lowest priority task in all three cores Logging External WDG handling in Core 0 - SP2 Tested locally, problem with manifest Check with Easwar on this part State combiner for Core 0 and Core 1 - SP3 Internal WDG in Core 1 has to be disabled

- Wiki page and test spec
- [CNCONVPF][MC] Error logging – FEL – Sprint 2- Priyanga Started from mid of Sprint 1
- [CNCONVPF][MC]  Memory Stack Handling - Retention RAM – Sprint 1 - Priyanga
- [CNCONVPF][MC]  Memory Stack Handling – NVM Sprint 2 and Sprint 3 - Ravindar

### Participants: Praveen, Santhosh, Prabu

### Date: 21 Dec 2022

### Meeting Minutes:

- [ZEEKR][MC]  Enable SC3 in OS – Sprint 1 – Santhosh – need to change to sprint 2
- [CNCONVPF][MC] WDG Handling – Sprint 1 - Preethica

1. MCAL configuration - all three cores COMPLETED WDGM and WDGIf configuration COMPLETED Test in all core (With Test Spec) - with and without lauterbach COMPLETED QM low priority task monitoring - Master core 0 COMPLETED Create a sperate task for Inita and map all Init runnable to this task Change priority for 5ms and 10ms and monitor the lowest priority task in all three cores Pushed to Gerrit and testing in progress COMPLETED Logging External WDG handling in Core 0 - SP2 Tested locally, problem with manifest Check with Easwar on this part Wiki page and test spec

- [CNCONVPF][MC] Error logging – FEL – Sprint 2- Priyanga Started from mid of Sprint 1
- [CNCONVPF][MC]  Memory Stack Handling - Retention RAM – Sprint 1 - Priyanga - RetentionRAM not working currently
- Test with Reset Santhosh to share UCB - Jayaraj Praveen (BCSC/ENG1) to check this Zeekr Single Ret Ram adaptation COMPLETED RetRam handling in slave core Analyze Cerberus wiki Integrate the code Test with test spec (Need to test by writing to RetRAM from slave cores) – SP 2 - INPROGRESS Create test code in slave core -> NvRa_Write, NvRa_Read
- [CNCONVPF][MC]  Memory Stack Handling – NVM Sprint 2 and Sprint 3 - Ravindar
