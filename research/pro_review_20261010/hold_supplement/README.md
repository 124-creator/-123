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

## 为什么不是完整原始数据包

未确认EEX完整行情/拍卖原件的再发布许可，因此不公开逐场CSV、工作簿或可重构完整行情的逐行导出；论文全文也不上传。不是技术不能上传，也不是认定所有这些材料都禁止再发布。此目录提供可公开的派生汇总、系数draw、底稿正文和自写计算脚本；不能凭这些文件独立重算1281场回归。
官方来源入口（未在本次发布中重新访问）：
https://www.eex.com/en/market-data/market-data-hub/environmentals/eex-eua-primary-auction-spot-download

## 代码与口径

SCRIPT.py是本轮自写静态数据/OLS检查代码，不是旧作者模型。PROTOCOL.json保留来源hash，但将个人路径替换为local_only目录。输入数据不随包分发：如有合法取得且与列示hash相符的原文件，可按协议提供；否则不要绕过hash检查。可在不取得原数据的情况下运行 `python -B SCRIPT.py --self-test`，它只检验合成数学例子、OLS/FWL与损坏输入拒绝，不生成市场结果。
VERIFICATION.json是执行时回执的脱敏导出，里面protocol_sha256指向原冻结协议，不是公开改路径版本。PUBLICATION_RECEIPTS.json区分原文件身份与公开副本身份。MANIFEST.json记录本目录公开字节，hash不是来源真实性或事前冻结认证。

## 判读限制

普通log比值与log SD在隐含均值/覆盖率下的残差等价是代数，不是经济创新。真实报告舍入破坏精确等价，真实两规格beta接近只支持有限测量稳健性。不能从区间略低于1推出“压缩分散”，不能称认证CV、公平、集中、市场权力或因果。partial R2仅样本内条件拟合，不是外样本预测增益。

本补件不提供直接拍卖论文全文或期刊当前分区认证；Pro先前报告的外部阅读仍以其阅读声明为证据层级。请按证据匹配主张，而非用显著性保证发表。
