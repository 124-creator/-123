# 原始资料与独立核查（快照日：2026-10-07）

本仓库不包含模型训练结果。以前任何实验目录、精度指标、预测文件和“PASS”结论都保持未认证状态；未上传、未执行、未用来证明数据真实性。

这里的“发现”仅是本次重新读取原始响应、核对字段及按官方制度版本重构后得到的数据核查事实，不是模型效果或已证明的研究创新。

## 给6pro的研究入口

先读 [START_HERE_6PRO.md](START_HERE_6PRO.md)，再完整读 [研究任务书](research/RESEARCH_BRIEF_6PRO.md)。用户已明确：目标为中科院三区，选择非开放获取／传统订阅发表路线，不是JCR Q3，也不是要求代码闭源。

新增 `research/` 目录提供10条论文公开包核查、19项近邻、近期补充检索、数据就绪与缺口、作者报价核对、期刊核查门槛，以及可直接复制的 `research/PROMPT_FOR_6PRO.txt`。记录有交叉，不能累加为独立论文总数。新增资料不扩大原数据的许可，不包含完整论文全文或旧模型实验结果。

任务要求6pro先反证选题新意、核实数据可得性和实际期刊资格，再给出一个主方向及两个备选或明确暂不足以选择。仓库候选不是既定答案，未调用用户的6pro会话，也未证明能发表。全国／广东／湖北完整历史日度面板仍未公开，只有取得并核验原件后才能做这些市场的数值实证。

## 已上传原件与解析表

| 序列 | 观察数 | 起始日期 | 截止日期 | 来源/定义 |
|---|---:|---|---|---|
| Brent | 9097 | 1987-05-20 | 2026-09-29 | EIA 日度现货，USD/barrel |
| WTI | 9512 | 1986-01-02 | 2026-09-29 | EIA 日度现货，USD/barrel |
| Henry Hub | 5698 | 1997-01-07 | 2026-09-29 | EIA 日度现货，USD/million Btu |
| 中国大陆 EPU | 923 | 1949-10-01 | 2026-08-01 | 月度指数；日期是月份标识，不是发布时间 |
| 中国大陆 TPU | 320 | 2000-01-01 | 2026-08-01 | 同一原始工作簿的月度贸易政策不确定性指数 |
| Wang 作者 EU 碳期货价格表 | 2059 | 2010-12-13 | 2018-12-27 | 作者公开资料，未认证具体合约、滚动、币种和单位 |

共 5 个原始 Excel 文件和 6 个解析 CSV。原件保持下载字节不变。EIA 文件按其再使用说明发布；EPU/TPU 工作簿保留原作者及论文署名；Wang 文件遵守 CC BY-NC 3.0，限非商业使用。[1][2][3]

作者提供的数据不等于已认证的交易所原生报价。`author_wang_eu_futures` 明确属于作者公开原件，不标为官方认证数据。

## 先读这些文件

- `reports/INDEPENDENT_FINDINGS_20261007.md`：本次独立核查发现、限制与待解决问题。
- `reports/RESEARCH_DIRECTION.md`：可证伪研究方向；尚未做模型实验。
- `DATA_LICENSES.md`：来源、署名、再发布边界。
- `metadata/raw_manifest.json`：原URL、下载时刻、字节数、SHA256、来源等级。
- `metadata/parsed_manifest.json`：CSV 行数、日期范围、SHA256。
- `metadata/audit_results.json`：本次从原件重新计算的机器可读结果。
- `metadata/local_exchange_sources.json`：全国、广东和湖北原始响应的下载入口及冻结哈希。

## 没有上传的内容

全国/广东/湖北批量报价快照未确认统一的再发布许可，因此暂留 `data/local_only/`，并由 `.gitignore` 排除。这里只发布独立统计、制度核查、来源和下载工具，不意味着这些官方数据是假的或禁止任何合法使用。

也未上传任何旧训练结果、模型权重、旧特征表、作者预分解结果、Wind/CSMAR/ICE 授权数据、凭据或个人工作目录。

## 验证与复算

实测运行环境：Python 3.13.13、openpyxl 3.1.5、xlrd 2.0.2。

```sh
python -m pip install -r requirements.txt
python scripts/verify_repository.py
python -m unittest discover -s tests -v
```

只对已公开原件重新解析：`python scripts/audit_snapshot.py`。注意：这会重新生成解析表及执行时刻，并把未请求的本地交易所检查标为未运行；不会假装重现缺失的本地快照。

下载一份当前全国综合价原始响应到忽略目录：`python scripts/fetch_exchange_sources.py --only cea_composite_live.json`。`--all` 还会抓取湖北 225 页，需要更多时间。下载结果若与冻结哈希不同，仅记录更新，不覆盖冻结原件或声称等同原快照。

要复核完整交易所统计，需要自行取得与来源清单哈希匹配的原件，放入 `data/local_only/` 后运行 `python scripts/audit_snapshot.py --include-local-exchanges`。没有这些原件时，相关测试明确跳过，不能据此声称全国、广东、湖北检查已复现。

## Sources

[1] https://www.eia.gov/about/copyrights_reuse.php
[2] https://www.policyuncertainty.com/media/China_Mainland_Paper_EPU.xlsx
[3] https://data.mendeley.com/datasets/v25wkdwgvm/1
