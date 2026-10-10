# EEX论文v3：正文定向审修与GitHub交接

日期：2026-10-10。最新远端写作基线：`16ab8ff415e51d69b750699f33d62f32c66e0ac4`。本版合并审阅了该提交与此前下载的v2，不覆盖两份历史稿。

## 先读

1. `MANUSCRIPT_EN.md`：完整英文正文。
2. `ONLINE_RESOURCE_1.md`：独立补充材料。
3. `EDITORIAL_REVIEW_ZH.md`：具体修订、数字/版面核对及仍存在的拒稿风险。
4. `TARGET_JOURNAL_CHECK_V3.md` 与 `SOURCE_LEDGER_V3.json`：真实期刊阅读及证据层级。
5. `AUTHOR_INFORMATION_AND_APPROVAL.md`：待作者确认的正式提交项。

对应Word文件为`MANUSCRIPT_EN_v3.docx`和`ONLINE_RESOURCE_1_v3.docx`。正文4张编号表、2图、4条编辑公式；补充材料4表、4条编辑公式。全部来自冻结结果，无新实验。

## 科学状态

当前稿件值得进入作者审阅，不是已经获得录用资格。重点为报告数量指标的条件共同变化和历史时期异质性，不是因果机制或新的预测模型。最大的未决风险是编辑是否认为这条经验事实具有足够的增量价值。学校认可不作为研究阻断，但CAS资格和完整收费不能猜测。

输入commit：`5745eb3ddca79602346053446583d794b0e09800`。
主结果commit：`e25c1e02e1a58e0aec1084f7419066855e9565ec`。
扩展commit：`d4b26f1bbd8c1d7c036259e48e119c9c12f6c9a9`。

## 文档构建

`tools/build_manuscript.py`依赖pandoc、python-docx和lxml，只转换当前文本/图件，不读取逐场输入或估计统计模型。图源见`support/figure_data.json`；`tools/build_figures.py`只绘制冻结点值与区间。`tools/verify_display_lock.py`检查受保护的文本/数值哈希，不冒充独立市场复算。

GitHub目录包含正文、补充、编辑说明、来源账本、格式构建器、展示锁和图源。会话完整ZIP另保留三份冻结结果JSON、237条数值来源账本及全文数字核验器；不声称每个历史实验大文件都重新推送。

作者最终确认前，不移除草稿声明，不发送投稿信。没有新的具体科学问题，不再反复增加模型或删改样本追求显著性。
