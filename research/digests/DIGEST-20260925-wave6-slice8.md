# DIGEST-20260925 · wave-6 slice-8（O-1721 常态链 · bm-a R149）

> 执行人：bm-a（OS iteration loop R149 · T-47 wave-6 · RESEARCH_MECHANISM v1.1 常态双频）
> 性质：内部研究用途，不构成采纳建议；一切外部内容未经我方门禁复验不得作为采纳依据；无登录、无绕墙、串行步速（R109 律）。

## 〇、通道实况（fetch 记账 15 次）

- PBCSF（pbcsf.tsinghua.edu.cn）：sitemap.xml 404 / robots.txt 404 / 直猜 `/kxyj/yjcg/index.htm`+`/kxyj/index.htm` 404×2（错形态·正解见下）/ 网站地图页 `wzdt.htm` 200（菜单文本确认「科学研究→研究成果」存在）/ `index.htm` anchor 提取 200（**导航解码成功：成果面正解=`/kxyj/yjcg/kyxm.htm`**）/ `kyxm.htm` 200=科研项目经费清单（非论文面）/ `lwfb.htm` 200=论文发表**年度**汇总（无逐篇 PDF 面）/ `yjyjj.htm` 200=NIFR 研究报告 16 页（产业面为主）/ **DDG lite `site:pbcsf.tsinghua.edu.cn 动量` 一发命中 10 结果（R124 梯第五例：站内路径全 404 时 site: 直搜=正道）**→ 目标 PDF `__local/F/D5/7A/66259A0664B091F2A94F23D78AD_C6E23DF5_21B1EF.pdf` 200（2.2MB·15 页·application/pdf）→ web_fetch 对 PDF 二进制不可解析（诚实记）→ 本地 requests 单取+pypdf 全文抽取成功。
- jisilu `/feed/category-5.rss` run-4：200，20 items。
- guorn.com：首页 200（社区热帖标题面复现）/ robots.txt 404 / `/community` 404 / DDG lite site: → **CAPTCHA 人机挑战墙**（bots 检测触发·不再加压·R109 节制律）。
- CJoE 退避腿：Semantic Scholar API retry → **429 三连窗**（R132 律第三次复现）。
- Bing CJK query：搅碎复现（fundsupermart 无关结果·wave-3 同坑再证）。

## 一、PBCSF 月频动量原文主源核验 ✅（本片主收获·retry 道闭项）

- **完整引文**：白颢睿、吴辉航、柯岩《中国股票市场月频动量效应消失之谜——基于 T+1 制度下隔夜折价现象的研究》，《财经研究》Vol.46 No.4（2020-04）pp.140-154，DOI 10.16538/j.cnki.jfe.2020.04.010（清华大学五道口金融学院·数据窗 2000-2016 A 股）。
- **主张核验（wave-2 在册 D6 主张逐字确认）**：①A股存在日内动量、隔夜动量、以及由 T+1 制度导致的日内-隔夜强反转关系，两者相反作用抵消总体收益动量；②T+1 下高风险股票隔夜收益率低、低风险股票隔夜收益率高（日内赢家=小市值/高IVOL/高VOL/高换手/低EP；隔夜赢家=反向低风险特征），负隔夜折价集中于高风险票=「T+1 将一天期回溯最大卖出期权嵌入 T 日收盘价」；③**新精化主张（本片新增）**：市场波动率高（低）时 T+1 约束更强（弱）、日内-隔夜反转更强（弱）、动量策略更差（好）——MOM(12,1,1) 高波动窗平均收益 **−1.33%** vs 低波动窗 **+1.27%**。
- **升级裁定**：在册 overnight_gap 族（zoo #78·OG1 预注册线）的证据注记由【wave-2 收录·原文未达】升为【原文已达·主源核验✓】；波动率条件化主张=**变体候选登记**（与 REGIME_GUARD/军种条件化路由外源同向佐证·预注册前零跑批·J18）；OG1 冻结件按律不动（其 line-19 历史注记为冻结时真值，由本片 supersede）。
- 反重复律：零新族（机制域=在册族证据升级非另立）。

## 二、DDG site: 同窗邻接种子（3 件·指针登记零采纳）

- cfrc.pbcsf PDF《聪明的贝塔：来自 A 股市场因子动量策略的实证研究》（因子动量完全解释行业动量·反向不成立）——**T-48 因子混合线（bm-b 车道）外源证据种子，只登记不碰**：`cfrc.pbcsf.tsinghua.edu.cn/__local/4/AE/67/89980D797AD790C70C6AD15BEAB_F3C5BFB8_73992.pdf`。
- PBCSF 研究简报 PDF（动量因子 5：mom12/mom6/momchg/imom/lagretn）——未来学术面种子：`www.pbcsf.tsinghua.edu.cn/__local/E/AD/3B/F24944A5ADC8089108B27D57291_3994F5E6_CBB03.pdf`。
- xyfintech 因子研究页（Hou-Qiao-Zhang 2019 A 股 426 因子筛选叙述）——学术参照种子：`xyfintech.pbcsf.tsinghua.edu.cn/yzyj.htm`。

## 三、jisilu feed run-4（常设道第 4 跑）

- 20 items 与 run-3 **完全同集：0 新 ID / 0 淌出**（三连稳态·feed 活跃度滚动窗内代谢稳定，全部 20 ID 在册面孔复核一致）。
- **工具化升级**：基线固化为机读 `results/jisilu_feed_baseline.json`（20 ID+ts），run-5+ 差分由 digest prose 升级为 JSON 对照（此前基线仅存 digest 行内）。

## 四、guorn/CJoE 诚实死面与收线

- **guorn 站内搜索面**：robots/sitemap//community 三 404（web 应用型站确认），首页社区热帖标题面公开复现（两帖方法论向：单因子组合穿越牛熊/因子月度收益），但帖子 URL 仍不可提取（markdown 转换丢 href+站内搜索面未破）——**种子维持**，后续窗换浏览器渲染面/换通道再试。
- **CJoE 同一性确认**：SS API 429 三连窗→按三窗重复失败律**收线转常态道机会性种子**；CrossRef 邻接线索（wave-4 slice-10：Liu et al. 2023 SSRN 4435622 等 3 件）仍为最佳指针；其内容主张 wave-2 已在册=收线零证据损失。

## 五、funnel 双列（O-1721 报告律·本片）

| 面 | 收割数 | 过闸数（入册/变体批） |
|---|---|---|
| PBCSF 主源核验 | 1（原文 15 页全文抽取） | 1（在册族证据升级登记·零新族）+1 变体候选（波动率条件化·预注册前零批） |
| DDG site: 邻接种子 | 3（因子动量/研究简报/426 因子页） | 0（指针登记·T-48 种子只登记不碰 bm-b 车道） |
| jisilu feed run-4 | 20 复现（0 新 0 淌） | 0（+基线 JSON 工具化） |
| guorn 站内面 | 4 试（首页✓/404×2/CAPTCHA） | 0（种子维持） |
| CJoE 退避腿 | 1 试 429 | 0（三窗收线·主张已在册） |
| **合计** | **29 收割面 / 15 fetch** | **1 证据升级 + 1 变体候选 + 3 种子登记 / 0 新族 0 采纳 0 跑批** |

采集≠入册；本片零采纳零引擎改动零跑批；主源 PDF 2.2MB 按大文件律不入 git（URL 公开可复现，抽取主张全文即本件）。

## 六、波-6 收官裁定与链

- **波-6 面账全清**：面(a) first-sweep 8 面全扫（qoppac/AA/SSRN-CrossRef/QC×2/米筐+优矿/hibor/波-6 补扫面）✅；retry 腿(b) 四面全处置——hibor 类目模式 ✅ R148 闭项 / **PBCSF 成果面 ✅ 本片闭项（原始目标=原文已获）** / CJoE ❌ 三窗收线转机会道 / guorn ❌ 种子维持；常设道(c) jisilu ✅ run-1~4+工具化。
- **T-47 闭项**：done，result_ref=本 digest+slice 链（DIGEST-20260925-wave6-slice1~8）；波-6 诚实总判定=**零新族**（外源面向「机制证据升级+死面边界勘定」倾斜=波-6 的真实收获结构，IM_IC_PAIR 新族在 wave-5 已入）。
- **波-7 预开**（链式开票禁断链·R142 范式）：T-2026-09-25-50 已开（**49 号同窗已被 bm-b composite-blend v2 票占用·R119 让号重建**；其 freeze 声明 deferred on T-47 closure+T-46 verdict=本片闭项即解锁其依赖），种子面=PBCSF 简报 PDF 深读（动量因子 5）+cfrc 因子动量全文（经 bm-b T-48/T-49 判据消费面协同·外源证据归口）+guorn 渲染面换通道重试+hibor 标题雷达常态采样+jisilu 常设道 run-5+。
