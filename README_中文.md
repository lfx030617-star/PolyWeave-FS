# PolyWeave-FS 链织：部分公开版

这里公开的是精选样例和部分评价工具，不是完整数据集或完整训练工程。其余资料没有上传到本仓库。

公开范围：300个规范结构（PI1M、OMG、SMiPoly各100个主来源样例），30条训练区条件—目标示例，60条论文逐种子端点汇总，以及读取、约束评价和均值/标准差复算代码。

未公开：完整结构库、完整训练表、训练/生成源码、偏好对与概率缓存、权重、正式测试条件、原始生成记录、论文草稿、完整压缩包及本地路径清单。没有用.gitignore把这些内容“藏在公开仓库内”，它们从未进入此仓库提交历史。

样例按冻结文件顺序确定，非随机抽样，不能据此报告总体生成性能；30条答案来自已有训练目标，不是新模型输出。连接点统一为裸`*`。有限图划分不等于严格骨架留出或预训练未见。

```bash
python scripts/preview_data.py --limit 2
python scripts/summarize_results.py
python -m unittest discover -s tests -v
```

需要检查化学规则时，在Python3.12环境安装requirements-evaluation.txt，再运行`python scripts/check_examples.py`。代码不训练模型，不下载完整数据。完整参考库没有公开，样例检查不计算完整库外新颖性。

本仓库自有代码采用MIT许可；数据保留各上游条款，详见data/TERMS.md和licenses。PI1M原README注明仅供学术用途，不将数据示例另授无限制商业使用许可。论文端点汇总按CC BY 4.0共享。保留来源标记并引用原PI1M、OMG、SMiPoly论文。

论文引用本仓库时，应表述“部分示例数据及评价工具公开”，不要写“全部数据与训练代码已开源”。
