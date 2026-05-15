# Theory on Speedup

> Source: /spaces/CARSFW/pages/2458140350/Theory+on+Speedup
> Last modified: 2023-08-08T13:15:04.000+02:00

---

Amdahl’s Law

An application has

- multiple independent tasks in parallel
- multithreading one application so that it runs across multiple cores
- Mix of both

For any architecture, there will be a portion that can't be parallelized (Serial Portion S) and a portion that can be parallelized (N)

Speedup = 1/(S + (1-S)/N)

For example, in a system if we have 60% of the application can be parallelized which means 40% can't be parallelized

For S = 0.4 and we have 3 cores (N = 3)

Speedup = 1/(0.4 + ((1-0.4)/3)) = 1.67

For example, with single core if a logic takes 10s, with 3 cores the execution can be completed in ~6s

![](../../../_images/Theory%20on%20Speedup/image2022-10-12_18-6-45.png)

Amdahl’s law is based on fixed problem size and it didn’t consider the HW particulars on the execution time (Cache memories, pipelining) ->that is of an execution workload that does not change with respect to the improvement of the resources

Gustafson’s Law

In a system, the relative size of the serial portion decreases over time and the parallelized portion grows. Gustafson’s Law states that the speedup for such a system—known as scaled speedup as

Scaled Speedup = N + (1-N) x S

Example. — A task that reads the data from SPI single channel and copies the data into memory and other tasks that process the data in memory.

The part that reads from SPI can't be parallelized but the part that process the data can be parallelized. So the performance measurement of static part (s) and parallel part (p) depends on how much data received on SPI channel

![](../../../_images/Theory%20on%20Speedup/image2022-10-12_18-8-28.png)

So which law to use is based on the architecture, but both shows high speed can be achieved by parallelization
