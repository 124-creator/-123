# 已完成的EEX A/B/C真实数据实验

**状态：EMPIRICAL GO（限定为报告字段条件关联）；非创新、因果或录用保证。**

优先阅读[REPORT_ZH.md](REPORT_ZH.md)、[SUMMARY.json](SUMMARY.json)和[结果表](results/ABC_TABLE.csv)。1,281场来自六份原始工作簿，不是由摘要生成的数据。A=B是本样本全部SD为正的结果，不计独立验证。

## 文件

- code/audit_inputs.py：独立标准库OOXML/CSV/字段溯源/排除链核验；不执行输入代码。
- code/run_eex.py：固定A/B/C、月份固定效应残差化、共享月份块索引和预算。
- code/test_run_eex.py：27项人工数学测试，不是市场实验。
- code/independent_check.py：完整dummy与显式重复行数值复核。
- results/：本次真实点估计、区间、敏感性、执行收据。
- audit/：原件与数字链核验、独立实现和实际测试日志。
- PROTOCOL_LOCK.json / gate1_review.json：探索后的执行配置与有边界的字段判断。

## 复现

原始输入固定到5745eb3ddca79602346053446583d794b0e09800的research/pro_review_20261010/full_data/EEX_FULL_DATA.zip。解压后INPUT_MANIFEST.json须在输入根目录。新建工作目录，原件保持只读；不要用摘要或旧预测表替换输入。

```bash
python -m pip install -r requirements.txt
# Put the extracted EEX_FULL_DATA contents in work/input (keep the original ZIP).
python -B code/audit_inputs.py --input work/input --out work/audit/verified
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -B code/run_eex.py \
  --data work/audit/verified/normalized_input.csv --gate gate1_review.json --out work/results
python -B -m unittest discover -s code -p 'test_run_eex.py' -v
python -B -O -m unittest discover -s code -p 'test_run_eex.py' -v
OPENBLAS_NUM_THREADS=1 python -B code/independent_check.py --root work
```

Windows可先设置相应BLAS线程环境变量。审计脚本已有现存输出目录时拒绝覆盖；计算也拒绝覆盖。artifact_tool交叉导入是本轮的第二读取路径，主复现不要求此内部工具，可仅用标准库原件解析。

重抽样采用SeedSequence([20261010,L])；这是前一轮已给程序的随机数流，不追求匹配团队另一初始化的区间端点。相同整数seed不代表两种初始化方法输出相同序列。

完整结果ZIP另含3,793条重抽样拟合记录和1,397套月权重。可以由固定配置再生；不需逐场原始数据再发布到新结果目录。数据许可不因本代码改变。新的公开结果也不代表全库旧S1/manifest验收通过。
