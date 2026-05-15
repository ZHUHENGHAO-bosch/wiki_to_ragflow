# Advantage of Basic Tasks over Extended Tasks

> Source: /spaces/CARSFW/pages/3012014383/Advantage+of+Basic+Tasks+over+Extended+Tasks
> Last modified: 2023-05-08T14:33:35.000+02:00

---

### 1. Scheduler Latency

With Basic task, we can reduce the time spent by scheduler in making decisions (The actual time spent by scheduler which consumes resources that cannot be used by real tasks anymore)

If we have Basic tasks, The scheduler will schedule the Task only after the alarm is expired. for example, if we have 5ms Basic task, OS will schedule only after the expiry of 5ms alarm.

As shown in below picture, the task will terminate after its execution, and it will be activated once the alarm is expired.

![](../../../_images/Advantage%20of%20Basic%20Tasks%20over%20Extended%20Tasks/image-2023-5-8_16-30-24.png)

But if we have an Extended task,

Scheduler will check for the event in a for loop , and if an event is found, it needs to find which event is set in a list of if condition as shown in below picture

This will eat up scheduler time and will affect the throughput of the system

![](../../../_images/Advantage%20of%20Basic%20Tasks%20over%20Extended%20Tasks/image-2023-5-8_16-34-47.png)

### 2. Task Sharing

Basic Task with same priority can share the stack → This will reduce the amount of RAM used for Task and IST stack

![](../../../_images/Advantage%20of%20Basic%20Tasks%20over%20Extended%20Tasks/image-2023-5-8_17-31-5.png)

Since we have enough RAM in Aurix PF, we are not enabling this feature as of now. But can be useful in other Platforms
