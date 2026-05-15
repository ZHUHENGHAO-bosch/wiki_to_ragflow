# Sphinx generate SWRS/SWCDD/UDS in Windows Environment

> Source: /spaces/CARSFW/pages/4328951677/Sphinx+generate+SWRS+SWCDD+UDS+in+Windows+Environment
> Last modified: 2025-02-26T02:43:01.000+01:00

---

## 1. Install required software packages with python pip

Use a high python version( 3.8 or above ) to install these packages:

- pip install sphinx     （Version: 7.3.7）
- pip install pillow        （Version: 10.3.0）
- pip install sphinxcontrib-plantuml   （Version: 0.30）
- pip install sphinx-rtd-theme               （Version: 2.0.0）
- pip install sphinx_needs  （Version: 2.1.0）
- pip install breathe             （Version: 4.35.0）
- pip install doxysphinx         （Version: 3.3.8）

PS: if not use a high python version, doxysphinx will not be installed successfully ,the error is like below:

Note: please put the python path in your system environment variables path

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-6-4_18-44-1.png)

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-6-21_17-1-40.png)

python version:

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-12-20_13-13-18.png)

sphinx-build --version as below:

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-12-20_13-11-14.png)

## 2. Download chery 8255 code

After downloading the code, you will see a swcdd folder in below path:

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-6-4_19-7-50.png)

## 3. Modify need.py file

Find you need.py file, you can search in cmd with command <pip show sphinx-needs>

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-7-31_11-8-5.png)

modify file context:

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-7-31_11-10-16.png)

comment line 768 and add cal_hashed_id = str(uuid.uuid4()).replace('-','').upper()

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-7-31_11-11-26.png)

## 4. Modify conf.py Doxyfile  and swrs_index.rst

add one line "needs_id_length = 8  # Length of the ID suffix" as below in conf.py file

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-8-7_11-31-22.png)

doxyfile changed :

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-8-7_11-33-59.png)

Add unittest folder :

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-8-8_16-44-30.png)

Exclude .h file to avoid duplication ID error:

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-8-8_16-45-50.png)

swrs_index.rst changed:

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-8-7_11-37-0.png)

Patch you can follow:

[cheryD01] add SM14 startup, sm18 clk mon uds (811354) · Gerrit Code Review (bosch.com)

## 5. Create a build folder in SM's sphinx subfolder and execute commands

Use ADC_Controller module as example：

1）Run cmd in build path

2) Execute Cmake configuration command as picture below:

"xxx\bin\cmake.exe" -DCMAKE_MAKE_PROGRAM=xxx\bin\mingw32-make.exe .. -G "MinGW Makefiles"

```
PS C:\KANG\01_Projects\chery8255\Config\FuSa\swcdd\ADC_Controller\sphinx\build> C:\VP_ArtifactoryTools\cmake\3.14.2\bin\cmake.exe -DCMAKE_MAKE_PROGRAM=C:\toolbase\mingw\4.8.1\bin\mingw32-make.exe .. -G "MinGW Makefiles"
-- Now is windows
-- Configuring done
-- Generating done
-- Build files have been written to: C:/KANG/01_Projects/chery8255/Config/FuSa/swcdd/ADC_Controller/sphinx/build
```

Replace your cmake.exe file path and mingw32-make.exe file path with below path

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-6-4_19-26-4.png)

After running successfully, you can see some files generated in build folder

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-6-4_19-29-25.png)

3)Run cmake --build . -- VERBOSE=1 in cmd window

After running, you will see a new _build folder in the path, and swcdd is generated within it.

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-6-5_9-54-17.png)

![](../../../_images/Sphinx%20generate%20SWRS_SWCDD_UDS%20in%20Windows%20Environment/image-2024-6-5_9-54-39.png)
