# E2价格信息增量｜拍卖端已就绪，外部参照待样件

2026-10-11。固定v8：b23920a1ed51bdd79428e4ebef5dd1bd2b9607e4。本轮不覆盖v8，不重跑原数量回归。

**状态：HOLD_DATA。** 1,281场拍卖端价格/报价价差已从原件提取和核对；合格外部价格配对0条；价格回归0次。不能把审核代码通过当成经济结论通过。

## 本轮交付
- [裁决与实际读取范围](RESEARCH_DECISION_ZH.md)
- [条件性分析协议](DRAFT_ANALYSIS_PROTOCOL.md)：须在样件合格后冻结来源、时点与样本，当前不是已放行的统计分析
- [真实访问与失败记录](SOURCE_LEDGER.json)
- [原件价格字段核验](results/AUCTION_PRICE_AUDIT.json)
- [配对数据门槛结果](results/PAIR_GATE_RESULT.json)
- [新论文段落及Word](../../paper/eex_price_revision_20261011/START_HERE.md)
- [唯一需补的样件](DATA_REQUEST_ZH.md)

## 运行
```bash
python -B code/audit_auction_prices.py --input ../../research/pro_review_20261010/full_data --out /your/local/private/price_audit
python -B -m unittest discover -s code -p 'test_price_pair_gate.py' -v
python -B code/price_pair_gate.py --auctions /your/local/private/price_audit/auction_prices_local.csv --references templates/REFERENCE_SAMPLE.csv --calendar templates/AUCTION_CALENDAR.csv --contract templates/SOURCE_CONTRACT.json --out /your/local/private/gate
```
以上命令相对于本研究目录；私有目录请使用本机实际路径，不把此占位路径直接当成输入。当前模板为空，正确输出应是HOLD而不是零效应。来源合同是人工文档审查记录，不是验证权限的魔法开关。程序不会联网、购买、发送邮件、读取凭据、执行工作簿公式、反序列化模型或运行回归。

代码单元测试20项为纯人工样例。生成的逐场市场行与原单元格追溯仅留本地，仓库只提交源码、汇总、空模板和编辑稿；需要时可从已固定原件重建，不重复发布新市场数据。来源哈希不认证统计群体或首次发布版本。
