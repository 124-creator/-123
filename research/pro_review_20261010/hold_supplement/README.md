# EEX限时HOLD补件：底稿和分母/变换检查

本目录补齐网页端Pro要求的两项材料。不是新一轮选点，也不是投稿GO。

阅读顺序：
1. DEFINITION_REPORT.md：四字段标签、年度映射、样本选择和未知群体。
2. INDEPENDENT_REVIEW_REPORT.md：原最终规格独立复核与首次冻结PARTIAL。
3. TRANSFORM_REPORT.md、TABLE.csv、RESULTS.json：固定变换/分母检查。
4. BOOTSTRAP.csv：本轮普通log模型999次系数，不是999个新拍卖样本。
5. FOLLOWUP_PROMPT.txt：请Pro作限时HOLD后的明确判断，不再扩大任务。

全部1281场成功EUA、2020—2025、EU/DE/PL；不同项目/序列，不称独立碳市场。
原log1p beta=0.880231483，原区间引用既有独立复核。本轮普通log beta=0.879726344，999次3月块区间[0.760931257,0.997876241]。全部样本SD正值，无变换导致的删行。原始结果已见，本轮是post-result exploratory，不是原预设、预注册或未触碰验证。

## 后续更新：完整输入已补齐

首版只有汇总；用户随后明确要求上传完整输入。现见 [../full_data/README.md](../full_data/README.md)：六份原始年度XLSX、全部1281场逐行样本、筛选前1327行和46条排除流水均已提供。读者可以从原件核查并重新计算。请不要继续引用首版“缺少逐场输入”的状态。数据来源与第三方权利边界见完整数据说明，论文全文仍不上传。
官方来源入口（未在本次发布中重新访问）：
https://www.eex.com/en/market-data/market-data-hub/environmentals/eex-eua-primary-auction-spot-download

## 代码与口径

SCRIPT.py是本轮自写静态数据/OLS检查代码，不是旧作者模型。PROTOCOL.json保留来源hash，将个人路径替换为local_only目录；这是历史计算的脱敏导出，不能直接视为完整新执行接口。后续补齐的输入和独立原件核查程序位于../full_data，读者应据实际字段重新解析，不绕过hash检查。`python -B SCRIPT.py --self-test`只检验合成数学例子、OLS/FWL与损坏输入拒绝，不生成市场结果。
VERIFICATION.json是执行时回执的脱敏导出，里面protocol_sha256指向原冻结协议，不是公开改路径版本。PUBLICATION_RECEIPTS.json区分原文件身份与公开副本身份。MANIFEST.json记录本目录公开字节，hash不是来源真实性或事前冻结认证。

## 判读限制

普通log比值与log SD在隐含均值/覆盖率下的残差等价是代数，不是经济创新。真实报告舍入破坏精确等价，真实两规格beta接近只支持有限测量稳健性。不能从区间略低于1推出“压缩分散”，不能称认证CV、公平、集中、市场权力或因果。partial R2仅样本内条件拟合，不是外样本预测增益。

本补件不提供直接拍卖论文全文或期刊当前分区认证；Pro先前报告的外部阅读仍以其阅读声明为证据层级。请按证据匹配主张，而非用显著性保证发表。
