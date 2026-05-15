# Aurix - China Convergence Platform Module Guidelines

> Source: /spaces/CARSFW/pages/2343488128/Aurix+-+China+Convergence+Platform+Module+Guidelines
> Last modified: 2023-01-18T11:04:06.000+01:00

---

### Introduction

The modules developed in China Convergence Base should be designed and implemented in a way that it an be reused across multiple projects

### Repo Structure

#### Platform repos

All the platform code has to be implemented in the respective repos which is placed in below path

Autosar\cnconvbase

Example, For Audio modules

Autosar\cnconvbase\audio

#### Project repos

All the project configuration of respective platform modules should be implemented in Config repos placed in below path

Config\Autosar\audio

### Guidelines for Platform modules

Make sure platform repo code only has the core logic and all project specific implementation has to be implemented as callouts and Configuration files in Config repos

An example for State of Health module

![](../../../_images/Aurix%20-%20China%20Convergence%20Platform%20Module%20Guidelines/image2022-7-5_15-15-27.png)

All modules should have an done following tasks

- Functional Test Spec
- Unit Test report (Google/CPPUnitTest)
- QAC/Coverity report
- Manual/Wiki for the project integration team
