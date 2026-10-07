# Pro第二轮复审入口：A′核验材料

本轮回应首轮Pro报告中的三个缺口：年度配额目标是否可用，综合＋价差是否代数退化，与最近论文是否有实质差别。不是模型训练或创新确认。

请使用同一个提交读取下列文件；在报告中列出实际打开的文件、阅读范围与失败项。只有路径或网页预览不等于已读。

## 按顺序阅读

1. FINDINGS.md：本轮结论、数字口径、继续/停止条件。
2. FINAL_VALIDATION.json、PUBLICATION_NOTES.json、SCOPE.md：已经执行、仍受阻、公开版转换与历史收据边界。
3. data/DATA_TARGET_FEASIBILITY.md；data/parent_results_normal/target_scope_statistics.csv、forecast_availability.csv、target_feasibility.json：49条目标范围统计与84条可用性记录。不要把报价日、共有日期、正量日、完整窗口原点和独立样本量混为一谈。
4. design/EQUIVALENCE_AND_DESIGN.md；algebra_checks.py、test_algebra_checks.py：负对照、泛函、误差依赖和容量/表示混淆。
5. institution/MARKET_CONTRACT.md、market_rules.json：字段含义、编制生效日、挂牌渠道、无成交延续和CEA22历史用途。
6. literature/NEIGHBOR_COMPARISON.md、neighbors_verified.json、citation_ledger.json：7篇近邻、稳定来源、版本与实际阅读范围。自动严格引用验收未完成；引用编号仅在本目录的文献账本内有效，不与制度/全仓库编号混用。
7. ../JOURNAL_SCREENING.md、../journal_candidates.json；institution/journal_gate_update.json：出版模式证据和CAS/学校资格缺口。

## 文件访问与复核

- PROMPT_FOR_PRO_REVIEW.txt是完整、可复制的任务书。
- target_feasibility.xlsx含5张工作表。不能读取二进制时，改读data/workbook_spec.json和两张CSV；仍需注明没有直接读取Excel。
- data/initial_source_receipt.json和仓库metadata/local_exchange_sources.json有冻结来源URL、哈希及字节数，但没有公开全国完整面板。团队本地已经读取/核验原件；公开读者不能仅凭哈希独立复算全量市场统计。
- private_evidence和_evidence在记录中出现时，指本地取证文件，不是这个公开仓库里可下载的全文。用已登记稳定URL合法重取；访问失败就保留缺口。
- 公开版保留一套parent_results_normal聚合输出，重复版本未上传。FINAL_VALIDATION.json描述此前普通/-O原件审计的对比，不意味着公开仓库含全部快照。

## 只运行无真实预测的检查

在相应目录执行python -B -m unittest discover -s . -v，并用python -B -O重复；data目录是6项数学/解析fixture，design目录是30项纯代数检查。完整原件审计另需合法取得匹配的本地快照，不能拿unit fixture替代真实数据。

预期交接：Pro给出继续/暂停补证/停止结论及可执行下一步，用户将回复带回，本地再核验修改。不要为了继续而承诺新意、三区或预测收益。
