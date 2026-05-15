# SAIL folder structure - Obsolete

> Source: /spaces/CARSFW/pages/4961271371/SAIL+folder+structure+-+Obsolete
> Last modified: 2024-11-07T08:55:12.000+01:00

---

## Overview

This page is to create the folder structure for SAIL in 8755/8255

Most probably ADAS applications will run in SAIL. so the folder structure shall be based on ADAS application

Need to Wait for the confirmation who will develop the Application in SAIL domain → PATAC or Bosch

## Considerations

- The folder structure shall be in a way it shall support all project use cases

## Module Level Folder structure：

Module

├── arch/                            # Module arch folder Contains files such as ,Flux or Arxml files ├── doc/                             # Documentation Folder: Includes design documents, user manuals, etc.

│   ├── module.rst              # module documentation

├── inc/                              # Header Files

├── cfg/                              # Module Configuration Files: Variations according to project or functionality ├── src/                              # Source Code Folder ├── test/                             # Module Test Code

│   ├── unittest                  #unit test

│   ├── int_test                   #integration test, if any ├── CMakeLists.txt              #CMake file

## Top Level Folder structure

Root_Folder/

├── asw                            # Includes files such as DaCore, FCT, and integration tests, isolated from Hw+ files.

├── 3party                        #  thirdParty - Customer modules and Third Party libraries

├── stdcore                      # Purchased AUTOSAR tool delivery packages or internal tool platform packages. Such as Cubas/Vector

│   ├── cubas                        #   cubas deliver package

│   ├── rtaos                         # etas Os

│   ├── mom/rte                 # RTE │   └── mcal                    # MCAL

├── config                      # Configuration projects and generated code for EB, CUBAS, DADY, and other configuration tools.

│   ├── cubas_cfg               #   cubas cfg project and generate codes

│   ├── rtaos_cfg                # etas Os cfg project and generate codes

│   ├── scom/rte_cfg          # rte generate codes │   └── eb_mcal_cfg           # mcal generate codes

├── cust_apl              #  project codes

├── diag                          #  Diagnostic codes

├── hsm                          #  Security codes

├── platform                   #  Cp platform modules

│   ├──  rbBSW                   #  Abstract Layer Modules such as EINC, Globaltime, rbPdm, etc.

│   │   ├──  function            #  function modules such as EINC

│   │   ├──  service              #  service modules such as rbSyslog

│   ├──  rbHSW                 #  Hardware-related modules such as peripheral drivers, memory protection, bus protection, etc.

├── mt                            #  Measurement and test, fault injection and XCP code and projects.

├── tools # Files related to Build and debug setup, GoogleTest, QAC

│   ├── btc_tools                # btc_tools, come from ip_if platform repo

│   ├── GT                          # google test

│   ├── QAC/Coverity        #  QAC/Coverity

├── fbl                            #  bootloader project
