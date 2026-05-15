# China Convergence - Unit Test Guidelines

> Source: /spaces/CARSFW/pages/2843524223/China+Convergence+-+Unit+Test+Guidelines
> Last modified: 2023-03-16T08:33:11.000+01:00

---

### Mocks

Mocks for all modules shall be kept in a centralized repo (cnconvbase/autosar/mocks)

Each module can create a folder for their mocks. With this we can reuse Mock function of a certain module in all module Unit tst

Please don't create mocks inside module Unit test folder. Mocks should be in centralized repo as mentioned above

![](../../../_images/China%20Convergence%20-%20Unit%20Test%20Guidelines/image2023-3-16_13-24-43.png)
