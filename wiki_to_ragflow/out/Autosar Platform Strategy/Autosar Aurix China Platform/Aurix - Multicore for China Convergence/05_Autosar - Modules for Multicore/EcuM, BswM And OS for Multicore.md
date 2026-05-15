# EcuM, BswM And OS for Multicore

> Source: /spaces/CARSFW/pages/2394053313/EcuM+BswM+And+OS+for+Multicore
> Last modified: 2022-08-18T17:46:07.000+02:00

---

## BswM

- On systems with distributed BSW there is one BSW Mode Manager (BswM) per partition
- Each of these BswMs can be configured independently
- A BswM mainly interacts with the state managers (ECU state manager and bus state managers, for instance) on the same partition
- The BswM is also responsible for the initialization and shutdown of BSW modules running in the same partition

## EcuM and OS

- There should be one OS and EcuM per Core
- Distributing the BSW is only possible when using the EcuM Flex; the EcuM Fixed does not support this
- The EcuM in the master core starts some drivers, determines the Post Build configuration and starts all remaining cores with all their satellite EcuMs

> **INFO**
> Distributing the BSW is only possible when using the EcuM Flex; the EcuM Fixed does not support this
