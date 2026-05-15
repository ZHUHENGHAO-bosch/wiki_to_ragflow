# E2E DBC Validation

> Source: /spaces/CARSFW/pages/5226340599/E2E+DBC+Validation
> Last modified: 2025-04-10T04:11:45.000+02:00

---

### E2E requirement checklist

| No. | Description | Maxus |
| --- | --- | --- |
| 1 | E2E 算法是否提供, |  |
| 2 | 是否为标准autosar profile |  |
| 3 | DBC中E2E 报文是否有创建信号组 |  |
| 4 | DBC中E2E报文没用到的字段是否有填充信号 |  |
| 5 | 填充信号是 0 或 1 |  |
| 6 | E2E发送的报文是不是都是 cyclic 属性的（没有CE类型） （Event发送 不要通过RTE调用， 触发os hook） |  |
| 7 | 创建的信号组 是否 都是8字节一组的 |  |
| 8 |  |  |
