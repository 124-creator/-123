# 发布说明

这是2026年10月10日既有定义核查底稿的正文，历史状态与未知项保留。正文中的“未发送”和“父代理未执行”是该报告形成时的状态，不是当前状态：用户随后报告已发送询证；父代理随后完成有限验收。暂无已提供的EEX答复。

# EEX分散度定义有限核实（不拟合）

## 裁决
**DATA_NUMERIC_GO / REPORTED_MEASURE_CONDITIONAL_GO / WINNER_POPULATION_H1_PENDING。** 已有数据不是不存在或整体NO-GO：2020—2025 EUA、EU/DE/PL、explicit successful 的1281条全部具备所需数量、主体均值与SD。可以定义并计算“报告字段比值”的非因果描述性对象；然而不能把当前Y直接认证为“成功主体内CV”，因为SD的统计群体尚无直接定义。没有执行关联统计、回归、残差变异检验或显著性预览，也未改变H1。

## 全量提取与完整性
- 2020—2025六份原件读出1327个日期行：1324 successful、3 cancelled。限定EUA T3PA及EU/DE/PL后，成功候选1281，数值完整可用1281；13个所需数值字段均无缺失、非数值、负SD或无效主体计数；未按X/Y大小删行。
- 年/平台成功数（EU / DE / PL）：2020 139/46/24；2021 132/45/46；2022 142/46/23；2023 143/47/24；2024 142/46/24；2025 142/45/25。与旧parsed_events逐个日期/平台/合约/status键完全一致。无重复键，1281个不同日期，同日多平台日期0。
- 三条取消保留raw状态，分别2020-03-17 EU、2022-03-02 PL、2022-02-01 EU。其获配均值和SD原始空白，不填0；成功投标条数和成功人数是原始0，与空白明确区分。其他产品不混入主样本。row_exclusions.csv完整保留排除流水。
- 保留了原始Date/Time、Auction Name、Contract、Status、Country和字段cell locator/number_format。quantity/主体均值/SD显示#,##0；Cover Ratio与Average number of bids per bidder显示0.00。整数均值使用半显示单位0.5并传播总量半单位误差；cover使用0.005并传播总量误差。显示格式只支持舍入诊断，不是官方舍入规则认证。

## 统计群体：分级，不偷换
|对象|本次证据|等级|
|---|---|---|
|提交均值mu_B|1281/1281在显示精度容差内吻合B/N|consistent-but-unverified：全部N主体解释|
|获配均值mu_W|1281/1281吻合V/S|consistent-but-unverified：成功S主体解释|
|获配均值按V/N|仅18/1281吻合，恰为N=S的18条；其余1263不吻合|非全部N均值解释的强数值诊断，非官方认证|
|提交/获配SD|标题确为per bidder；没有进一步群体说明|unknown：不能从均值推出SD同群体|
|SD分母|未找到n或n-1说明|unknown；未倒推population/sample|
|跨年度定义|六年字段标题/位置/显示格式一致|结构verified；语义不变仍unknown|

另有1281/1281吻合B/V=reported cover、B/bid_count=Average bid size、bid_count/N=Average number of bids per bidder。Number of bids submitted及Number of successful bids是投标条数，绝不替换N或S。N/S为主体数；全部候选通过条数>=对应主体数的必要检查。SD非负数量上界在两种分母假设下都未出现超界，这同样不能认证分母。

## 实际读取的直接文字范围
2020—2025每份只有Primary Market Auction一个sheet；没有Caption sheet、没有cell comment，没有发现文字脚注或SD计算定义。实际读取全sheet非日期单元格，literal及locator在source_excerpts.json。
- 六年Primary Market Auction!R6：Average volume bid per bidder。
- 六年!S6：Standard deviation of bid volume per bidder。
- 六年!T6：Average volume won per bidder。
- 六年!U6：Standard deviation of volume won per bidder。
- 六年!L6：Auction Volume tCO2；L5：Volumes；W5：Participants。
2017—2019只核标题和Caption，没有全行穷尽认证，不进入主样本。Caption!F3是EUA 3. Phase，H3是T3PA；航空产品单列EAA3。Caption主要是国家/产品代码表，不含两对均值/SD定义。产品代码线索及旧已读schema支持当前EUA识别，但不能拿2017“2013—2020”字面范围认证2021—2025统计定义。未联网，B3“More information”不是已访问网页。

## 机械关系与非代数内容
总量与人数确定均值，不确定主体SD。mechanical_relationship_check.json用有限synthetic向量检验：成功向量[1,3]与[2,2]总量和人数相同而SD不同；不是真实拍卖实证，也不证明当前控制后的剩余X变异。
若S成功者之外N-S主体获配0，p=S/N：
- population：var_all=p var_w+p(1-p)mu_w²；CV_all²=(CV_w²+1-p)/p。
- sample：s_all²=((S-1)s_w²+S(1-p)mu_w²)/(N-1)。
因此不能直接相减submitted CV与won CV，说拍卖压缩/放大同一群体不平等。两个不同群体的条件关联本身仍可研究，不是恒等式；p也必须作为显式参与结构考虑。当前reported CV=reported SD/reported mean，若SD和均值群体不一致，它只是字段比值，不是认证的主体CV。
仅不知道sample/population不是全部NO-GO：若确认每对SD/均值群体相同，reported-CV事后关系仍可估计并披露分母未知。需要统一population比较时，只能在确认ddof后按sqrt((n-1)/n)转换，不能暗选。未知群体比未知ddof更实质。

## 最短必要补充：一份官方字段说明，不继续无限audit
请提供适用于2020—2025 R/S/T/U四列的一段EEX定义或官方答复，回答：
1. bid mean/SD是否按同一N个提交投标的主体、先合并同一主体多条订单后计算；won mean/SD是否按同一S个成功主体，是否排除零获配的失败主体？
2. 两个SD分别除以n还是n-1？若历年有变化，给生效年份即可。
以上问题已写入OFFICIAL_QUESTION.md，未发送。若只想研究报告统计量而非成功者内分散度，可披露现有unknown并另经用户批准固定“reported fields association”对象；本次不偷偷替换原H1、不拟合。成功者内H1仍待第1项；第2项可作为披露/有限口径敏感性而非一票否决。直接近邻全文/新颖性依赖未在本次解决，不拿数据可计算认证投稿价值。

## 完整性与执行边界
14份原件均hash和bytes与旧manifest匹配，解析九份均用已验证的同一byte buffer：2017—2019限定标题/Caption，2020—2025全所需字段。运行后14份再hash无变化。原项目只读；只写本scratch；Python -B；复用既有venv，无安装、联网、旧模型/作者程序/pickle执行。ordinary可信静态文件scope，不声称修复S1目录对象授权。
verify.py返回passed=true、候选键1281、hash不变；这是本次执行层校验，父代理独立验收未执行。探针最初年份匹配误命中祖目录20260528导致对xls尝试openpyxl并失败，已改为basename筛选后生产全量执行成功；openpyxl默认style警告不影响现有value/显式number_format读取。verification.json中的未验证项明确保留。
