# China Convergence EM  Meeting Minutes

> Source: /spaces/CARSFW/pages/2411008834/China+Convergence+EM+Meeting+Minutes
> Last modified: 2022-09-09T09:21:52.000+02:00

---

Date: 05 Sep 2022

Agenda: Decision on Error and DLT logging mechanism

Participants:

- Mohan
- Newton
- Easwar
- Senthil
- Praveen
- Carven
- Prabu
- Sudeep

Meeting Minutes:

- Mohan: ESP Workshop it is decided to use both FEL and EM since EM has the advantage of storing more data and FEL can store SoC failure information when SoC is not available

SWC → FEL → EM → INC → SOC

Advantages: Read FEL value via Diagnostics over CAN (When SOC is not available)

EM has the advantage of storing more data

The data is stored in NVM → Reason for SoC not available

- FEL in BL ? NVM is prerequisite
- ESP → No Plan for implementation as of now
- CART → What is their approach on logging error data
- For our case, We have project callout to route the data

Decision matrix: China Convergence EM and DLT Meeting Minutes - XC-CI China - Docupedia (bosch.com)

Open points and Next Steps:

1. Discuss with CART → Have FEL
2. Be Cautious FEL is Safe module, Callout has to be handled via CA or in a safe module
3. CN Specific modules - What is the big Advantage of using EM
4. Reading FEL in BL

user-1f19a , To come up with overview concept for CN Convergence Platform

Date: 09 Sep 2022

Agenda: CN Conv PF EM Architecture

Participants: Mohan, Newton, Easwar, Senthil, Praveen

Meeting Minutes:

Discussed the architecture

China Convergence Error Logging Mechanism - Draft - XC-CI China - Docupedia (bosch.com)

Try to use SafeErrorMemory module

Next Steps:

Include the SafeError Memory in the architecture - user-1f19a
