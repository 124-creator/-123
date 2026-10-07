# 数据许可、来源与再发布边界

这里没有给所有第三方资料统一套用一个许可证。来源许可与数据真实性是不同问题；可公开访问也不自动等于可批量转载。

## EIA 三个官方原件

`RBRTEd.xls`、`RWTCd.xls`、`RNGWHHDd.xls` 来自美国 Energy Information Administration。EIA 说明其信息产品属于公共领域并允许使用/分发，同时要求使用者注明 EIA 和产品发表日期，未授权用户暗示 EIA 背书。[1]

本仓库保留原来源URL、2026-10-07取得时刻和服务器 Last-Modified（2026-09-30），不把服务器更新日期当作逐日首次发布时间。三个文件分别是 Brent、WTI、Henry Hub 现货，不是碳期货、油气期货或欧洲 TTF。

## 中国大陆 EPU/TPU

原件：`China_Mainland_Paper_EPU.xlsx`。工作簿原始说明允许在注明作者、论文及 policyuncertainty.com 的条件下自由使用。[2]

保留署名：Steven J. Davis、Dingqian Liu、Xuguang S. Sheng；《Economic Policy Uncertainty in China Since 1949: The View from Mainland Newspapers》（2019）。原件及 `metadata/audit_results.json` 留有原署名和许可文本。[2]

没有将作者其他产品或网站文章的许可一并推定为相同，也没有声称已获得其指数的逐月首次发布时间。

## 作者公开碳价资料

署名：Wang, Minggang (2020), Data for: Carbon price forecasting with complex network and extreme learning machine, Mendeley Data, V1, DOI: 10.17632/v25wkdwgvm.1。[3]

仓库许可证：CC BY-NC 3.0。使用或进一步发布原件及衍生表时保留署名、指出转换及非商业限制；不要将其作为商用数据许可。[3]

本仓库对 `data.xlsx` 的转换仅将 Sheet1 日期/作者价格排序导出 CSV；未修正价格、换汇、填补日期或执行 ELM 模型。两个工作表内部一致不构成 ICE/交易所价格认证。

## 暂不再发布

全国、广东、湖北报价网站原始快照暂未确认可用于公开仓库的批量再发布授权，存于忽略目录。以下载URL、字节哈希、独立统计摘要和自用下载工具交付核查路径，而不是转载整个报价表或网页模板。

R10 论文代码/数据RAR、作者预分解结果、其他作者包、旧训练输出和授权供应商数据均不在本次发布范围；不能因这个仓库公开就推定这些材料可再许可。

本仓库原创脚本与报告尚未单独指定再许可条款；第三方数据继续适用上述各自许可。本说明是本次发布范围记录，不是法律意见。

## Sources

[1] https://www.eia.gov/about/copyrights_reuse.php
[2] https://www.policyuncertainty.com/media/China_Mainland_Paper_EPU.xlsx
[3] https://data.mendeley.com/datasets/v25wkdwgvm/1
