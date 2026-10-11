# 本机执行：只用已经取得的逐场数据，不下载/发布新行情

保留v8/v8.1。当前公开GitHub没有240/275逐场CSV；将既有本机压缩包解压到私有目录。不要把这些文件提交GitHub，结果输出也先本地检查再仅发布合适汇总。

1. 安装本包requirements.txt的版本；人工测试依赖statsmodels，仅用来交叉核对数值实现。
2. 从原repo `research/pro_review_20261010/full_data`（固定输入5745eb3…）生成只在本地保存的拍卖价格表：

```bash
python code/audit_auction_prices.py --input /path/to/full_data --out /path/to/private/auction_base
```

该脚本逐项核对原清单及字段；新价格研究不得复用旧训练输出。它不估计任何市场系数。默认导出表哈希为b1d737d7dc7d1af53b989560ccb13d8cad52345747441ab34f77c320edbe498f。

3. 先查新增四份CSV实际字段，完全不拟合：

```bash
python code/run_official_reported_price.py --private-root /path/to/full24 --inspect --out /path/to/private/header_check
```

程序支持四CSV在根目录或data子目录，且必须与固定哈希对应。然后由本机代理据INPUT_HEADERS.json填写 `templates/INPUT_MAPPING_TEMPLATE.json` 的实际列名、来源定位和百分号口径。不得把某列含Absolute就直接取正。八个数量字段映射用于275场全体对照；估计变量取原EEX校验值。

4. 映射和原表定义记录完成后，一次执行，不做模型选择：

```bash
python code/run_official_reported_price.py --private-root /path/to/full24 --auction-prices /path/to/private/auction_base/auction_prices_local.csv --mapping /path/to/reviewed_mapping.json --out /path/to/private/E2_results
```

5. 应得RESULTS.json、INPUT_GATE.json、PRIMARY_WCR_DRAWS.csv、PRIMARY_WCR_SIGNS.json、EXECUTION_STATUS.json。主模型为有符号报告偏差，主解释变量为投标数量报告比值；不是当前旧FULL24协议的获配SD绝对偏差模型。

预算15分钟/1100次；预定1007次；一次999抽只测试主焦点系数。逐年稳定性未另估计，不能宣称已证明稳定。所有p/CI均探索性；季度间独立近似未认证。

6. 若新CSV尚不可读取，程序必须输出BLOCKED_INPUT_OR_DIAGNOSTIC、estimates=null、real_price_model_fits=0；这是正确阻断，不生成空白占位系数0。请将真实结果文件与协议状态交给作者核对后，再使用E2_INTEGRATION_TEMPLATE_EN.md补入论文。未完成模板不能用于投稿。

本轮17个不同人工测试普通/-O分别通过；这不是新CSV解析已验收，也不是统计功效或覆盖率认证。未收到真实列名，真实数据映射链仍待验证。
