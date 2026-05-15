# Multicore Design Patterns

> Source: /spaces/CARSFW/pages/2476796598/Multicore+Design+Patterns
> Last modified: 2023-08-08T13:13:08.000+02:00

---

## Overview

There are number of design patterns to achieve Parallelization with Multicore system. We will see some of those in this page

### Master/Worker design pattern

Master core (Master) executes the code until it reaches an area when it can be parallelized. Then triggers the workers in another cores (Core 1 and Core 2) to perform the computationally intensive work.

Once the worker finishes work, Master starts again and completes the work

![](../../../../_images/Multicore%20Design%20Patterns/Master_Worker.png)

### Peer design pattern

This is same as Master/worker but here Master also shares the computationally intensive work with other cores

![](../../../../_images/Multicore%20Design%20Patterns/Copy%20of%20Master_Worker.png)

### Pipelined design pattern

In this pattern, application is divided into 'series of smaller, independent stages' - Where output of stage is input to the next

Each stage can be placed in different core

![](../../../../_images/Multicore%20Design%20Patterns/Pipelined.png)
