# Taiji TC3xx variant Support

> Source: /spaces/CARSFW/pages/7064277144/Taiji+TC3xx+variant+Support
> Last modified: 2026-04-22T07:39:10.000+02:00

---

## Overview

This page is to summarize the component which needs to support TC3xx variants support

### Variant Matrix

| Variants | TC37x | TC38x | TC39x |
| --- | --- | --- | --- |
| Cubas | Maxus as base |  |  |
| Vector | Chery 8155/8255 as base |  |  |
| Rta-Car |  |  |  |

### Board

Use Vcuplus board... All variants shall run in Vcuplus board...

### Component Difference

| Component | Difference Description | How To Handle |
| --- | --- | --- |
| MCAL | MCAL config for each variant and should support VCUplus board for all variants |  |
| StdCore - OS | Need OS configuration to start multiple core. Take Maxus Cubas and change only OS for each variant |  |
| Startup code | Each core has its own startup code. Based on config we need to include file in build and call-in main startup |  |
|  |  |  |
|  |  |  |
