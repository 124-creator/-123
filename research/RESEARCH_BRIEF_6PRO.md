# 6pro 碳价格选题任务书

资料截止与本轮整理日期：2026-10-07。用户已明确目标为中科院三区，采用非开放获取／传统订阅发表路线；不是 JCR Q3，也不是要求代码闭源。学校认可的分区版本、大类／小类及 SCIE／SSCI资格仍需核实。

本次只整理了供6pro接手的资料，没有在用户的6pro会话运行分析，没有训练模型，也没有得到论文录用或预测提升的证据。旧实验、模型权重、特征表、预测指标和“PASS”持续不可信，不得补入。

## 先按证据审查，不要先堆模型

你的任务是查清数据是否支持一个实质性、可证伪、与直接近邻区分的研究问题，再筛选实际符合中科院三区与订阅路线的期刊。允许否定本仓库的候选方向；不能为迎合发表目标制造创新或有效性。

请先声明你实际读到的文件、未能读到的文件，以及联网／附件／代码执行是否可用。看到仓库目录不等于读过所有表格。没有市场原件时只能做选题与可得性分析，不能声称已经完成统计实证。

## 建议读取顺序

1. `research/publication_goal.json`：用户确认的目标与未决资格。
2. `research/data_inventory.json`、`metadata/raw_manifest.json`、`metadata/parsed_manifest.json`、`DATA_LICENSES.md`：可直接分析数据、来源等级、权利边界。
3. `reports/INDEPENDENT_FINDINGS_20261007.md`、`metadata/audit_results.json`：仅本轮原响应核查，不是预测成绩。
4. `research/author_quote_checks.json`：作者报价与官方字段的核对，不能把相异口径的差异全部当错误。
5. `research/papers.json`、`research/near_neighbors.json`、`research/literature_matrix.csv`及本文下方索引：已整理的论文包与近邻。
6. `research/search_update_20261007.json`：近期补充核查；其中未核实线索必须单独处理。
7. `research/DATA_GAPS.md`、`metadata/local_exchange_sources.json`、`scripts/fetch_exchange_sources.py`：缺口及获取原件的入口。
8. `research/JOURNAL_SCREENING.md`：订阅模式与分区核实门槛；不要把未确认候选当作三区。

## 数据就绪程度

仓库直接提供5个许可原件和6个解析CSV，覆盖EIA能源、EPU/TPU及Wang作者EU价格表；表级数量和日期范围见data_inventory。Wang表属于作者资料，具体合约、连续合约规则和单位尚未认证，不能直接用作主实证的官方报价。

全国／广东／湖北完整历史面板暂不在公开仓库。官方来源、冻结哈希、采集工具和汇总诊断已提供；它们不等于完整日度数据。原件未公开主要是批量再发布条件未确认，并非统一判假。若你能够合法获取公开原件，请保存实际取得版本并独立复核，不把更新数据冒充本仓库冻结快照。

更换文件扩展名、只发布CSV或设成私人分享，并不自动解决第三方数据的权利问题。作者仓库标了CC许可也不自动证明所有上游供应商数据均可再发布。缺失值不得转为0，latest不得默认当close，amount/quantity不得当成收盘价。月度指数日期标识不是首次公开时间。

## 三个待反证候选，不是已经成立的方向

A. 全国CEA观测目标定义与样本外评价的敏感性。研究动态综合价、年度配额等合法目标的区分是否影响目标匹配基准下的预测能力与区间评价。

关键反证：本轮官方综合价已经能按有效编制规则重构。重构与原价一致是数据核查，不是预测改进。不得故意用过时权重或错误零量标签制造一个差数据集，再把修复错误包装成创新。不同合法目标必须各用自己的随机游走基准、共同可比较预测起点与固定步长；不能跨目标比较裸RMSE便声称某目标更好预测。

B. 已知动态年度权重下，年度价格与综合价预测的聚合一致性及联合区间。探讨变化权重、活跃年度切换和相关预测误差是否使直接／底层聚合预测失配。

关键反证：层级预测、预测协调及误差传播已有方法；须检索时变权重和非平稳层级的直接近邻。2026年单一年度权重为1时聚合问题退化，不得把相同目标重复计为独立市场。未来权重、组分价格和新挂牌年度的冷启动都要按预测时已知信息处理。没有充分的活跃年度并行样本就放弃。

C. 外生政策／能源变量的真实信息可用性与碳价预测稳健性。比较发布日期、修订、月日频匹配及保守滞后设计对预测评价的影响。

关键反证：混频预测、EPU/文本融合及实时信息集研究并非空白。没有首次公开时间或历史修订版本时，滞后假设只能叫敏感性分析，不能叫已实现真实实时回测。还须证明碳市场特定的经济问题而非重复通用“避免泄漏”常识。

以上A/B/C都可被否定。若数据或近邻不支持，可提出更合适的新候选，并给出支持和推翻它的证据。不强制沿用上一阶段推荐。

## 实验设计必须先写清

- 精确资产、字段、货币／数量单位、交易渠道、有效权重及状态规则；不能以全市场总量代替对应报价渠道。
- 样本选择、训练／验证／测试按时间隔离；在预测起点重新执行特征选择、标准化、分解和调参，或者证明缓存等价。
- 一个主预测步长和少量预先指定稳健步长；分别定义下一官方交易日和固定多交易日，不用删日期改变期限。
- 目标匹配的随机游走是必要基准；再设置少量统计／线性与常见机器学习基准，按问题选择而非机械加深网络。
- 点预测报告相对基准损失和不确定性；区间同时报告覆盖、宽度、区间评分、校准成本及样本量。
- 区分预测时已知状态与事后成交状态；后者只能事后分组评价，不能提前作为特征。
- 预设等价界限与停止条件；不敏感可接受，宽置信区间应判证据不足，不能用“显著性不够”持续刷组合。
- 没有逐笔数据及识别假设，不声称恢复有效价或识别因果机制；SHAP/注意力/Granger不自动支持结构因果。
- 基础模型需记录公开版本、预训练时间／数据截止、实际可用日与成本，防止用后发布模型制造过去可交易性的假象。

## 你应输出的决策书

1. 数据就绪表：现在能分析什么，必须补什么，无法获得时是否应停止。
2. 近邻反证表：至少覆盖数据定义、时间协议、分解泄漏控制、点／区间与最新基础模型研究；每个关键判断有可回查的原始出处，全文／摘要／索引层级明确。
3. 一个首选方向及两个备选，或者明确“暂不足以选择主方向”。每个包含中英文暂定题目、经济／市场问题、可证伪假设、贡献、数据需求、已有近邻与区别。
4. 最小可行实验：目标与样本、时间协议、基准、主检验、稳健性和否定／停止条件；不要虚构实验数值。
5. 期刊门槛表：中科院官方可验证版本与大／小类、学校收录资格、当下订阅路线、额外费用、范围匹配及拒稿风险。查不到单刊分区就写待确认，不能拿JCR或其他品牌分区替代。
6. 分阶段行动清单与需用户补充的材料。录用概率、创新性和实验效果不得作保证。

建议决策准则：先过数据真实性／可得性、实质近邻区分和期刊资格三道门槛，再评价实现成本与统计辨识力。纯“分解+优化器+神经网络”组合、无机制的模型堆叠或为了效果换数据口径不作为优先方向。

## 论文包核查索引

以下是10条核查记录，不是10篇均已运行复现的论文。原件身份、数据认证与模型有效性分开判断。

### R01 | SW-HyDEC: A structure-aware hybrid decomposition and ensemble learning framework for carbon price forecasting

DOI：10.1007/s00521-026-11982-8。[33][11]

样本／产品：实际文件：广东1614条，2015-11-26至2023-01-13；湖北1613条，2015-11-25至2023-01-13；深圳SZA-2016为806条，2016-09-01至2022-04-12。均不含表头。；实际文件明确GDEA、HBEA、SZA-2016；同时含Open/High/Low/Avg/Close、Volume、Amount及外生变量。EUA_Price仍未明确点位和合约。。证据范围：出版商全文明确关联仓库；官方Figshare API v3给出文件、许可、名称；三个真实文件HTTP200、SHA256/MD5与API一致，全部工作表只读核查；不认证价格原生真实性或预测性能。。

使用障碍：share页及整包入口HTTP 202空响应，但已通过同一官方item API和三个单文件直链全部真实下载。；湖北ClosePrice有4条空值；三市场EUA_Price分别333、304、64条空值。下载成功不能等同数据无缺失或协议完整。；仓库仅3个工作簿，没有源码；插补、时间分割、外生变量可得性/许可和算法依赖仍要独立实现并核验。；深圳SZA-2016不能与深圳全品种均价或全国CEA合并；作者转载原价未与交易所逐行对比。；后续官方报价对比见research/author_quote_checks.json；作者表不应按全表已认证处理。第三方Wind输入的再发布权利仍需另核。。未独立复现作者预测指标。

### R02 | Carbon Price Forecasting Using Optimized Sliding Window Empirical Wavelet Transform and Gated Recurrent Unit Network to Mitigate Data Leakage

DOI：10.3390/en17174358。[36]

样本／产品：广东GDEA：2014-03-11至2023-03-10，1972交易日；湖北、北京、天津为另外的验证市场。；广东碳排放配额GDEA（主样本）；另外三个试点的配额碳价。。证据范围：本轮直接取得出版商XML全文；只核验字面可得性和文章样本声明，没有运行模型。。

使用障碍：可得性声明只有正文和联系通讯作者，不是公开原始数据下载。；没有检出原作者源码；逐窗口EWT、TPE搜索空间、时间分割和依赖版本需要自行依据正文实现并另外核查。；原价日期、零成交过滤和复现参数仍需对实际原始数据核对。。未独立复现作者预测指标。

### R03 | Forecasting the Price of Carbon with Macroeconomic and Financial variables

DOI：10.1016/j.jedc.2026.105435。[17][14][10]

样本／产品：价格及排放图为2005-03至2023-09，但正式预测样本明确为2012-06至2023-09，136个月；共同评价2018-12至2023-09。二者不得混为一个样本。；EU ETS实际/名义碳价；需要进一步核实底层合约定义与拼接。能源变量来自LSEG，核证排放及宏观量来自官方源。。证据范围：直接取得arXiv v3全文、版本记录和出版社身份API；未获取论文数据包或训练代码。。

使用障碍：论文仅列官方公共数据和LSEG来源，公共源网站不是作者原始建模表。；正文提到按请求获取的是额外稳健性结果及某些预测结果，不是全部训练数据可得性声明；不能误写为整包按请求提供。；MCMC代码参考Chan并经作者适配，引用别人代码不是公开本篇复现代码。；宏观修订历史、发布时间、年度排放时间分解和商业LSEG序列仍是重现障碍。。未独立复现作者预测指标。

### R04 | Carbon Price Forecasting with Quantile Regression and Feature Selection

DOI：10.48550/arXiv.2305.03224。[13][22]

样本／产品：EU：正文声称2009-03至2020-12、182样本，训练至2019-12，测试2020；广东：训练2017-01至2020-12共1082，测试2021-01至2021-08共162。；EU ICE ECX EUA期货收益；广东试点配额，不能把试点直接称全国CEA。。证据范围：arXiv摘要和实际下载PDF，使用现有pdftotext只读提取；不安装包、不运行论文源码。。

使用障碍：未检出数据/代码可得性专节或原作者下载入口，不等于证明不存在。；正文EU月度2009-03至2020-12与182条声称不一致；广东段又出现与其样本不符的2009-03至2020-12描述，需要作者更正和数据核查。；44因素+18技术指标与广东24因素尚无可下载完整建模表。；所谓TeX下载实际返回PDF，已按照文件魔术核实，不能记为源码已取得。；按正文2009-03至2020-12每月一次计算为142个月，不是182；不擅自修正原文182，记录这一疑点。。未独立复现作者预测指标。

### R05 | EU ETS carbon price forecasting via VMGE-Net: a variational decomposition and channel-aware GRU framework

DOI：10.1038/s41598-026-68475-w。[40]

样本／产品：出版社摘要称2017-01-20至2026-03-18，1994日观察、25个变量。；EU ETS碳价；摘要没有足够信息确定现货/期货合约与点位。。证据范围：出版社摘要和日期/许可信息；未取得完整实验协议和可得性声明。。

使用障碍：数据与代码可得性段在本轮可访问页面中缺失，不能写成作者明确不公开。；PDF入口HTTP 200但文件魔术为HTML，发生回跳；没有取得PDF全文。；具体分解参数、外生因子来源、序列点位和环境版本未知。。未独立复现作者预测指标。

### R06 | Comparative market dynamics using deep learning architectures for forecasting CO2 allowance prices across multiple jurisdictions

DOI：10.1007/s44163-026-01551-2。[34]

样本／产品：七辖区EU、中国、澳大利亚、新西兰、韩国、California、RGGI；共同工作日样本2022-09-01至2025-08-31。；作者统一称七辖区配额现货；供应商、产品代码、各市场真实交易点位须另外核实，不能仅凭该称谓保证可比。。证据范围：直接出版商全文；可得性明确，但不证明真实公开下载或协议已审计。。

使用障碍：按请求提供数据不等于已公开。；没有检出自己的代码或可直接下载的样本。；日历对齐、稀疏市场插补、调参与评价时段、各辖区资产定义仍需要精读和原始序列核验。。未独立复现作者预测指标。

### R07 | CarbonTimer: Overcoming data scarcity in carbon price forecasting with a large time series model

DOI：10.1016/j.jclepro.2026.149247。[9][5]

样本／产品：未核实（原记录为null）；未核实（原记录为null）。证据范围：出版社身份API与出版商提交Crossref元数据；403页面是阻碍记录，不是论文正文。。

使用障碍：HTTP 403/WAF限制，未读取数据与代码可得性声明，不虚构按请求或无公开数据结论。；模型预训练版本、预训练时间及潜在目标序列交叉污染，必须在取得正文/作者包后检查。；不能以其他Timer仓库冒称本论文代码或数据。。未独立复现作者预测指标。

### R08 | Do Carbon Price Forecasts Improve Compliance Procurement? Evidence from European Union Allowances

DOI：10.48550/arXiv.2607.23426。[19][16]

样本／产品：原始序列2019-01-02开始；80条烧入后2019-04-25至2025-12-31共1721交易日；测试2025-05-01至2025-12-31。；Investing.com提供最近12月到期合约滚动拼接的ICE Endex EUA futures报价，屏幕代码C、每手1000 EUA；不是现货也不是固定到期期货。。证据范围：直接arXiv v1全文及版本摘要；未下载作者样本、未运行预测与采购优化。。

使用障碍：网站历史公开与论文提供完整数据包不同，没有找到原作者可直接下载的建模表及代码。；连续合约滚动规则、发布时间和17:00伦敦截止需逐变量验证；美国收盘数据顺延到下一起点。；采购容量、冲击、风险与需求场景都是模拟输入；不能把模拟写成企业实盘。。未独立复现作者预测指标。

### R09 | Carbon price forecasting with complex network and extreme learning machine

DOI：10.1016/j.physa.2019.122830。[26][24][29]

样本／产品：实际文件2059观察，2010-12-13至2018-12-27；两张非空表是同样长的日期/价格表示，不能相加当4118独立样本。；仓库作者称EU ETS碳期货；文件只提供日期与价格，没有明确EUA/EUAA、交易所、到期/连续规则或收盘/结算点位。。证据范围：官方作者数据仓库页面/API与真实文件下载及所有3个工作表只读检查；论文仅身份/出版社API核实。。

使用障碍：能够下载作者数据但没有模型代码，仍不能直接等同完整可复现。；仓库API明确关联该论文DOI，但本轮出版社全文403，尚未在论文正向核实仓库链接；严格口径归为作者存储库关联，不计为已确认论文正向提供数据。；CC BY-NC限制商业使用；不能用仓库作者身份替代交易所原价真实性认证。。未独立复现作者预测指标。

### R10 | Gaps between market performance, government planning and social objectives: projections and comparisons of carbon price intervals

DOI：10.1057/s41599-025-05482-8。[41][25][28]

样本／产品：论文市场表现样本湖北现货日收盘2018-08-02至2022-11-30，训练截至2022-08-30，测试2022-09-01至2022-11-30；下载市场Data.xlsx为945条数据、17列但没有日期列，尚未逐日对应论文划分。另有省级年度MAC、2022夜间灯光等异频数据。；湖北碳配额现货价格及推导的政府规划价、社会MAC影子价；不能把三者全部当作交易所实际碳价。。证据范围：出版商可得性段直接链接nzsgz2h274；仓库实际文件API和HTTP200归档；SHA256与平台声明一致；只读检查六个XLSX和13个ZIP包，不执行MATLAB/Python/notebook。。

使用障碍：已具备与论文正向关联的数据和源码归档，但未运行，不声称重现指标。；源码主要为MATLAB，含Python LightGBM模块，读取发现trainNetwork、arima/garch、lightgbm/numpy/pandas；依赖版本、工具箱许可与随机种子未构成经过测试的环境。；官方仓库许可CC BY4.0与论文BY-NC-ND4.0不同；内部含第三方优化与分解源码，需要检查各自版权，不把存储库许可自动覆盖它们。；原始市场表未提供日期列；已有分解结果不能代替严格逐起点重新分解的证据。；RAR所有文件可列出，抽取六个工作簿与code.zip成功，13个内层ZIP均CRC通过；整包流式读取遇目录项解压错误，未宣称整个RAR完整性全通过。。未独立复现作者预测指标。

## 直接近邻索引

19项近邻中包含预印本、理论、交易机制和数据材料，并非19篇同类型预测论文；与上方论文目录存在交叉。

### frl_liquidity_2025 | The influence of market liquidity on the efficiency of China's pilot carbon markets

重叠点：直接排除“首次研究碳价薄交易、零成交与随机游走”之类宽泛贡献。。[4]

区分／限制：拟题只问公开综合行情、年度配额权重版本和供应商零值误分是否改变样本外相对随机游走能力与分组覆盖结论；不把流动性回归再包装一次。。证据范围：本子代理已读身份/出版社索引；2026-10-07主代理另读取作者上传全文并确认thin trading、volume、depth与random walk效率主题。全文核验是主代理提供的上下文，不冒充本子代理再次精读。。

### carbon_thickness_2009 | Carbon trading thickness and market efficiency: A non-parametric test

重叠点：“交易稀少会影响随机游走推断”早已有碳市场直接前例。。[37]

区分／限制：不是样本外预测/区间研究，也没有公开全国综合行情和供应商精度的版本审计。。证据范围：作者机构工作论文全文。

### ibikunle_2016 | Liquidity and market efficiency in the world's largest carbon market

重叠点：碳价可预测性、流动性及市场质量的关系不是新命题。。[43]

区分／限制：本任务没有其逐笔交易和订单信息；只能研究公开日频观测口径的预测稳健性，不能借用其微观结构识别结论。。证据范围：作者机构接受稿全文。

### systematic_staleness_2024 | Systematic staleness

重叠点：“利用陈旧价格提取流动性机制”已有成熟的一般金融方法。。[32]

区分／限制：公开综合价不是交易价；日频零收益不是其高频结构staleness估计量。这里必须只称观测更新状态，不称识别latent transaction/efficient price。。证据范围：出版商正式全文的作者机构副本。

### wu_qin_2021 | Assessing market efficiency and liquidity: Evidence from China's emissions trading scheme pilots

重叠点：中国试点、状态变化、效率—流动性联结早已有直接前例。。[31]

区分／限制：全国年度配额综合报价版本和供应商精度导致的样本外预测/覆盖差异，不是其核心设问。。证据范围：作者摘要：NCBI PubMed XML；非全文。

### eua_conformal_2025 | European Union Allowance price forecasting with Multidimensional Uncertainties: A TCN‐iTransformer Approach for Interval Estimation

重叠点：“首次碳价格共形区间”被直接反证。。[2]

区分／限制：不以再加一个Transformer/液性分组校准当贡献；拟题以公开价格定义和样本版本审计为对象。。证据范围：出版商提交的Crossref摘要；出版社页面403，未得全文。

### otsubo_2026 | Intraday and Daily Price Discovery in Carbon Markets: EUA Futures Versus Carbon ETFs

重叠点：碳市场报价停滞、非同步交易和“有效价格”已经有专门价格发现研究。。[7]

区分／限制：研究中国公开综合行情的数据定义，不竞争跨场所有效价格估计；EEX拍卖不能替代二级现货/期货。。证据范围：出版商Crossref摘要；出版社索引另提示多成分陈旧报价可能混杂，未得全文。

### rwc_2026 | Taming Tail Risk in Financial Markets: Conformal Calibration for Nonstationary Portfolio VaR

重叠点：“状态加权金融共形校准”“压力组条件覆盖”不是新框架。。[18]

区分／限制：只把已存在校准器当对照；窄问题是观测定义/错标签是否改变诊断，而不是发明状态加权。。证据范围：arXiv v3作者全文；预印本。

### dracp_2026 | Dynamic Regime-Aware Conformal Calibration for Reliable Economic Forecast Intervals under Multiple Distribution Shifts

重叠点：经济/能源/金融状态共形校准、漂移加权、条件尺度和在线控制均已有近邻。。[20]

区分／限制：本任务核心不是将以上模块重新拼接；需要明确“报价构造的已知制度状态”与一般未知波动状态不同。。证据范围：arXiv v1作者全文；预印本。

### kath_ziel_2019 | Conformal Prediction Interval Estimations with an Application to Day-Ahead and Intraday Power Markets

重叠点：能源共形区间、changing market conditions及点模型无关校准早有先例。。[21]

区分／限制：中国碳公开综合价的观测和供应商零值，不是其估计对象；不能把能源首次搬到碳作为宽泛贡献。。证据范围：作者arXiv v2全文。

### barber_beyond_exchangeability | Conformal Prediction Beyond Exchangeability

重叠点：漂移加权和最近观测优先不是新方法。。[49]

区分／限制：可以借其漂移风险理论，但公开日频综合报价并不自动满足交换性或其界所需条件。。证据范围：作者CMU论文全文。

### lo_mackinlay_1989 | An Econometric Analysis of Nonsynchronous Trading

重叠点：报价采样会制造某些自相关和随机游走拒绝是经典问题。。[42]

区分／限制：说明“观测可预测性≠可执行交易收益”；不推出所有碳价可预测性都由非交易产生。。证据范围：NBER作者摘要与出版信息。

### glas_hartmann_2022 | Uncertainty measures from partially rounded probabilistic forecast surveys

重叠点：“舍入影响不确定性/校准诊断”在相邻预测文献中已经存在。。[30]

区分／限制：本文舍入的是主观概率，不是供应商万吨成交量；不能将其经验结果直接外推为碳价舍入已造成同样偏差。。证据范围：经济计量学会正式全文。

### gottlieb_kalay_1985 | Implications of the Discreteness of Observed Stock Prices

重叠点：价格离散化影响波动矩不是新发现。。[1]

区分／限制：这里已经确认的主要精度问题是成交量字段；若价格与官方完全匹配，不能声称供应商“价格舍入”制造了收益自相关。。证据范围：美国金融学会刊期页作者摘要。

### conditional_limits | The limits of distribution-free conditional predictive inference

重叠点：不能把某几个流动性状态的经验接近名义覆盖，写成任意条件下严格分布无关保证。。[12]

区分／限制：本项目应预先定义粗分组，报告覆盖估计和不确定性；只主张经验分组校准。。证据范围：arXiv作者摘要。

### text_fusion_2026 | Scale-aware dynamic fusion of textual and numerical information for carbon price forecasting in Chinese emissions trading markets

重叠点：政策文本融合不宜作为备选方向的独立新意。。[3]

区分／限制：观测定义、错误版本、供应商量字段与相对随机游走/校准结论，是另一估计对象。。证据范围：出版商Crossref身份元数据＋出版社索引；identity-only。

### procurement_2026 | Do Carbon Price Forecasts Improve Compliance Procurement? Evidence from European Union Allowances

重叠点：“严格信息集＋相对随机游走＋履约价值”已有近期直接近邻。。[15]

区分／限制：没有真实需求、容量和执行价时不把采购效用作为本项目主贡献；“日历报价易预测”也不等于可执行盈利。。证据范围：arXiv v1作者摘要。

### bauer_policy_2026 | Carbon Pricing and Inflation Expectations

重叠点：仅有政策日历或SHAP不能声称发现因果政策微观机制。。[38]

区分／限制：对观测定义作确定性重算可以归因于重算规则，但真实市场制度调整同时伴随经济变化，不能用简单前后差冒充其事件识别。。证据范围：Brookings作者工作论文全文。

### regional_dispersion_repository_2026 | Data and code for “Regional carbon price dispersion and national market linkages in China”

重叠点：直接反证把“跨市场口径统一、产品定义、缺失不作零、主分析不前填/前填只诊断”单独当作首次；它不是预测研究也足以否定这些步骤自身的原创性。。[27]

区分／限制：尚可检验的是全国年度配额公开综合行情的权重版本和量精度误标签，在固定日历与目标匹配RW下，对样本外相对预测和预设分组覆盖结论的影响；不把口径文档/前填诊断本身作为贡献。。证据范围：Mendeley作者一手仓库描述已直接读取；没有下载或执行压缩包，未读论文全文，未验证其统计结果。。

## 本轮近期补充核查

4条可回查的补充记录与4条未核实线索分开放在search_update中。这里仅列4条有原始页面／出版商索引佐证的记录；与上方R05有重叠，不能累加为4篇新独立论文。出版商全页可访问不代表整个实验已审查。

### U01 | Multi-step ahead carbon credit price forecasting using time series foundation models

出版商索引显示时序基础模型的多步长碳价比较，以及日/月频预测。模型数量、首发日期和实际资产定义仍待核。[48]

对选题的限制（我们的推断）：仅引入时序基础模型或长步长不是空白；须查实际资产、预训练截止与评价日是否构成时间信息污染。

范围：publisher_title_and_index_snippets; no full text retrieved。未重新取得该论文数据／代码、未复算作者指标。

### U05 | A novel interval prediction model based on LUBE and decomposition ensemble for carbon price forecasting and trading

出版商全文明确VMD、MLP/Bi-GRU及QD-LUBE区间框架，市场包括湖北、广东和全国。[35]

对选题的限制（我们的推断）：分解+深度区间+简单交易评估已有近邻；本次没有复算其收益或检查原数据。

范围：live_publisher_browser; citation_meta, abstract and introduction inspected; no empirical reproduction。未重新取得该论文数据／代码、未复算作者指标。

### U07 | EU ETS carbon price forecasting via VMGE-Net: a variational decomposition and channel-aware GRU framework

出版商索引显示已接受的早期版本，使用VMD、GRU及通道注意力；摘要报告1994个EU ETS日度观察。[40]

对选题的限制（我们的推断）：VMD+GRU+注意力结构亦有截至九月的新近邻；不得据摘要认定其时间协议、市场合约或绩效有效。

范围：publisher_index_of_reference_pdf; matches existing R05 identity; no empirical reproduction。未重新取得该论文数据／代码、未复算作者指标。

### U08 | RF-LSTM carbon price prediction based on CEEMDAN decomposition and multiscale entropy reconstruction

出版商摘要和引言明确训练窗口滚动的CEEMDAN分解—预测及RF-LSTM组合，使用湖北与EU案例。[39]

对选题的限制（我们的推断）：滚动分解本身不宜作首创；原生数据和逐预测起点的信息集仍须阅读全文核查。

范围：live_publisher_browser; citation_meta, abstract and introduction inspected; no empirical reproduction。未重新取得该论文数据／代码、未复算作者指标。

## Sources

[1] https://afajof.org/issue/volume-40-issue-1
[2] https://api.crossref.org/works/10.1002/for.70024
[3] https://api.crossref.org/works/10.1016/j.engappai.2026.115440
[4] https://api.crossref.org/works/10.1016/j.frl.2024.106560
[5] https://api.crossref.org/works/10.1016/j.jclepro.2026.149247
[7] https://api.crossref.org/works/10.1111/irfi.70099
[9] https://api.elsevier.com/content/article/PII:S0959652626017889?httpAccept=text/xml
[10] https://api.elsevier.com/content/article/doi/10.1016/j.jedc.2026.105435?httpAccept=text/xml
[11] https://api.figshare.com/v2/articles/29348171
[12] https://arxiv.org/abs/1903.04684
[13] https://arxiv.org/abs/2305.03224
[14] https://arxiv.org/abs/2402.04828
[15] https://arxiv.org/abs/2607.23426
[16] https://arxiv.org/abs/2607.23426v1
[17] https://arxiv.org/html/2402.04828v3
[18] https://arxiv.org/html/2602.03903v3
[19] https://arxiv.org/html/2607.23426v1
[20] https://arxiv.org/html/2608.17079v1
[21] https://arxiv.org/pdf/1905.07886v2
[22] https://arxiv.org/src/2305.03224v1
[24] https://data.mendeley.com/api/datasets-v2/datasets/v25wkdwgvm?fields=articles.*&version=1
[25] https://data.mendeley.com/datasets/nzsgz2h274/1
[26] https://data.mendeley.com/datasets/v25wkdwgvm/1
[27] https://data.mendeley.com/datasets/v9xpz8zb4h/1
[28] https://data.mendeley.com/public-api/datasets/nzsgz2h274/files?folder_id=root&version=1&%24start=0&%24limit=1000
[29] https://data.mendeley.com/public-api/datasets/v25wkdwgvm/files?folder_id=root&version=1&%24start=0&%24limit=1000
[30] https://econometricsociety.org/publications/quantitative-economics/2022/07/01/Uncertainty-measures-from-partially-rounded-probabilistic-forecast-surveys/supp/1634-7604-1-SP.pdf
[31] https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=33736253&retmode=xml
[32] https://iris.univr.it/retrieve/5b378998-ad22-4188-8182-6c1c9ddedd5b/BandiPirinoReno2024_ss.pdf
[33] https://link.springer.com/article/10.1007/s00521-026-11982-8
[34] https://link.springer.com/article/10.1007/s44163-026-01551-2
[35] https://link.springer.com/article/10.1007/s44176-026-00067-4
[36] https://mdpi-res.com/d_attachment/energies/energies-17-04358/article_deploy/energies-17-04358.xml
[37] https://storre.stir.ac.uk/bitstream/1893/1704/1/SEDP-2009-22-Montagnoli-de-Vries.pdf
[38] https://www.brookings.edu/wp-content/uploads/2026/03/WP106_Bauer-et-al.pdf
[39] https://www.nature.com/articles/s41598-026-35085-5
[40] https://www.nature.com/articles/s41598-026-68475-w
[41] https://www.nature.com/articles/s41599-025-05482-8
[42] https://www.nber.org/papers/w2960
[43] https://www.pure.ed.ac.uk/ws/portalfiles/portal/22161953/Ibikunle_et_al._2015_Revised.pdf
[48] https://www.sciencedirect.com/science/article/pii/S1568494626007386
[49] https://www.stat.cmu.edu/~ryantibs/papers/nexcp.pdf
