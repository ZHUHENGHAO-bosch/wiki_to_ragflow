# Aurix - Wakeup from Standby Mode

> Source: /spaces/CARSFW/pages/2377379990/Aurix+-+Wakeup+from+Standby+Mode
> Last modified: 2022-08-05T12:29:57.000+02:00

---

## Overview

As mentioned in Aurix - Standby Power domain - XC-CI China - Docupedia (bosch.com) , we will use Topology of Type 2 (Where VEXT will be turned OFF)

Below are the possible Wakeup sources that can move the Tricore to Normal Mode from Standby Mode

1. Main VEXT supply ramps-up again if configured via PMSWCR0.PWRWKEN enable bit
2. Wake-up is triggered by Standby Controller if configured via PMSWCR0.SCRWKEN enable bit
3. Wake-up via Wake-up Timer if configured via PMSWCR0.WUTWKEN enable bit
4. Wake-up via Pin B (Pin 33.12) if configured via PMSWCR0.PINBWKEN enable bit

We need to enable Aurix Wakeup by SCR and during Power on Reset So, below bit has to be set before entering to SCR standby mode

- Enable PMSWCR0.PWRWKEN → Tricore wakeup on Power on Reset
- Enable PMSWCR0.SCRWKEN → Tricore wakeup by SCR
