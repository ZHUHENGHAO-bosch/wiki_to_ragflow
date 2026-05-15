# China Convergence - Preventive Measures

> Source: /spaces/CARSFW/pages/2400074139/China+Convergence+-+Preventive+Measures
> Last modified: 2022-09-06T06:02:19.000+02:00

---

## Overview

This page is to list down all the problems faced in previous projects and to have an mechanism to detect and solve these problems in early face of the up coming projects

## Issues

### 1. Performance issue

#### QM WDG Supervision Entity

Usually Watchdog will be enabled when the safety development started, but before that most of the QM modules will be implemented.

Since Watchdog is not active, there is no mechanism to detect OS Jitters

At later time detecting a module which takes a high CPU load is very tough and needs lot of rework.

Solution: Enable Watchdog at the early phase of the project and configure an QM Supervision entity which can detect the OS Jitters

#### RTMO

RTMO gives the complete load information of the task

It has to be mandated that every delivery has to attach the RTMO report to the ticket (With and Without the change). Reviewers must check the RTMO report before the approval

#### Logging Overall load

Overall load taken by the system can be logged every 1 or 2 mins

### 2. Logging

DLT logs helped a lot in the previous project to identify the root cause.

So it is important to add DLT log wherever it is necessary when we are implementing/integrating an module.

Developers have to implement the logging mechanism where they feel the log will help. Reviewers have to ensure that the logging is done properly in their review

Reviewers and developers need to make sure the logging mechanism in the module is not spamming the logs with cyclic information

### 3. Boot time measurement

We need to have a boot time measurement framework, which can print time taken at each level/state in DLT

Since the Safety tests are the one taking so much time, it has to be make sure that before delivering the safety tests, the time taken has to be calculated and to be checked whether it meets the project start up time requirements

### 4. FEL or Error Memory

Each module has to report an fatal (only very critical) error to FEL or Error Memory

Developers has to keep FEL/EM in their design. Reviewer has to ensure the FEL/EM is used at proper place during the review

### 5. RAMROM Summary

Any major delivery has to be reviewed with RAMROM summary. In case of a major change, it has to be justified

Reviewers has to ensure RAMROM summary data as part of the review process (At least for any major module delivery)
