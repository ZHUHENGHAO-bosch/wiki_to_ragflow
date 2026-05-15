# Taiji - VCU Repo download and Build commands

> Source: /spaces/CARSFW/pages/7108637151/Taiji+-+VCU+Repo+download+and+Build+commands
> Last modified: 2026-05-09T04:25:46.000+02:00

---

## Overview

This page is to summarize how to download code and build

### Code download

For access related refer this page - Source code download for Taiji platform - GEN4 generic - Docupedia

> **INFO: Repo Init command**
> repo init -u cm_gerrit:projects/taiji/manifests -b rb-taiji_main_dev  -m rb-taiji-hqx121c1-pcs04.xml -g autosar --no-repo-verify --depth=5 repo sync -c -q --force-sync

### Build commands

To Build: Build.bat -p t1j -o app -tc TC37X/TC38X/TC39X

Build.bat -p t1j -o app -tc TC39X -bv CUBAS

To clean: Build.bat -p t1j -o app -tc TC37X/TC38X/TC39X

To debug : Build.bat -p t1j -o app -tc TC37X/TC38X/TC39X -d
