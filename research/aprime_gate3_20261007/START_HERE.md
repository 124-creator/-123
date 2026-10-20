# A′第三轮：先核主张和资格，再裁决是否值得训练

当前范围更新（2026-10-09）：用户明确表示“学校认可可以不用考虑 请你继续”。学校认可不再是继续研究、补证或裁决的条件，不再索取学校材料；旧学校审计记录仅保留为历史，不变成已认证。传统订阅/非OA的既有出版偏好不因此取消，历史中科院三区目标也不因此获得认证。最新研究补证见continuation_20261009/RESEARCH_UPDATE.md；研究资料冻结截止仍为2026-10-07，后来读取与新访问单独记日。

本轮软件状态：独立复审不通过，用户授权的一轮限定修复已经停止。不训练、不认证创新。当前第三轮仅为本地未通过草稿，尚未提交或发布，没有第三轮固定提交SHA。上一轮已公开基线cfce35a4d2ddab44df85c0b0e427333810a192bd不能冒充本包；不要跟随main混用文件。当前软件状态先看verification/LIMITED_CODE_REVIEW.json及REPAIR_AND_REVIEW.md：L1/L2在本次源码/测试范围符合，S1父对象相对打开尚未实现；研究补证可以继续，训练和发布不能由此自动通过。

## 阅读顺序

1. SCOPE.md、CLAIM_CONTRACT.md：H1为其他年度Q数值信息增量，H2仅分项监督辅助。
2. FEASIBILITY_GATE.md、eligibility/results/summary.json及origin_eligibility.csv：新增成熟标签、20步历史、80验证全部成熟后评价的资格计数。CSV1138行含两个品种，各569行；只有元数据，没有价格/数量/预测/误差。
3. eligibility/eligibility_core.py、audit_supervised_eligibility.py、test_eligibility.py、secure_snapshot_reader.py及test_secure_snapshot_reader.py：源码静态阅读或获准的纯资格测试，不训练。读取器是未通过的软件草稿，不宣称已完成任何平台的完整读取安全认证。原件不公开，公开克隆的实源测试会跳过。
4. institution/FIELD_TIME_CONTRACT.md、CALENDAR_GATE.json、RULE_TIMING_LEDGER.csv，以及CALENDAR_RULE_TIMING_NOTE.md/INDEX_DISCOVERY_LOG.json：保留各自历史时点的制度草稿与访问范围。15条时间账本、10项历史日历缺口及6类历史学校材料不等于现行条件；学校材料已于2026-10-09移出当前要求。最新日历证据及仍未知项以continuation_20261009/RESEARCH_UPDATE.md与EVIDENCE_LEDGER.json为增补，不把quote union冒充官方日历，也不把后来读取回填为历史访问。
5. literature/DIRECT_NEIGHBOR_MATRIX.md保留历史8记录及阅读范围。2026-10-09两篇合法缓存XML的阅读增补见continuation_20261009/LOCAL_NEIGHBOR_REVIEW.json：子代理报告逐节阅读，父代理读回收据并核49条原文定位、14项对照和关键段，排除一项复制错的附录范围字段。其余六篇仍是旧范围，不是8篇全文通读，也不是创新/作者成绩认证。旧JSON七维对照可按需补读，但须记录实际范围。
6. protocol/PROTOCOL.md、config.json、analysis_contract.json：唯一候选h5/20步历史/250成熟训练/80验证/8管线/5%提议门槛。子代理的h1/60/1%草案不采用。
7. verification/LIMITED_CODE_REVIEW.json、LIMITED_REPAIR_PARENT.json、REPAIR_AND_REVIEW.md是当前限定失败记录；EXECUTION_SCOPE.md、REAL_INPUT_RECHECK.json、TEST_RESULTS.json、CODE_REVIEW.json保留各自历史时点/字节范围，不覆盖后来修改的全部代码。PUBLICATION_CHECKS.json及最终metadata/publication_manifest.json未完成验收，不将准备清单当成已发布证明。软件验证与研究门分开；临时目录偏差和被拒绝访问不被后续测试追认。历史第二轮FINAL_VALIDATION不是本轮清单权威；本轮没有提交后的新克隆或远端回读收据。
8. 根research/JOURNAL_SCREENING.md及上一轮institution/journal_gate_update.json只作既有期刊线索；本轮不认证现行费用或CAS资格。

## 新事实与未完成项

实源普通/-O资格输出一致，11份冻结原件前后sha/bytes未变。CEA22有208个临时评价资格，203终点在主期可评分，2025-02-28至2025-12-24；旧228只是报价诊断，不要求复现。203不是独立有效N、功效或官方监督资格。原件未公开，所以Pro不能由汇总独立重算。

Sustainability已做平价/非平价及宏观更新；Systems已保留无成交公布收盘并做风险/履约分组，宽泛“首次状态/防泄漏”被反证。Q是已有信息压缩，不是新数据或全年度向量；Qflat不等于每个成分都没更新。首次/完整同题排除和作者成绩均未认证。

研究目标是一次有限裁决，不是无限堆模型/补引文。若官方轴、可辩护报价时间/语义或实质差异不能成立，继续暂停或停止。本包没有真实预测、模型训练、收益认证、采购/套利/政策因果结论，也没有助手调用Pro；用户将把固定包与提示词交给Pro。
