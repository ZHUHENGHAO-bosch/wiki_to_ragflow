# Discussion on PS HOLD Preconditions

> Source: /spaces/CARSFW/pages/2795568613/Discussion+on+PS+HOLD+Preconditions
> Last modified: 2023-03-01T10:58:46.000+01:00

---

### Participants: Ellen, Alex, Donghua, Huang Can, Praveen

#### Meeting Minutes:

- Discussed on below truth table. Since we have Safety Shutdown path where When SoC State monitor detects SoC is not powered ON it will have backlight OFF via Safety Shutdown path
- Which means at least for Aurix Platform and Projects we don't need to consider serializer Power supply to monitor PS_HOLD as preconditions

![](../../../../../_images/Discussion%20on%20PS%20HOLD%20Preconditions/image2023-3-1_17-57-2.png)
