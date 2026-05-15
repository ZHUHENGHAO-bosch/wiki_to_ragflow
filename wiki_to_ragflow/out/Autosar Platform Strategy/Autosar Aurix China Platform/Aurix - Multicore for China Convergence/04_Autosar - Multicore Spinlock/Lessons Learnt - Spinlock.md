# Lessons Learnt - Spinlock

> Source: /spaces/CARSFW/pages/2917677656/Lessons+Learnt+-+Spinlock
> Last modified: 2023-04-05T06:20:44.000+02:00

---

### Issue 1: ErrorHook called when INC tries to log message via DLT in Core 2

DLT and INC both uses Spinlock for Multicore handling.

Currently both INC and DLT spinlock are configured as STANDARD

Now in Slave Core 2, Inc Tries to log an DLT message inside its own spinlock. Since DLT also has a spinlock mechanism, when it tries to Get its Spinlock ErrorHook is called with E_OS_NESTING_DEADLOCK

#### Solution 1: Make DLT spinlock as Optimized

Since inside DLT we are sure that we will not call any other Spinlock, there is no chance of Deadlock as explained in Deadlock Use Case 2 - Nesting Spinlock - XC-CT China - Docupedia (bosch.com)

So we can configure DLT spinlock type as Optimized. Since for Optimized spinlock, nesting order will not be checked by OS, we will not get ErroHook

![](../../../../_images/Lessons%20Learnt%20-%20Spinlock/image-2023-4-5_12-16-16.png)

#### Solution 2:  Configure Nesting Order for DLT and INC

Configure the Nesting order for INC spinlock. This will make sure ErrorHook will not be called

![](../../../../_images/Lessons%20Learnt%20-%20Spinlock/image-2023-4-5_12-19-9.png)

#### Decision:

Since we confirm that DLT will not have any nesting of Spinlock and Optmized Spinlock will improve performance we will go with Solution 1: Make DLT spinlock as Optimized
