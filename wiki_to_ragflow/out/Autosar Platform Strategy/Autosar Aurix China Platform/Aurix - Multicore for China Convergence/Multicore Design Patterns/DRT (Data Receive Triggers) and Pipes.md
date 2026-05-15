# DRT (Data Receive Triggers) and Pipes

> Source: /spaces/CARSFW/pages/2478737789/DRT+Data+Receive+Triggers+and+Pipes
> Last modified: 2022-10-26T11:35:19.000+02:00

---

For the pipeline design pattern, it is good to use Data Receive Triggers (DRT) which will reduce/avoid spinning time

### Pipes

Pipe is a mechanism by which output of one process (Task) is directed into the input of another process (Task)

For example,

If Task A in Core 0 and Task B in Core 1 has to communicate, then for Task A to share data to Task B

- Task A should keep its write end open and close the read end of the pipe
- Task B should keep its read end open and close the Write end of the pipe

We can achieve this using spinlock

### DRT (Data Receive Triggers)

Data Receive Trigger is a mechanism where a data received by Task A in core 0 triggers an event in Task B in Core 1 (to indicate the data is received)

### DRT with pipes

For pipeline pattern, DRT with pipes will be very effective (will avoid the spinning time)

![](../../../../_images/DRT%20%28Data%20Receive%20Triggers%29%20and%20Pipes/DRT%20with%20Pipes.png)
