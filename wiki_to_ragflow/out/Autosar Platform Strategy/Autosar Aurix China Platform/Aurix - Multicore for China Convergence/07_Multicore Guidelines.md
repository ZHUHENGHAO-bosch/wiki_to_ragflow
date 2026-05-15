# 07_Multicore Guidelines

> Source: /spaces/CARSFW/pages/2396096776/07_Multicore+Guidelines
> Last modified: 2022-10-26T11:21:49.000+02:00

---

## OS

- Low priority non-preemptive tasks can slow down synchronization between cores
- Only runnables, which has sensitive to Jitter should be mapped to non-preemptive tasks
- If preemptive tasks with low priority own a spinlock, they can slow down the synchronization between cores

## RTE

- Always recommend to use implicit S/R and asynchronous C/S ports (which are more efficient with multicore OS)

Difference between Implicit and Explicit data access

- Implicit data access transmission means that a runnable does not actively initiate the reception or transmission of data. Instead, the required data is received automatically when the runnable starts and is made available for other runnables at the earliest when it terminates
- Explicit data reception and transmission means that a runnable employs an explicit API call to send or receive certain data elements. Depending on the category of the runnable and on the configuration of the according ports, these API calls can be either blocking or non-blocking

![](../../../_images/07_Multicore%20Guidelines/image2022-8-19_14-56-12.png)

### Spinlock

- If a task in the same core uses spinlock for a shared data, then make sure Spinlock is combined with interrupt lock
