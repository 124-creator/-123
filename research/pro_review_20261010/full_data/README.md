# EEX完整实验输入

这里提供当前EEX分散度研究的完整输入，不再只是摘要。

- raw/：2020—2025年度六份原始XLSX，保留原始字节。
- parsed/candidate_dispersion.csv：全部1281场主样本，53列，保留来源文件、工作表和原行号。
- parsed/extraction_all_2020_2025.csv：筛选前全部1327条日期记录，包括其他产品和取消记录。
- parsed/row_exclusions.csv：全部46条排除记录及原因。
- parsed/raw_field_cells.json：原单元格值、位置和格式。
- INPUT_MANIFEST.json：来源文件身份、字节数、SHA256和真实数量。
- verify_data.py：逐一检查六份工作簿与导出值，检验完整筛选链。
- EEX_FULL_DATA.zip：上述输入以及两份核查报告、最新结果表的一次性下载包。

数据文件是既有原件和本次独立核查导出，不是根据摘要系数生成的模拟数据，没有截断或抽样。两份报告正文位于相邻hold_supplement目录，ZIP内另包含reports路径副本。

## 读取与核对

下载ZIP并解压即可使用。Python 3.10+和openpyxl可运行 `python -B verify_data.py`；运行目录是本目录。六份原始工作簿与完整逐场CSV同时提供，读者现在可以自行规范化字段、重算关联，不能因摘要给出1281就强行筛样本。字段名中的reported_CV只是历史代码标签，统计群体与ddof仍未知，不等于认证群体CV。

我们实际将1327条记录的13个原始数值字段逐单元格比较，共17251项比较，普通和优化模式都通过；6个XLSX和3份逐行CSV与本机来源字节一致。该检查不认证因果、创新或首次预注册。

## 来源与发布边界

数据来源标识：European Energy Exchange，EUA Primary Auction Spot年度拍卖报告。
历史来源入口（本次不作新访问声明）：https://www.eex.com/en/market-data/market-data-hub/environmentals/eex-eua-primary-auction-spot-download
用户明确要求上传当前实验完整输入，本次按该要求提供。第三方原件不因仓库代码许可而获得新的再许可；本次上传不声明EEX授予了特定开放许可，相关权利和署名保留原来源。数据中没有企业身份、个人账户、凭据或本机私人路径。

范围只包括当前2020—2025 EEX实验，不包括电脑里全部碳价资料、论文全文、无关数据或旧模型。本轮不追加实验或重选题。
