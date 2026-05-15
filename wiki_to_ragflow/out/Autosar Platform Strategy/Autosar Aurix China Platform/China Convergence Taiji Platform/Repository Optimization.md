# Repository Optimization

> Source: /spaces/CARSFW/pages/3429736971/Repository+Optimization
> Last modified: 2023-10-16T10:01:08.000+02:00

---

|   |   |   |   |   |
| --- | --- | --- | --- | --- |
| Manifest file | repo | Comments | Responsible | Finish Plan |
| cerberus-autosar | clusterbase/tools/QAC | Whether we need this ? No QAC is in Antifactory we can remove this no need Ji Hongguang: no any calls using this repo, can remove it. | Chery | 29 Sep 2023 |
| hydra | clusterbase/tools/DevelopmentEnvironmentExternalTools-legacy | Do we need this? need Ji Hongguang: we are using it, refer to link Download the Repository Praveen: We can use python in Antifactory instead of python in this repo | Chery | 29 Sep 2023 |
| hydra | DevelopmentEnvironmentPlatformTools-legacy | Do we need this? need Ji Hongguang: build code fail remove it. Praveen: We are using Tools.RAMROMMetrics and some tools from this folder so we need this | Chery | 29 Sep 2023 |
| Hydra | clusterbase/tools/unit-test/cppunit-eclipse ( used) clusterbase/tools/unit-test/cppunit (NOT used) clusterbase/tools/unit-test/hippomocks (USED) clusterbase/tools/unit-test/lcov (NOT used) | All these are in antifactory Remove all this repo and make sure CPP UT can be run before delivery Cerberus and Hydra modules use CPP UT Newton: Should be using by some fusa modules. | FUSA | 29 Sep 2023 merged in taiji branch 11 Oct 2023 |
| Hydra | clusterbase/autosar/diagnostics | We don’t use module in this repo Newton: We can remove. | Zeekr Xiaoyang | 29 Sep 2023 |
| Hydra | clusterbase/autosar/backlight" | We don’t use module in this repo Newton: We can remove. | Zeekr Xiaoyang | 29 Sep 2023 |
| Hydra | clusterbase/autosar/actuators/fan | We don’t use module in this repo Newton: We can remove. | Zeekr Xiaoyang | 29 Sep 2023 |
| cerberus-autosar | projects/cerberus/tools/automation | Do we need any of the python scripts in this repo? I think we don’t need. We can remove Newton: Need to check if not using, we should remove. Yu xiaoyang: "Generate Checksum on output srec" need Tools\Automation\ChecksumCalculation | Zeekr Xiaoyang | 29 Sep 2023 |
| cerberus-autosar | clusterbase/tools/laut-tc3xx | Why do we need this ? Need to check this Newton: These should be used, need to check. Yu xiaoyang: Debugger need this. | Zeekr Xiaoyang | 29 Sep 2023 |
| Hydra | clusterbase/build/build-scripts | I think we don't use these scripts. If not used please remove this | Zeekr Xiaoyang | 29 Sep 2023 |
| Hydra | BuildComplianceChecker | Check whether we use any of the python files in build process | Zeekr Xiaoyang | 29 Sep 2023 |
