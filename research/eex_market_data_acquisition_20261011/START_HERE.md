# 新数据获取：从这里开始

本包在独立分支 eex-market-data-acquisition-20261011 上交付。它补的是数据与获取路径，不是已完成的价格经济实验；原v8、v8.1和数量回归保持原样。

## 取得了什么

1. Figshare 作者公开表：EU carbon price data.xlsx，36,646字节，平台MD5及本机SHA-256一致。作者数据集明确声明CC BY 4.0。[1] 原文件在 data/raw/figshare_28682684_v1/，同源解析CSV在 data/parsed/figshare_eu_daily.csv。
2. 实际读取1,577条日期/价格记录，2018-01-02至2024-03-27，无重复日期、缺失价格或数值零。标题的“2018–2024”不代表2024全年；本文件没有2025记录。结果由 results/DAILY_AUDIT.json 与可重读原表的代码支持。
3. 原表只有 date、Y 两个字段，未说明具体EUA/EUAA、交易所、现货/期货、合约、单位和收盘口径。它是作者提供的公开副本，不能称为交易所认证原始行情；逐年行数也不认证完整交易日历。本公开包依据作者声明的明确许可选择纳入原件，但没有把该许可外推为所有上游交易所或供应商的许可。[1]
4. Mendeley data.zip 也已真实下载，508,904字节、平台SHA-256一致。从其字节核验后的工作簿实际读取5,262个日期行，2005-04-22至2025-10-02；原表明确是连续EUA期货结算价及成交量，脚注标Wind。作者页面混写Wind/Investing.com，且许可文字提醒第三方内容可能需另授权。[2] 因此ZIP和行情行仅本机留存；GitHub只提供 results/HELD_SOURCE_AUDIT.json 的来源、字段与覆盖事实，不公开原始/派生报价行。
5. 该工作簿XML错误声明维度为A1，实际有5,269个展开行位置。已根据物理XML与 reset_dimensions 读取，而非误报只有1行；原文件未修改。归档成员名 data/期货结算价(..A).xlsx 原样保留，未根据元数据擅自补全文件名。

## 必须保留的研究边界

合格拍卖截止前参照仍为0条；有效价格配对0条；新价格回归0次。上述日度作者文件不能直接接入原时点价格门，不能将收盘、结算、成交、best bid和midpoint混为一种价格。

ICE官方历史服务说明有逐笔trade/quote交付，但跨市场广义历史年限不认证ECP产品2020–2025覆盖；说明列出的联系地址见 SOURCE_INDEX.json。[3]

本轮取得的ECP规格标注2026-10-10，确认当前每日实物交割产品身份，不能代替历史条款与行情样件。[4]

LSEG说明也明确派生数据并不会自动消除再分发许可义务。[5]

EEX官方REST服务是另一条可询证渠道；此前手册特定产品历史表不能被总体历史起点覆盖性地解释，不能据此购买错误数据产品。[6]

最有价值的后续动作是：先询清Figshare原系列的产品/单位/来源；严格时点方案则向ICE/EEX申请5–20个真实拍卖日样件，分别确认历史产品映射、事件时间、最近成交/无成交last best bid及研究使用与公开原始行权限。先样件、再全样本；不换模型凑结果，不把作者副本当作交易所认证，不改冻结主稿。REQUEST_DRAFTS_EN.txt 是草稿，未发送、未购买。

## 包内文件

- DOWNLOAD_INSTRUCTIONS_ZH.txt：实际成功的获取方式、复下载及核验命令。
- ATTRIBUTION.txt / LICENSE_DECISION.json：署名、转换说明、许可与不适用范围。
- SOURCE_INDEX.json / metadata/ACCESS_STATUS.json：六个新候选、实际失败与成功记录；后来的工具安全拒绝不被抹除或改称成功。
- DATA_DICTIONARY.md：保留原标签、明确未知口径。
- SOURCE_CONTRACT.json：每个实际解析输入必须出现在冻结的单源清单中。
- code/download_public.py：只下载固定Figshare文件，验证长度、MD5及SHA-256；不关闭TLS校验，不覆盖冲突原件。
- code/parse_daily.py：从已经验哈希的原字节生成/重核每一行CSV及覆盖摘要。
- code/verify_package.py / MANIFEST.json：包内选定文件的字节核对。
- results/LOCAL_EXECUTION.json：保留初始9测试历史；写入路径定点修复后，父方实际重跑14个不同测试，普通和优化模式各14通过、0跳过。这不是GitHub远程/CI收据，也不是统计贡献认证。
- results/CODE_WRITE_REPAIR.json：保留首次独立FAIL、两轮有界修复及错误--check调用的纠正；只认证实际静态预校验与独占创建，不认证完整目录对象、并发TOCTOU或双输出事务原子性。默认解析命令是只读模式。
- PRO_REVIEW_PROMPT_ZH.txt：可给网页端Pro审判的有界问题；本轮未自动调用Pro。

获取日期是2026-10-11，不回填为论文预注册或事前信息。没有运行旧模型、notebook、预测结果或重新拟合主稿。新增CI为只读核验，不自动提交、合并或训练。

Sources:
[1] https://api.figshare.com/v2/articles/28682684
[2] https://data.mendeley.com/datasets/d4bv52fgmd/1
[3] https://www.ice.com/publicdocs/ICE_Consolidated_History_Fact_Sheet.pdf
[4] https://www.ice.com/api/productguide/spec/18709519/pdf
[5] https://www.lseg.com/content/dam/data-analytics/en_us/documents/expert-talks/data-analytics-redistribution-expert-talk.pdf
[6] https://www.eex.com/en/market-data/eex-group-datasource/real-time-data
