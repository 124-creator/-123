# 唯一尚缺的经济验证输入：逐场拍卖与时点一致的参照价格

当前E1已经使用现有六份工作簿完成，不需要重复下载2020—2025数量数据。2026年前9个月也已在运行器取得并计算；该原件因再发布权未确认没有包含在本包。

## E2先验一份样件即可

优先提供DEHSt 2024年第2季度（或同样本期其他一季）拍卖报告的合法全文，目的是核查是否存在**逐场数值表**及二级市场参照时点方法。

本轮实际尝试但失败的官方样件：
https://www.dehst.de/SharedDocs/downloads/EN/auctioning/2024/2024_report_Q2.pdf?__blob=publicationFile&v=6

其URL来自UBA官方出版清单。入口失败不证明报告没有所需内容，也不授权绕过访问控制。若用户能够正常取得，作为附件交付即可；不要付费购买或公开受限全文。

合格CSV的最低字段：auction_date、auction_end_timestamp_with_timezone、auction_product、auction_price_eur_per_tCO2、reference_product、reference_timestamp_with_timezone、reference_price_eur_per_tCO2、reference_quote_type（成交/买价/中价等）、source_document_and_row、usage_rights_note。

必须逐场配对、单位一致并说明产品期限。拍卖后日收盘、月份平均折价、图上的模糊点值及拍卖最高/最低申报价，不能假装投标截止前二级市场价格。现有工作簿的价格列不自动补齐这一缺口。

若样件只有月度均值/图形，没有可读取逐场数值且无合法配对数据，就继续HOLD价格关联，不无限追下载、不更换为更容易显著的结果变量。取得合格数据后先写E2具体协议，再看关系结果。

## 2026原件归档说明

用于E3的官方文件：
https://public.eex-group.com/eex/eua-auction-report/emission-spot-primary-market-auction-report-2026-data.xlsx

本轮取得字节数72742，SHA-256：
54e6fb649872d229333adb29b62a3ff5b7fddd7393facc047050fb8f87a1bf3d

年度URL是动态文件；以后下载若哈希不同，不得称为本轮完全相同的快照。运行器没有将原件提交或打包到公开产物，当前只保留哈希、代码、资格统计和结果。持有合法原件的作者应私下归档准确快照；不要求再发公开GitHub。
