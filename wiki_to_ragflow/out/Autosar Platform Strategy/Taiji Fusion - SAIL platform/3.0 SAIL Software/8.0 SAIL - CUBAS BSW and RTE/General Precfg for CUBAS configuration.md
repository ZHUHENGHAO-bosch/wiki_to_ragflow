# General Precfg for CUBAS configuration

> Source: /spaces/CARSFW/pages/5061188830/General+Precfg+for+CUBAS+configuration
> Last modified: 2024-11-28T07:30:46.000+01:00

---

## 1，确认AeeePro环境 2，生成cubas配置工程 3，用AeeePro打开cubas配置工程 4 模块配置

## 1，确认AeeePro环境

cubas使用J6E_AR45__24_02 package，工具版本为 Aeee pro 2023.2.0.2， 首次使用过cubas mcu配置环境，请在工程目录 \Platform\stdcore\cubas下执行_install_Toolbasetools.bat

## 

## 2，生成cubas配置工程

在工程目录\Cust_apl\config\cubas\AEEE_mic_J6e下执行GenCubasPath.bat来生成cubas静态包文件夹快捷方式

![](../../../../_images/General%20Precfg%20for%20CUBAS%20configuration/image-2024-11-28_14-16-39.png)

## 3，用AeeePro打开cubas配置工程

打开toolbase AeeePro2023.2..0.2设置工作环境后，加载\Cust_apl\Config\cubas\AEEE_mic_J6e，勾选如下，进入界面后切换ABACUS,可以直接点解build确认环境是否无误，

![](../../../../_images/General%20Precfg%20for%20CUBAS%20configuration/image-2024-11-28_14-18-21.png)

![](../../../../_images/General%20Precfg%20for%20CUBAS%20configuration/image-2024-11-28_14-21-37.png)

## 4 模块配置

以上步骤没有错误即可自行配置负责的模块了，配置完成后，

1. 生成在 \Cust_apl\Config\cubas\AEEE_mic_J6e\_builds\J6E_MASTER\_out 路径下，请与参与编译的路径 \Cust_apl\Config\cubas\_out 比较拷贝到此路径下，才能完成配置BSW的配置；
2. 生成在 \Cust_apl\Config\cubas\AEEE_mic_J6e\_builds\J6E_MASTER\_gen\swb\rtegen 路径下，请与参与编译的路径 \Cust_apl\Config\cubas\rtegen 比较拷贝到此路径下，才能完成配置RTE的配置；

![](../../../../_images/General%20Precfg%20for%20CUBAS%20configuration/image-2024-11-28_14-25-23.png)

![](../../../../_images/General%20Precfg%20for%20CUBAS%20configuration/image-2024-11-28_14-24-52.png)
