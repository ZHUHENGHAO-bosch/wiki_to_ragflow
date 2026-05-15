# Deadlock Use Case 1 - Preemptive Task in Same Core

> Source: /spaces/CARSFW/pages/2917677539/Deadlock+Use+Case+1+-+Preemptive+Task+in+Same+Core
> Last modified: 2023-04-05T05:10:36.000+02:00

---

## Deadlock in Multicore when we use Spinlock

An example for deadlock in multicore

Task A and Task B runs in Core 0 -> Task A has highest priority

Task C runs in Core 1

![](../../../../_images/Deadlock%20Use%20Case%201%20-%20Preemptive%20Task%20in%20Same%20Core/image2022-8-10_18-2-52.png)

## Solution to Deadlock problem

Use Spinlock with interrupt lock mechanism

Task A preemption is stopped since interrupts are locked

![](../../../../_images/Deadlock%20Use%20Case%201%20-%20Preemptive%20Task%20in%20Same%20Core/image2022-8-10_18-6-33.png)

If a task in the same core uses spinlock for a shared data, then make sure Spinlock is combined with interrupt lock
