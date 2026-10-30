# PolyWeave-FS 链织：部分数据、评价工具与最终DPO模型

公开内容包括300个规范结构（PI1M、OMG、SMiPoly各100个主来源样例）、30条训练区条件—目标示例、60条逐种子端点汇总、部分读取与评价代码、生成接口，以及固定种子101的最终全量DPO模型。

**模型下载：[GitHub Release](https://github.com/lfx030617-star/PolyWeave-FS/releases/tag/model-dpo-full-seed101-v1.0.0)。**模型包约895 MB，以7个分块附件提供。下面的标准库工具会自动下载、逐块校验、合并并解压，得到与服务器原始ZIP完全一致的文件；已下载完整且校验通过的分块可以复用。

```bash
python scripts/download_model.py
```

准备Python3.12及适配硬件的PyTorch环境，安装requirements-inference.txt后运行生成。已有验收通过的DCU环境保留厂商PyTorch，无需重新安装。

```bash
python -m pip install -r requirements-inference.txt
python scripts/generate.py --model-dir models/PolyWeave-FS-DPO-full-seed101 --example-index 0 --attempts 20 --output results/example_0
```

生成结果保存在本地，包括全部尝试、合格去重结构和汇总。连接点统一为裸`*`。详见[使用说明](docs/MODEL_USAGE.md)。

**继续不公开：**完整结构库、完整训练表、训练源码、原始生成池流水线、偏好对与概率缓存、其他模型、正式测试条件、原始生成记录、论文草稿及完整私有资源包。这些资料未进入公开仓库历史；最终模型权重单独通过Release公开。

数据示例按冻结文件顺序选择，非随机抽样；30条答案来自已有训练目标，不能据此报告模型总体生成性能。单个种子模型不等于论文五种子平均结果。有限图划分不等于严格骨架留出或预训练未见。完整参考库未公开，公开接口不计算完整库外新颖性。

本仓库自有接口代码采用MIT许可；模型包保留原PolyTAO Apache-2.0许可和修改声明，数据保留各上游条款。PI1M原README注明仅供学术用途，不将其数据示例另授无限制商业许可。端点汇总按CC BY 4.0共享。计算约束检查不代表合成可行性或材料性能已经验证。

论文引用时可说明“部分示例数据、评价与生成接口及一个最终DPO检查点公开”，不能写成“全部数据与训练代码已开源”。
