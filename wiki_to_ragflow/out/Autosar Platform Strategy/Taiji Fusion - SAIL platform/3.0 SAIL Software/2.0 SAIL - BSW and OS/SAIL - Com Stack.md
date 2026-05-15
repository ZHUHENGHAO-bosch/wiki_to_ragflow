# SAIL - Com Stack

> Source: /spaces/CARSFW/pages/4875393030/SAIL+-+Com+Stack
> Last modified: 2024-11-07T08:20:11.000+01:00

---

## 1. Overview

This page is to summarize the Com architecture and other relevant information about Autosar COM stack in SAIL domain

### 1.1. One Click Com

One Click COM tool was implemented by ADAS team which will make the COM stack relevant part more easy

The supported features are listed as follows

- DBC import to generate ECU extract, ECU values and callback functions
- Valin mapping from CAN signals to internal variables.
- Valout mapping from internal variables to CAN signals.
- Signal Monitoring
- PDU Monitoring, including Timeout and E2E.
- SGU messages transmission.
- LGU messages transmission

### 1.2. PATAC  CAN Database import

For oneclick com we need input as dbc file. But our input is arxml from PATAC.So  need used one Python lib（Canmatrix） to convert the arxml to dbc and then use Oneclick com tool.

#### 1.2.1. Solution - Oneclick COM

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_15-55-13.png)

- Step one ： convert the arxml file to dbc format

First make sure Python 2.7 or later is installed

Install canmatrix

$ pip install canmatrix

convert the arxml file

$ canconvert source.arxml target.dbc

- Step two：Use Oneclick com generation ECU extract, ECU values files

Prerequisite : Environment items

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-4-12.png)

Note:

a) To support different python version and path, the user needs to update the path here:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-5-5.png)

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-5-26.png)

b) To quick install all the required python modules, the user can use this command list as follows, please update your own path correspondingly.

pip install -r D:\07_SBX\ii-bds\com_tool\requirements.txt --upgrade --target C:\TCC\Tools\python3\3.9.1-1_WIN64\Lib\site-packages

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-5-54.png)

c) If you encounter an unresolvable environment problem in note b), unzip ‘3.9.1-1 WIN64.zip’ in your local position and set python path in 'PythonConfig.json', such as:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-6-33.png)

GUI executable：

UI executable file location:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-14-39.png)

COM Basic Setting

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-20-38.png)

One Click COM GUI overall illustration

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-16-28.png)

In COM feature, it is divided into 3 areas:

Sub-feature select area ： is used for feature selection Configuration area： is used to configure customer requirements Information area： is used to log some information when generating files.

COMGen

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-25-43.png)

COMGen will import DBC to generate ECU extract, ECU values, callback functions and PDU monitor logic. DBC:absolute path of your DBC file NODE:name (in DBC) of your target node Channel:Don't change, keep it as it is. BusPrefix:name of the bus, set it as anything you want NoUseSig:Any signal containing the string specified here will be ignored during arxmal and code generation. For example, if NM, TimeSync, Diag messages and CRC/ALC signals are to be excluded, put the common part of the signal names here, then these signals will be ignored.

Click the ComGen button and generate ECU extract, ECU values files。in this path can find the generated ECU extract, ECU values files.

Output files path: \ii-bds-OneClickCOM_Radar_V2.0\com_tool\output

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-34-15.png)

- Step three：import  ECU values files  to AEEE Pro

#### 1.2.2. Solution - COM importer

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-10-16_16-39-56.png)

- Step one ： Use Java_Importer generation ECU values files

Prerequisite :

1. Customer input database

2. Java_Importer_GUI_2024-08-26

3. AEEE Pro ( 2023.2.0.2)

How get Java_Importer :

Use Toolbase get Java_Importer, more information see  picture below:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_13-46-8.png)

When the toolbase update completed, can find the  Java_Importer in this path :C:\toolbase\generic_importer\2024-08-26

more information see picture below:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_13-49-53.png)

Comment: Because Java_Importer installed from the Toolbase is not applicable to the current CUBAS project. The script for Java_Importer needs to be changed。

Updated Java_Importer in this path：\\temp_j6e_mcu\Tools

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_14-8-26.png)

Use Java_Importer generation ECU values file:

1. Open AEEE Pro， more information see picture below:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_14-10-44.png)

2. Import Java_Importer， more information see picture below:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_14-29-47.png)

After loading, switch the isolar-B view, export the ecuvalue file use the button, and then click "generate ECU Configuration Wizard " to proceed.

more information see picture below:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_14-41-16.png)

Next step， more information see picture below:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_14-42-35.png)

Select need generate PDUs， more information see picture below:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_14-47-50.png)

Click “finish” button， and then can find the generated  ECU values file.

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_15-0-17.png)

Comment: At the end of the ECU values file generation, there will be a pop-up window with an error message, which is ignored and does not affect the arxml file generation.

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_14-59-48.png)

- Step two：import  ECU values files  to AEEE Pro

Note：Before generating the configuration code, you need to manually delete the controller configuration of the CAN and CANIf modules, as shown in the following figure:

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_15-10-52.png)

![](../../../../_images/SAIL%20-%20Com%20Stack/image-2024-11-7_15-11-55.png)

wiki page for Taiji Cubas:

Import DBC files to arxml file - XC-CT China - Docupedia (bosch.com)

wiki page for Win3 Cubas:

How to develop Net&Com For CAN In Wave3 - wave 3 development - Docupedia (bosch.com)
