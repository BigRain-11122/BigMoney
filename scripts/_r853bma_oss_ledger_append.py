# _r853bma_oss_ledger_append.py -- append section 六 (S3/S4/S5 supplementary scan) to research/OSS_HARVEST_LEDGER.md
# Multi-writer file law: python fresh-read-append (replace-tool append forbidden per 2026-10-06 pit law).
# Evidence: results/oss_eng_scan/s345-20261008.json (rc0, 3 probe rounds, API+search dual-channel).
import io, datetime, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(REPO, 'research', 'OSS_HARVEST_LEDGER.md')
raw = io.open(P, 'rb').read()
text = raw.decode('utf-8', 'replace')
assert '六、' not in text, 'section 六 already present'

section = '''
## 六、S3/S4/S5 补扫收口（@bm-a 承接·r853·10-08 提前完成 10-09 期限）

- 取证=scripts/_r853bma_oss_s345_scan{,2,3}.py 三腿（api.github.com 直连+search API+web 搜索通道双源；聚宽社区直取=JS 渲染空 body 如实披露，改走搜索通道证据）；证据集 results/oss_eng_scan/s345-20261008.json（rc0·S3 404 两腿治愈：内存库主名过期=gplearn/gplearn→trevorstephens、mbhushan→PyPortfolioOpt org、dcajasun→dcajasn，search 实证=借力律正面执法）。
- 判据口径：license 五门（MIT/Apache/BSD 直用·GPL=REF-ONLY 弱互惠登记·AGPL 触顶退出·NONE=不可用只登记）+ 健康（star+push 新鲜）+ dup 门（在役面 akshare/tushare/own-engine 不重收；judged-out 族 MOM 0/4920/时间序 0/228/野路子 0/1569 零再准入——S5 全族=情绪族非 MOM；mom-index=宝妈散户情绪非动量，名称撞面如实披露）。

### S3（awesome-quant 漏斗甄别）

| # | 名 | 溯源 | star（API 10-08） | license | fit（首判） | 复用形态 | 成熟度 | 工时 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| S3-01 | gplearn（GP 因子挖掘） | github.com/trevorstephens/gplearn | 1,893 | BSD-3 PASS | W15 供给线候选：符号回归因子挖掘 | 取思想+库直用 | 活跃 | 8h | **准入实验候选** |
| S3-02 | PyPortfolioOpt | github.com/PyPortfolioOpt/PyPortfolioOpt | 6,078 | MIT PASS | alloc/组合线（EF/BL/HRP 经典族） | 库直用 | 活跃 | 8h | **准入实验候选** |
| S3-03 | Riskfolio-Lib | github.com/dcajasn/Riskfolio-Lib | 4,537 | BSD-3 PASS | alloc+risk（优化+风险指标族） | 库直用 | 活跃 | 8h | 准入候选 |
| S3-04 | quantstats | github.com/ranaroussi/quantstats | 7,686 | Apache-2.0 PASS | 报表/tearsheet 面（CEO 面增强参考） | 库直用（低优先） | 活跃（10d） | 4h | 准入候选 |
| S3-05 | easyquotation | github.com/shidenggui/easyquotation | 5,453 | MIT PASS | A 股实时行情备胎通道 | 通道 REF（akshare 在役 dup 面） | 221d 缓 | 4h | 登记（备胎） |
| S3-06 | FinancePy | github.com/domokane/FinancePy | 3,169 | GPL-3.0 | 衍生品定价（当前无 A 股对口面） | REF-ONLY（弱互惠登记） | 活跃 | - | 登记不直用 |

### S5（情绪因子开源实现·O-2215 REGIME-5 情绪工具供给）

| # | 名 | 溯源 | star（API 10-08） | license | fit（首判） | 复用形态 | 成熟度 | 工时 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| S5-01 | vibe-astock（A 股短线复盘看板） | github.com/simonlin1212/vibe-astock | 667 | Apache-2.0 PASS | 涨停池/连板梯队/龙虎榜/赚钱效应/晋级率/情绪周期派生指标纯计算直出 | 代码直用+数据通道核验 | 活跃 | 8h | **REGIME-5 供给候选 #1** |
| S5-02 | mom-index（宝妈指数） | github.com/mihang123/mom-index | 384 | MIT PASS | 散户情绪反向指标（民间判据形式化面） | 判据 REF | 低配 | 2h | 登记观察 |
| S5-03 | go-stock | github.com/ArvinLovegood/go-stock | 7,784 | GPL-3.0 | AI 选股终端（市场/个股情绪面） | REF-ONLY | 活跃 | - | 登记（触顶不直用） |
| S5-04 | QuantMind | github.com/qusong0627/QuantMind | 1,717 | AGPL-3.0 | AI 原生量化平台（对标 Qlib） | 触顶退出 | - | - | **退出登记** |
| S5-05 | easy_investment_Agent_crewai | github.com/liangdabiao/easy_investment_Agent_crewai | 659 | NONE | AKShare+CrewAI 多 agent 分析 | 无授权=不可用 | - | - | 登记不直用 |

### S4（聚宽/掘金社区知识·vendor registry·无 star 面）

| # | 名 | 溯源 | fit（首判） | 复用形态 | 工时 | 状态 |
|---|---|---|---|---|---|---|
| S4-01 | 聚宽因子看板（情绪类因子 taxonomy） | test.demo.joinquant.com/view/factorlib/list | A 股原生因子分类正典（情绪/动量/风格/技术族） | 知识 REF（分类学采纳候选） | 2h | 登记 |
| S4-02 | 聚宽龙虎榜营业部生态（get_billboard_list） | devpress.csdn.net/v1/article/detail/155556423 | 龙虎榜营业部维度：知名游资买入跟踪/跟随判据 | 知识 REF（在役 LHB 链增量=营业部维度） | 4h | 登记 |
| S4-03 | 掘金智能策略：涨停开板/网格 | myquant.cn/docs2/tools/ | 涨停开板=A 股原生连板情绪族新判据；网格=在役对照 | 知识 REF（判据形式化候选） | 4h | 登记 |
| S4-04 | 游资龙虎榜驱动短线（风格切换判据） | stockapi.com.cn/blog/22 | 弱势连板概率骤降/游资快速兑现/T+1 滞后三判据 | 知识 REF（情绪周期状态机判据） | 2h | 登记 |

- 首轮准入扫描清单（第一节）S3/S4/S5 全部**已扫**，5 路准入链齐（S1/S2 r846+S3/S4/S5 r853）；下一准入实验推荐排序：S5-01 vibe-astock（REGIME-5 情绪工具供给·Apache 净）> S3-02 PyPortfolioOpt（alloc 线）> S3-01 gplearn（因子供给）；达标 30% 准入门槛复核与预注册实验另开票（出场轴三选一门+同族 corr 门照旧）。
- 借力律注：外部宣称=未验证假设——以上 fit/工时为首判面，正式准入前一律走独立验证门禁链（数据口径→T+1→成本→随机基线三铁律）。

'''+datetime.datetime.now().strftime('※r853 bm-a S3/S4/S5 补扫执行体（本章 append-only，本章在册）\n')

new = text + section
with io.open(P, 'wb') as f:
    f.write(new.encode('utf-8'))
print('appended section 六; new size', len(new.encode('utf-8')), 'bytes')
