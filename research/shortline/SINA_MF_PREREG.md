# SINA_MF_PANEL — sina 个股四档资金流前向采集候选 PREREG（FROZEN·T-2026-09-26-72）

> 状态：**FROZEN**——冻结时点=采集器实现票 T-2026-09-26-72 认领（2026-09-26 04:33 bm-a R217，T-43 THS 先例：票认领→prereg 冻结 commit→实现）；冻结后判据/护栏/schema 禁看结果改线，open items（§5）按注记路径收口不改语义。
> 注册链：R212 候选登记（clist 路径族阻断 27h+ 触发）→ R215 三面探针（活性/量纲/深度，
> 新鲜度 UNDETERMINED）→ **R216 新鲜度证伪=FRESH**（双股日期序非掩膜读数穿透至 2026-09-24）。
> 证据：DIGEST-20260926-r215-t71-sina-mf-probe.md + DIGEST-20260926-r216-t71-sina-mf-freshness.md
> + results/_r215_sina_mf_probe.json + results/_r216_sina_mf_freshness.json。
> 车道：MF_COLLECTOR §8 族跨源双面候选；本件=数据车道 prereg，**零回测零引擎**（T-67 纯采集同律）。

## §1 候选面（byte-honest，全部来自实测响应）

- **端点**：`vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_qsfx_lscjfb`
  （直连 urllib 配方＝update_futures/T-69 同源先例；R215/R216 六请求全 200，73-640ms）。
- **个股面**：`daima=sh600519` 必填（列表/排行面缺席：R215 r1 无 daima=Input error 实证）
  ⇒ **rank 车道替代不在此面解决**（T-39 自愈道不变，本候选=分解量纲的跨 provider 冗余面）。
- **字段**（冻结 schema，原样 ASCII）：`opendate, trade, changeratio, turnover, netamount,
  ratioamount, r0, r1, r2, r3, r0_net, r1_net, r2_net, r3_net`（14 列+股票代码列）。
- **排序面**：`sort=opendate&asc=0` 实测有效（行严格日期降序，R216）＝新鲜度/回看读数的合法面；
  `sort=netamount` 掩膜陷阱禁用于任何覆盖率/新鲜度结论（R215/R216 双实证）。

## §2 量纲与诚实律（R118 律——本候选的核心纪律）

- sina r0..r3=**sina 自有四档分解**：API 面不含档位阈值文档（folklore 称其阈值与 EM 超大/大/中/小
  不同源）⇒ **禁映射到 EM 主力语义、禁冒充 EM 主力净流入替代列**（量纲造假禁行）。
- **自洽律**（采集器入账硬校验）：`netamount == Σ(r0_net..r3_net)` 浮点精确（R215 百行 worst
  4.77e-07；R216 当日两行再验证）——违者该行拒绝入账诚实计数。
- **r3 结构零**：高价股 r3≈0 为结构性（600519 实证）非死列（601398 非零反证）；禁丢弃禁造数。
- **隔离律**（THS 分件分库先例）：独立目录 `data/sina_mf/`、独立 spec 节，**禁与 EM 面板混读混 join**；
  消费面把 `sina_tier*_net` 当独立因子族（与 EM mf 列的相关性=实证问题非假设）。

## §3 经济与车道设计（采集可行性）

- **逐股请求经济**：5222 股 × 1 请求；每请求带回 `num` 行日期降序史（num=100 实测可用；
  num 上限 R220 实测 ≥2500td——收口注记见 §5①）⇒ **回看窗≥100td** ≈ EM daykline 120td 同级
  ⇒ 定位=**回填/gap 修复面+跨源冗余面**，非每日前向面（5222 请求/日违 EM 公民义务先例，禁）。
- **刷新门**（镜像 daykline 道）：面板 cutoff 落后最近完整 bar 日 **20 交易日** 或首拉/未完成 →
  分离后台全宇宙刷新；新鲜 ⇒ 零网络 no-op。月度级全宇宙重拉 ≈5222×2.5s≈3.6h（§1 MF_COLLECTOR 同计）。
- **护栏**（update_futures 同族全套）：15:30 完整性守卫（前丢弃当日行）＋本地 ETF 交易日历日期自戳
  ＋同日幂等（date 已在→字段 tol 比对跳过）＋overlap 逐行校验失配行本地不动＋2.5s 全局限速
  ＋连接级 3 连熔断停发（30min 自愈窗）＋checkpoint 断点续拉＋30min spawn 节流＋DETACHED 无窗口
  ＋车道归属护栏=**仅 bm-a 动作**（R31 判例）他机 stdout-only 诚实 no-op。
- **退出码契约**：gate 0=正常/no-op/刷新在途、2=机制故障；refresh 分离进程 0=全宇宙完成、
  2=未完成（checkpoint 保全）、3=完成但有 overlap 失配——2/3 原样上报勿掩盖；selftest=离线自检。

## §4 验收判据（机器可验，采集器票冻结时点生效）

1. 全宇宙首拉后：覆盖 ≥5000/5222 股、每覆盖股含最近完整 bar 日行（coverage 报告如实；
   非宇宙成员/skipped 逐类计数诚实披露）。
2. 自洽律全面板零违例（违例行不入账、计数披露）。
3. 同日重跑幂等（字节级零增长）；overlap 边界行校验通过。
4. selftest 离线全绿（守卫/幂等/熔断/日戳四节先例面）。
5. 请求预算实弹计数入账（首拉 5222 内；后续窗 3 探针/30min 同 T-39 范式）。

## §5 open items（实现票首拉时收口，诚实标注）

- num 精确上限 → **R220 已收口（FROZEN-at-lower-bound）**：实测 num=600→600 行（2024-04-09..2026-09-24）、
  num=2500→2500 行（2016-06-06..2026-09-24，~10.3y），自洽律全行精确（worst 4.77e-07）；
  ceiling ≥2500td 超一切实用回看需要 ⇒ 冻结面=单请求回看窗实用无上界（≥2500td）；**本面板采集器
  num=100 冻结行为不变**（首拉在飞/判据面零改）；深史重拉（num=2500 级）=未来 prereg 修正案选项
  （5222 请求预算面另注），非本票面。请求记账：2 探针请求（r600+r2500，purpose=num freeze，
  预算面=首拉实测测量请求，非日常窗 T-39 探针节流面）。证据=results/_r220_sina_mf_num_probe.py
  + results/_r220_sina_mf_num_probe.json（bm-a R220，date-sorted 读数 R216 律）。
- `fenlei` 参语义未测（R215/R216 恒 fenlei=1 与 folklore 配方一致；保守沿用，禁擅自变更）。
- 档位阈值官方文档（sina 页面 JS/帮助面）→ 外源扫描常态线下批收口（O-1721）；
  收口前消费面档位语义=UNDOCUMENTED 诚实标注。
- 采集器实现票=另开 GM 署名单（P1 数据源扩容，O-1620 下放面；T-43 先例流程）。
