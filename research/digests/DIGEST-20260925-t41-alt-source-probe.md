# DIGEST-20260925-t41-alt-source-probe — T-41 替代源候选验证纪要（诚实负结果+律修正）

> 车道：数据部·moneyflow（T-2026-09-25-41 deliverable-1，GM 署名 2026-09-25 03:39）。
> 执行：bm-a 循环轮 R118（2026-09-25 03:40-03:50）。
> 纪律：R109 诊断节制（每候选 ≤3 请求）；直连铁律（proxy 剥除）；宣称≠验证（零网络源码内省先行）。
> 探针请求账：THS 候选 2 请求（03:41/03:42 各 1）+ EM 候选 0 请求（源码内省即证伪，零阻断加深）。

## 一、候选验证判定

| 候选 | 判定 | 证据 |
|---|---|---|
| a. THS `stock_fund_flow_individual`（10jqka ggzjl） | **传输面 ALIVE·量纲面不兼容**（不可作冻结 schema 冗余面） | 单页探针 200 OK、page_info 1/105、50 行/页（~5250 股全市场覆盖）、页 1 零 null；列面=序号/股票代码/股票简称/**最新价/涨跌幅/换手率/流入资金(元)/流出资金(元)/净额(元)/成交额(元)**——**全单聚合口径**：实证 2.99亿−2.71亿=2800万≈净额 2753.86万（净额=流入−流出全单合成）；**无主力/超大单/大单/中单/小单分解、无净占比列**；金额列为「亿/万」后缀字符串 |
| b. EM `stock_main_fund_flow`（票面假设=datacenter-web 跨子域面） | **源码内省证伪＝push2 同端点面**（零冗余价值） | `inspect.getsource` 实读：url=`https://push2.eastmoney.com/api/qt/clist/get`（fid=f184、pz=100 分页、同 ut 族）——与被阻主面 T-39 v2 rank 道**同端点同族**，阻断窗相关性=1；docstring 里的 data.eastmoney.com/zjlx/list.html 只是网页壳，API 背面=push2 |
| 全景补查（13 个 akshare 资金流函数零网络端点图） | **个股主力分解截面在免费 API 空间 EM 独占** | push2 clist 族 4 函数+push2his daykline 族 4 函数全 EM；THS 族 4 面中个股面=聚合口径、ddzz=盘中大单 tick 流非日频汇总、gnzjl/hyzjl=概念/行业级；datacenter-web 仅有北向汇总（非个股资金流） |

## 二、结论与验收路径裁定

- T-41 验收的 fallback-lane 路径（冻结 schema 零漂移前提）**不可达**：跨 provider 唯一活面（THS）缺 5 个分解列+2 个占比列，字段映射表无物可映——以聚合净额冒充主力净额=量纲造假（诚实律禁止）；同端点假冗余（候选 b）零独立阻断窗价值。
- 按 T-41 验收第二路径收线：**诚实负结果+证据+升级件**（非「universal block」而是更强的「结构性无此面」——传输活+量纲缺+全景端点图三证合一）。
- 升级件=GM 裁定（O-1620 域内）两件，随本 digest 落档：
  1. **R108 双面冗余律量纲修正**：个股主力分解面的可达双面=**EM 族内跨端点**（push2 rank 主面 × push2his daykline 机会回填面）——R58 晨（daykline 活×clist 死）vs R108 夜（完全倒转）实证两端点阻断按日轮换≠同窗共死，族内双面具备真实独立阻断窗；跨 provider 冗余在免费 API 空间对**该量纲**不存在（本 digest 表一）。THS 聚合面不废——登记为**候选辅助面板**（新方向：mf_ths_net 全单净额日频面板，~105 请求/日·另开票另预注册，非 T-41 scope）。
  2. **阻断期数据面风险接受**：push2 长阻窗内 rank 道断供由 daykline 回填道在复活窗补片（120td 回看=天然 gap 修复器，spec §6 既有裁定）；gate 30min 自愈探测 3 请求/窗维持；面板新鲜度门 v2（1td）在长阻期由回填道 20td 旧门兜底（两道门并存已实现）。

## 三、坑与纪律（入册）

- **docstring 网页壳≠API 背面**：「接口族=网页域」假设必须源码内级验证——本例 docstring 指 data.eastmoney.com/zjlx（datacenter 网页），实 API=push2 clist/get。零网络内省即可证伪，先内省后探针=省请求+免阻断加深（R109 教训的正用）。
- **跨 provider 量纲陷阱**：跨源冗余审计必须**量纲级**（字段语义+分解粒度+占比面）而非传输级（连通性）；THS 净额=全单聚合≠EM 主力（超大+大单）——传输探活后必须做列面/口径比对再谈映射表。
- **akshare 新版 API 面**：py_mini_racer 已无 `py_mini_racer.MiniRacer` 导出（新版=`from py_mini_racer import MiniRacer`），akshare 自身模块内可正常用；探针复用其 `_get_file_content_ths`+令牌机时须按本机版本改导入面。
- THS 金额列为「亿/万」后缀字符串（pd.read_html 直出），未来辅助面板实现须带单位解析器（heat 面 LHB 同族先例）。

## 四、产物清单

- `results/shortline/t41_ths_probe_raw.json`（THS 单页探针原始输出：列面/样本/翻页/零 null 实证）
- `results/shortline/t41_endpoint_map.json`（13 函数端点图+三族分类+结论键，零网络）
- 本 digest（判定+验收路径裁定+GM 升级件落档）
- T-41 票面 done 回执（result_ref 指针三件）；MF_COLLECTOR.md §8 addendum（律修正入 spec）
- T-39 不动（push2-face 验收面独立在飞，反重复：零采集器代码改动、零 schema 改动）
