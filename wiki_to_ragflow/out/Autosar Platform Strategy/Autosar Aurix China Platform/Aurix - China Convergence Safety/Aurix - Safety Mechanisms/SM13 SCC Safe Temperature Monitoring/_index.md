# SM13 SCC Safe Temperature Monitoring

> Source: /spaces/CARSFW/pages/2411013000/SM13+SCC+Safe+Temperature+Monitoring
> Last modified: 2023-03-21T08:05:53.000+01:00

---

For China convergence safety, we have only SCC as an ASIL B complaint, hence temperature monitoring of Aurix is considered

The TC3xx has two internal temperature sensors integrated:

- Die Temperature Sensor (DTS)
- Core Die Temperature Sensor (DTSC) on-chip.

Both temperature sensors are technically the same, but physically located on different places. The DTS is placed close to PMS (Power Management System) and AD converter cluster. The DTSC is located close to CPU core cluster.

![](../../../../../_images/SM13%20SCC%20Safe%20Temperature%20Monitoring/SM13%20%20SCC%20Temperature%20Monitoring.bmp)
