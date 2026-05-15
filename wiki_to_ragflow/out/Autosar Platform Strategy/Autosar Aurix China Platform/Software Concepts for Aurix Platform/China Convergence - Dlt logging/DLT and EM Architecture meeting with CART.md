# DLT and EM Architecture meeting with CART

> Source: /spaces/CARSFW/pages/2423638171/DLT+and+EM+Architecture+meeting+with+CART
> Last modified: 2022-09-16T08:13:58.000+02:00

---

### Date: 16 Sep 2022

### Agenda: To sync Dlt mechanism and Error logging with CART modules

### Participants:

From CART:

- Kavitha,
- Karthik V

From CNConvPF

- Praveen
- Senthil

### Meeting Minutes:

1. Discussed on DLT architecture China Convergence - Dlt logging - XC-CI China - Docupedia (bosch.com)
2. Discussed on EM architecture China Convergence Error Logging Mechanism - Draft - XC-CI China - Docupedia (bosch.com)

### Open Points and Next actions:

1. Identify the CART (Including Cerberus and Hydra) modules which are not doing dlt logging via Wrapper in Config repo Responsible: user-81080
2. Safety modules DLT logging has to be make sure that they are logging via an wrapper in Config repo. Responsible: Karthik Vangili (MS/ENE-VD-EP1-XC)
3. ECT has to add this Super OPL and has to take care of tracking it further Prabu Dhandapani (MS/ENE-VD1-XC)
4. All CART modules shall use FEL (Not the EM) user-81080 Karthik Vangili (MS/ENE-VD-EP1-XC)
