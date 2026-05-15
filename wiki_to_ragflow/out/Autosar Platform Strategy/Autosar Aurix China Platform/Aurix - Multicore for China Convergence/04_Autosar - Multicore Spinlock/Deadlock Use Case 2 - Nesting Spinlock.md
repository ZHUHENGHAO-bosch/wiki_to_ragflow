# Deadlock Use Case 2 - Nesting Spinlock

> Source: /spaces/CARSFW/pages/2917677552/Deadlock+Use+Case+2+-+Nesting+Spinlock
> Last modified: 2023-04-05T06:09:50.000+02:00

---

### Deadlock due to Nesting Spinlock

When a Spinlock is nested, then there is a chance of Deadlock as explained in below picture.

Here.

- Core 0 acquires Spinlock A
- Core 1 acquires Spinlock B
- Core 0 tries to acquire Spinlock B (Since it is already acquired by Core 1, it spins)
- Core 1 tries to acquire Spinlock A (Since it is already acquired by Core 0, it spins)
- Dead lock

To avoid deadlocks it is not allowed to nest different spinlocks. Optionally if spinlocks shall be nested, a unique order has to be defined

> **INFO: Nesting Order Check**
> OS will check for Nesting Order only if the spinlock type is STANDARD. ErrorHook will be reported if we try to Get Spinlock inside Spinlock If the Spinlock type is OPTIMIZED, Vector OS will never check for nesting order. So need to be careful when we are using OPTIMIZED spinlock type in our implementation.

![](../../../../_images/Deadlock%20Use%20Case%202%20-%20Nesting%20Spinlock/image-2023-4-5_11-54-36.png)

### Solution:

In case if Nested Spinlock is needed, we need to specify the order of spinlock in linked list

![](../../../../_images/Deadlock%20Use%20Case%202%20-%20Nesting%20Spinlock/image-2023-4-5_12-9-41.png)
