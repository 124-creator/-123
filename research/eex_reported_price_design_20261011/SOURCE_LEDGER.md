# 本轮真实阅读、版本与访问范围（2026-10-11）

## 项目来源

- GitHub 124-creator/-123，eex-market-data-acquisition-20261011，b99007b8401c59d63d298493a094c51ac2082f24：完整读pro_optimization_handoff的START_HERE_ZH.txt、PRO_PROMPT.txt、CURRENT_STATE.json；分支/目录只作元数据发现，不声称全库全文读完。
- 6cd665873c9bb11ed266bb3d5eea7e587ef2ca80：完整读eua_official_cutoff_pilot的START_HERE_ZH、FULL24_PARENT_ACCEPTANCE、FULL24_EXPLORATORY_PROTOCOL、FULL24_DELIVERY_VERIFICATION。完整树列举证实该目录只有元数据；FULL24_SOURCE_INDEX仅第1—160行。
- 文稿来源：6206f191cd22daf0fe9bc45b57fefa2539d3c74b的v8.1正文，以及b23920a1ed51bdd79428e4ebef5dd1bd2b9607e4的v8 SI、题名与REPRODUCIBILITY。实际完整读正文/SI；未用段落预览冒充完整审阅。
- 原六工作簿：5745eb3…固定完整输入，复用经本轮完整静态审查的自编XML审计器；未执行旧模型、notebook或外部作者代码。新240行官方表未读取。

## 本轮联网证据（仅一手来源）

1. Bosco B (2023), Trade, equilibrium prices and rents in European auctions for emission allowances. Environmental Economics and Policy Studies 25:87–113. DOI 10.1007/s10018-022-00344-y. https://link.springer.com/article/10.1007/s10018-022-00344-y 。出版商HTML全文可读；定向读§5及相关变量定义。首次在线2022-05-31，正式卷期2023。未重现其GARCH或作者收益。
2. MacKinnon JG, Nielsen MØ, Webb MD (2023), Cluster-robust inference: A guide to empirical practice. Journal of Econometrics 232:272–299. DOI10.1016/j.jeconom.2022.04.001。作者所在机构保存的出版版PDF：https://pure.au.dk/ws/portalfiles/portal/391370322/1-s2.0-S0304407622000781-main.pdf 。PDF全文解析可得，本轮定向读§4.3、§5.3及相关式35/36；未读每一页表格或复现作者模拟。用其说明CV1/WCR方法及少簇风险，不把21季度当自动充分。
3. Empirical Economics Submission Guidelines：https://link.springer.com/journal/181/submission-guidelines 。本轮正文可读；核对题名、作者、Word、摘要、关键词、图表、SI、声明与数据代码条款。资格CAS/全部费用本轮不确认。指南明确第三方受限数据可说明获得条件；不因非OA或GitHub存在推断再许可。

## 本轮失败与非访问

- OpenUmwelt 2022Q1官方样件：https://openumwelt.de/server/api/core/bitstreams/f21a9a64-169a-4fef-bcce-d1cb0758d128/content 。web返回Timeout/Internal Error，未取得正文或字节；没有改工具重试。
- Queens旧目录页和另一本Wiley cluster-method论文入口均返回Internal Error，不作为全文证据；最终使用上述不同的已成功取得指南论文。
- 运行环境curl GitHub API为DNS解析失败；GitHub连接器可读写。两者不混写成HTTP403。
- 没有调用付费LSEG/EEX API，没有提交询证、使用私有凭据、镜像绕过或OCR图形取点。

新官方数据的24份PDF属于团队取得，不是本轮工具全部取得；来源清单和哈希既不能证明native tick，也不能取代实际字节。
