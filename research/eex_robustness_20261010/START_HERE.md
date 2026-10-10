# EEX第二轮实验复审：正向关联稳健，强度随时期变化

核查与执行日期：2026-10-10。
基线结果提交：e25c1e02e1a58e0aec1084f7419066855e9565ec。
数据提交：5745eb3ddca79602346053446583d794b0e09800。

先读REPORT_ZH.md，再读KEY_RESULTS.json和CODE_AND_EXECUTION_RECEIPT.json。PROTOCOL_EXTENSION.json在新扩展拟合前写入，但历史数据及分期结果已见，不是预注册。

裁决：数值和有限稳健性支持继续限定主张的论文；不能认证已达到中科院三区录用标准。重要新增结果是2023–2025的关系强度高于2020–2022，不能写成时期恒定或归因某政策。

## 复现（从仓库根目录运行）

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -B research/eex_abc_results_20261010/code/audit_inputs.py --input research/pro_review_20261010/full_data --out /tmp/eex_new_audit
python -B research/eex_robustness_20261010/code/extend_review.py --data /tmp/eex_new_audit/normalized_input.csv --out /tmp/eex_new_extension --protocol research/eex_robustness_20261010/PROTOCOL_EXTENSION.json --prior research/eex_abc_results_20261010/results/results.json
```

输出路径须新建，不覆盖旧结果。Python3.10+；本轮运行3.13.5，NumPy2.3.5、SciPy1.17.0。原始审计脚本沿用前轮我们独立编写的只读OOXML解析；不执行用户包中的旧实验或模型。

本目录公开核心代码、原样协议、结果摘要和执行收据。随会话完整结果ZIP另有15项测试、测试日志、完整results/extension_run/中的逐draw输出与1897组抽样索引、独立算法交叉核对代码、Excel、PNG/SVG及长报告；不声称这些大文件全部逐个上传GitHub。所有输出可由固定代码与输入重建。

没有新市场数据缺口阻断本轮计算，无需重传六份工作簿。具体期刊历史CAS单刊记录和SD群体/版本说明仍未知，但不将学校认可重设为阻断。
