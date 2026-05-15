# 3.0 Timp 1.0 - Epics

> Source: /spaces/CARSFW/pages/6245224039/3.0+Timp+1.0+-+Epics
> Last modified: 2025-10-15T03:09:33.000+02:00

---

## Overview

This Page is to analyze how to merge Fusion Demo to Taiji Main branch without affecting existing projects

### Current Matrix

| Tricore Version | TC377 | TC38x | TC39x |
| --- | --- | --- | --- |
| Vector | Taiji Chery 8155 Chery 8255 | CCU | VCU Plus |
| Cubas | Taiji Maxus | - | GHAC Fusion WIN2 |
| RTA-CAR | - | - | - |

### Taiji platform board

| Variant | Board |
| --- | --- |
| TC37x | Maxus/GHAC/Chery8255?? |
| TC38x | CCU |
| TC39x | VCU Plus |

### First step in TIMP

Make TIMP as complete platform for Tricore supporting - TC37x, TC38x and TC39x. And more to TC4x

| Top level Epics | Detailed features | Comments |
| --- | --- | --- |
| Repo restructure in Taiji Main | Remove dependency with GB Create meaningful repos in PF Concept for Config repo handling | Make sure it doesn't affect running project |
| Taiji Fusion to Taiji Main - Autosar - AR TC39x | CMAKE Macro for TC39x MCAL integration for TC39x RTA-OS for TC397 with HW counter Option to add Flux, Scons and rbnetcom based on build Macro Cross Cutting concerns - RAMROM, LD, RTMO, MEMMAP Adapt the configuration to latest Cubas Enable RTE | Use Fusion board to Test |
| Taiji Fusion to Taiji Main - Autosar - AR TC39x - Phase 2 | XCP -Optimization Multicore LCM Mode management Multicore COM - If needed Logging LCM concept and Clean up and implementation considering ADAS product use cases - System Manager |  |
| Taiji Build platform | Create a build platform suitable to support multiple compiler and controller in TIMP - Concept Create a build platform suitable to support multiple compiler and controller in TIMP - for Tricore GHS ....................... | ...... |
