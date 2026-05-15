# Rte Multicore Handling

> Source: /spaces/CARSFW/pages/2394056119/Rte+Multicore+Handling
> Last modified: 2022-08-18T18:01:58.000+02:00

---

## Overview

RTE uses OS for communication between

- OS Applications
- Synchronization between the cores
- Sending events from one core to other

RTE generates the code that uses above OS functionality automatically

### Sender-Receiver Communication

1:n or n:1 communication. Senders provides the data and Receiver receives the data

#### Receiver Mode:

- Implicit data read access - when the receiver’s runnable executes it shall have access to a “copy” of the data that remains unchanged during the execution of the runnable
- Explicit data read access - the RTE generator creates a non-blocking API call to enable a receiver to poll (and read) data
- wake up of wait point - the RTE generator creates a blocking API call that the receiver invokes to read data
- activation of runnable entity - the receiving runnable entity is invoked automatically by the RTE whenever new data is available

![](../../../../_images/Rte%20Multicore%20Handling/image2022-8-18_21-23-48.png)

#### Rte_Read / Rte_Write (Simple Data Transfer)

At Sender side:

1. Sender writes data to using Rte_Write
2. Rte writes data to shared memory using OS IOC_Write(Inter OS communication) Call
3. Rte sets an event to Receiver core to inform it has sent the data

At Receiver side:

1. Event set by Sender will trigger Rte_read API
2. Rte reads data from Shared memory using IOC_Read API

![](../../../../_images/Rte%20Multicore%20Handling/image2022-8-18_21-24-42.png)

#### Rte_Receive/Rte_Send (Queued transfer of data)

![](../../../../_images/Rte%20Multicore%20Handling/image2022-8-18_21-29-2.png)

### Client-Server communication

N:1 Communication

![](../../../../_images/Rte%20Multicore%20Handling/image2022-8-18_21-31-34.png)
