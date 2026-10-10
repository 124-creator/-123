# 网页端 Pro 独立研究审判入口（2026-10-10）
本目录是自包含、脱敏的研究决策交接，不是论文、全仓库验收或继续训练授权。

## 最新补件：EEX限时HOLD复审

用户已提供网页端Pro的审判回复；执行代理没有代用户调用或登录Pro。现已完成其要求的固定分母/变换检查，不再广泛选点。

请先读 [hold_supplement/README.md](hold_supplement/README.md)，其中包含两份完整核查底稿的脱敏正文、新结果表、999次bootstrap系数、自写脚本和执行回执。复制 [hold_supplement/FOLLOWUP_PROMPT.txt](hold_supplement/FOLLOWUP_PROMPT.txt) 请Pro继续作HOLD后的决策。

全部1281场样本不变；普通log模型正向关联保持。本轮是主结果之后提出的探索检查，测量稳健性支持不等于创新或投稿GO。

## 完整数据现已提供

用户随后明确要求上传当前实验的完整输入，现已补充 [full_data/README.md](full_data/README.md)。其中包含2020—2025六份原始XLSX、全部1281场逐行样本、筛选前1327条记录和46条排除流水，并提供 [EEX_FULL_DATA.zip](full_data/EEX_FULL_DATA.zip) 一次性下载包（含两份报告）。读者可以据原件重新解析并实算，不再被摘要缺少数值输入阻断。第三方原件不由仓库代码许可重新授权，数据来源与发布边界见完整数据说明。

以下保留首版交接说明，原目录清单已更新并覆盖本次补件。

阅读顺序：READER_BRIEF.md → DATA_SUMMARY.json → RESULTS_SUMMARY.json → LITERATURE_SUMMARY.json → ACCESS_AND_CORRECTIONS.md。最后复制 PRO_PROMPT.txt 到用户自己的网页端 Pro，并附本目录链接。尚未调用 Pro 或登录 ChatGPT。

已有助手的 NO-GO 不是裁判答案。请独立检查其是否把因果/真实采购门槛强加给可发表的描述性研究；最多比较三项具体问题并选择唯一问题，或说明为何全部 HOLD/NO-GO。

MANIFEST.json 列出本交接包除自身以外的全部文件字节数及 SHA256。SOURCE_RECEIPTS.json 保留首版历史收据；后续两份报告正文和完整EEX数据分别见hold_supplement和full_data。论文全文仍未提供；hash只是文件身份，不是真实性认证。

范围：只新增本目录；不修改 main、不提交旧脏树。既有生产 S1 失败及旧 manifest 不匹配仍属于旧发布边界，不能用本包校验宣称全仓库 PASS。
