# AI Safety Image

> Source: /spaces/CARSFW/pages/6896508473/AI+Safety+Image
> Last modified: 2026-03-13T08:57:35.000+01:00

---

##### Advantage:

针对固定坐标范围内， UIUE的更新及小的变更不再需要重新导入图片及花费工时， 符合国标的图标能够使用同一版模型，涵盖不同主机厂资源。

##### 落地方向：

- ISO/PAS 8800标准的解读及与 ISO26262的配合
- 系统分析，流程/工具支持
- 模型覆盖度，时效
- 高通芯片分析
- 数据集
- 测试

|   |   |   |   |
| --- | --- | --- | --- |
|  | Q | Comment | Status |
| 1 | 不同尺寸，不同客户，图片模型训练成本 | 04 Mar 2026 不同尺寸需要参数调整及数据训练。图片资源相差不大可以评估复用。 Dataset训练及管理 需要按照ISO/PAS 8800 进行。 | DONE |
| 2 | 同一客户中不同尺寸的 图片模型如何区分 (需要判断下同一版UIUE中不同大小图片的模型适配， 例如 ABS 和 挡位 大小不一样。 需要进一步测试。) | 如果不同尺寸使用不同模型， 系统资源需要评估 如果不同尺寸图片 resize使用同一个模型， 需要评估。 | ONGOING |
| 3 | 当前 EPL 中对 safety AI 的支持 | 目前EPL 流程中没有 ， 需要确认如何实施及audit 标准。 | ONGOING |
| 4 | 两种 yolov8 的 应用 | 评估是否需要冗余 模型， 性能及资源占用。 如果需要 冗余模型的选型及评判。 | ONGOING |
| 5 | Yolov8-det 的应用场景 | POC实际没有应用yolov8-det， 只用yolov8-cls做图像识别。yolov8-det 模型更复杂，不适用判断图标的case. | DONE |
| 6 | Pytorch -> onnx -> dlc   模型的性能评估及优化 | 当前GPU 使用23% 占用较多，需要优化。 POC模型使用6张图片一次喂入， 100ms, 看是否能优化。 需要支持更多的图片及大小。 | ONGOING |
| 7 | 是否有 GPU 的性能资源隔离 | GPU 资源隔离是否能实现。 当前GPU 使用23% 需要优化。 | ONGOING |
| 8 | Memory protect 具体实现 | 暂时没有实现， 需要进一步讨论必要性。 | ONGOING |
| 9 | 如何评判 AI 识别出来，驾驶员却不能识别的 case | 现在识别的数据集有限， 需要识别更多的corner case来完善数据集 。 需要讨论 数据训练的规范化及验证 。 | ONGOING |
| 10 | 在 DPU 中获得图片的硬件节点，与 MISR 的区别。 是否符合之前ASIL-B的定义。 | 使用screen 接口截图， screen_read_display() 接口读取的是合成后的图片。 | DONE |
| 11 | Yolov8中对具体图像的 并行识别。 | 需要进一步量化看下图像识别的时间 是否能满足要求 需要再确认模型提供的接口及 调用时间。 同问题6， 模型时间，大小 和 图片数量的优化 | ONGOING |
| 12 | MidTrim 做过模型评测， 可以借鉴的部分 ISO/PAS 8800 评估下的软件实施内容有哪些 ？ | yolov8的模型失效模式分析 dataset lifecycle( requirement/analysis/development/design/imp/verification/validation) AI Safety ( requirement/analysis/development/design/imp/verification/validation) | ONGOING |
| 13 | 高通的两套解决方案 SNPE vs QNN | 13 Mar 2026 SNPE 主要可以用于 8155， 生成dlc文件， 生成内容不能修改优化。 QNN  为第四代HTP,包含DSP， 为高通以后的工具。 QPM 中可以安装QAIRT, 同时包含 SNPE 和 QNN.  后续准备用 QNN 来部署在 8255 及以上的芯片。 |  |
| 14 |  |  |  |
| 15 |  |  |  |
| 16 |  |  |  |
| 17 |  |  |  |
| 18 |  |  |  |
| 19 |  |  |  |
| 20 |  |  |  |

##### Reference:

| Qualcomm doc |
| --- |
| 80-NL315-18_REV_E_Qualcomm_Snapdragon_Neural_Processing_Engine__SNPE__Overview.pdf |
| 80-PF777-22_REV_D_SM8150_SA8155_SA8155P_SM7150_Hexagon_Tensor_Accelerator__Hta__Overview.pdf |
| 80-PF777-141_REV_A_Snapdragon_Neural_Processing_Engine_Quick_Start_Guide.pdf |
| 80-PR886-1_REV_A_SNPE_DSP_and_Aip_Runtime_Concurrency_Management |
