# Sphinx  generate SWRS/SWCDD/UDS

> Source: /spaces/CARSFW/pages/4219635088/Sphinx+generate+SWRS+SWCDD+UDS
> Last modified: 2025-01-14T04:30:34.000+01:00

---

#### Demo in  sharepoint : https://sites.inside-share3.bosch.com/sites/167912/Documents/0000.Overall%20Project/16.%20Functional%20Safety/10_Supporting_Workproducts/03_Safety_Mechanisms/SM53%20Safe%20Telltale/_build/html/swrs/swrs_index.html

Document is like below :

![](../../../_images/Sphinx%20%20generate%20SWRS_SWCDD_UDS/image-2024-5-16_17-55-35.png)

## HOW TO :

### 1 Install  sphinx with python or  use sphinx  docker image(sphinxdoc/sphinx:latest) .

Generate docs with docker could refer below steps, Otherwise could install sphinx with python Documenting with Sphinx

1. Demo docker-compose.yml   :
2. Install below sphinx extensions after first step:

- pip install sphinx     （Version: 7.3.7）
- pip install pillow        （Version: 10.3.0）
- pip install sphinxcontrib-plantuml   （Version: 0.30）
- pip install sphinx-rtd-theme               （Version: 2.0.0）
- pip install sphinx_needs  （Version: 2.1.0）
- pip install breathe             （Version: 4.35.0）
- pip install doxysphinx         （Version: 3.3.8）

### 2   For CNCovbase, we have template sphinx config file

convbase.zip

### 3 Generate SWCDD html

1. cd ./convbase
2. sphinx-build -b html source build
3. we will get html document in ./build folder

![](../../../_images/Sphinx%20%20generate%20SWRS_SWCDD_UDS/image-2024-4-28_15-57-49.png)

Congratulations!  You got a html document as below:

![](../../../_images/Sphinx%20%20generate%20SWRS_SWCDD_UDS/image-2024-4-28_16-2-26.png)

## Taiji Practice

Template repo : project:projects/taiji/cnconv/config/FuSa/swcdd · Gerrit Code Review (bosch.com)

Refer to template folder to generate swcdd and uds at one time.

In every SM's sphinx subfolder :

1. mkdir build &&  cd build
2. cmake ..
3. make sphinx

1). add comments like this

![](../../../_images/Sphinx%20%20generate%20SWRS_SWCDD_UDS/image-2024-5-13_13-48-40.png)

2). If \implement or \verify   is used in before project,  need update  uds/requirements.md which is supposed to generate UDS Req chapter like below :

![](../../../_images/Sphinx%20%20generate%20SWRS_SWCDD_UDS/image-2024-5-13_13-53-12.png)

3). In Taiji platform we could use DOORS ID attribute in DNG to track requirement id in code and classic Doors.

![](../../../_images/Sphinx%20%20generate%20SWRS_SWCDD_UDS/image-2024-5-14_19-41-57.png)

### 4). We could save DNG page as html file, so we can extract requirement id link via script. It looks like below .

![](../../../_images/Sphinx%20%20generate%20SWRS_SWCDD_UDS/image-2024-5-17_11-39-18.png)

### 

https://rb-alm-20-p.de.bosch.com/rm/resources/BI_rkQSlVF-Ee6aZZPhXPVuIw

### Reference:

1. Convbase: SWAD & SWCDD - Creation With Sphinx
2. https://inside-docupedia.bosch.com/confluence/display/SWDEFINEDCAR/Docs+as+code+with+Sphinx
