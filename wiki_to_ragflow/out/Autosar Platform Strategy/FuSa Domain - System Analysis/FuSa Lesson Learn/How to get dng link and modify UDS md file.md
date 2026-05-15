# How to get dng link and modify UDS md file

> Source: /spaces/CARSFW/pages/4355263502/How+to+get+dng+link+and+modify+UDS+md+file
> Last modified: 2024-06-12T04:48:44.000+02:00

---

## 1. Open chery 8255 Software Req_Cart and add module explorer widget

here is the link below:

https://rb-alm-20-p.de.bosch.com/rm/web#action=com.ibm.rdm.web.pages.showArtifactPage&artifactURI=https%3A%2F%2Frb-alm-20-p.de.bosch.com%2Frm%2Fresources%2FMD_EBI2qx5QEe-KXae95JKs7A&artifactInModule=https%3A%2F%2Frb-alm-20-p.de.bosch.com%2Frm%2Fresources%2FBI_EBSntR5QEe-KXae95JKs7A&componentURI=https%3A%2F%2Frb-alm-20-p.de.bosch.com%2Frm%2Frm-projects%2F_8HIsAOK7Ee6XXvwUSNli6A%2Fcomponents%2F_8aqE8OK7Ee6XXvwUSNli6A&vvc.configuration=https%3A%2F%2Frb-alm-20-p.de.bosch.com%2Frm%2Fcm%2Fstream%2F_8a8_5uK7Ee6XXvwUSNli6A

Add module explorer to dashboard, so we can find specific SM easily

![](../../../_images/How%20to%20get%20dng%20link%20and%20modify%20UDS%20md%20file/image-2024-6-12_9-36-5.png)

## 2. Save htm file to get link

Go to a SM module, you can add some attributions in column,  and save the file as htm format.  Here is an example for SM13:

![](../../../_images/How%20to%20get%20dng%20link%20and%20modify%20UDS%20md%20file/image-2024-6-12_10-47-27.png)

![](../../../_images/How%20to%20get%20dng%20link%20and%20modify%20UDS%20md%20file/image-2024-6-12_9-42-30.png)

Download .py file to generate the links of SWRS-HLR-xxx, put this python file in the folder where you save the htm file

getLink.py

Run .py file

PS: this script is just a frame, you may modify it depending on the format of your htm file.

![](../../../_images/How%20to%20get%20dng%20link%20and%20modify%20UDS%20md%20file/image-2024-6-12_10-39-19.png)

## 3. Modify md file

Open md file in below path:

![](../../../_images/How%20to%20get%20dng%20link%20and%20modify%20UDS%20md%20file/image-2024-6-12_10-43-59.png)

Update dng file and SWRS_HLR- number in md file

![](../../../_images/How%20to%20get%20dng%20link%20and%20modify%20UDS%20md%20file/image-2024-6-12_10-45-31.png)
