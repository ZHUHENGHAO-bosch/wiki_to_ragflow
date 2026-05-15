# Taiji - Aurix Safety guidelines

> Source: /spaces/CARSFW/pages/4415558435/Taiji+-+Aurix+Safety+guidelines
> Last modified: 2024-06-25T14:23:17.000+02:00

---

## Overview

This page summarizes the guidelines for use of Safety in Projects that is based on Taiji platform

## Guidelines

- Keep all Safety module in Core 0. Even though we have two cores with lock step, to make the architecture simple we shall keep all safety components in Core 0

This is just a guideline, but if project has performance issue and really need Core 1. still Taiji supports this use case.

![](../../../_images/Taiji%20-%20Aurix%20Safety%20guidelines/Taiji_Guideline_Architecture.bmp)

- All safety components variables must be located in Core 0 memory. Since only core 0 memory is protected with BUS MPU

If we need to use Core 1 memory, then BUS MPU and its FIT test cases has to be implemented

- Always use context switcher module for trusted functions to access ASIL API from QM context. Do not configure direct trusted API in configurator -> Context Switcher - Introduction and How To Configure - XC-CT China - Docupedia (bosch.com)
- Service External WDG from Core 0 and internal WDG for all cores
