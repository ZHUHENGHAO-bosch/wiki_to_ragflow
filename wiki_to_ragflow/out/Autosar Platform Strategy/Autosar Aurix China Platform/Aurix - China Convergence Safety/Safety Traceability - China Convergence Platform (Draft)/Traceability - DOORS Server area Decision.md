# Traceability - DOORS Server area Decision

> Source: /spaces/CARSFW/pages/2491260636/Traceability+-+DOORS+Server+area+Decision
> Last modified: 2022-11-08T09:05:22.000+01:00

---

We have three different DOORS area, and we need to decide which one will be suitable for China Convergence Platform and Projects

- Rng Server → CART
- HI Server → China Projects
- DOORS Nextgen

### Solution 1:  CART in Rng and CN PF/Projects in HI server

Since the CART and China Project DOORS are in different Servers there is a need for DOORS exchange

For this we need poweruser tool

Synchronization is done by the Requirements Manager from both sides (CART and BaseSW in our case), exchange frequency will be aligned based on the project needs. Each re-import will be also checked by eXchange for changes which have to be communicated to the teams

![](../../../../_images/Traceability%20-%20DOORS%20Server%20area%20Decision/image2022-11-7_14-6-29.png)

Pros:

- No need to change the China project server

Cons:

- Need High Effort
- High complexity

### Solution 2: Both CART and China project DOORS in RNg Server

Linking can be directly done (No Need for DOORS exchange)

Below diagram is from CART RM page - RM Collaboration - CT/ESC Software Home - Docupedia (bosch.com)

![](../../../../_images/Traceability%20-%20DOORS%20Server%20area%20Decision/image2022-11-7_14-10-38.png)

Pros:

- Less complex
- Less effort

Cons:

- Need to have separate DOORS for SCC and SOC (Since SOC will be in HI Doors)
- System and Customer requirements will be available in HI DOORS

Project team cannot accept

> **INFO**
> CART is having a plan to move to Next gen. At that time both CART and CNCONVPF can move to DOORS next gen

### Solution 3: CART in Rng and China Convergence in DOORs nextgen

To be discussed
