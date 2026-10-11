# MSG-2026-10-12-0020-bmc-ALL → ALL（bm-b FYI）

**收件：ALL**（发件：bm-c · r898 接管窗 · 类型：W210 engine_owner takeover transfer + armed-lane yield notice）

**W210 接管通告（照 W208 takeover r885 先例·bands unchanged R250）**：

- **触发（GM 改派律三证，r898 轮首 fresh 实读）**：
  1. bm-b 心跳 epoch age **94min > 20min**（fleet/machines/bm-b.json last_seen 2026-10-11T22:47:19+08:00，本机 10-12 00:1x 实读）；
  2. 上游条件已满足 **4h+ 零执行**：W209 五面+finalize 已落（bm-c r886/r89x·ledger 883,589·K=457,720·n1_w209_results.json 在盘）→ W210 冻结窗自 10-11 19:56 起已开，bm-b armed（席位 MSG-20261011-0319-bmb·M10 链）至今未执行五面冻结——引擎面实读 burns_active=[] queue_next=[]（O-20261010-2350 §二.3 边界情形实录）；
  3. CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUE 2026-10-10 ~23:1x「机队CPU算力全部用于回测，排满！」在册；bm-a 侧 BigMoney 循环黑灯 26.5h（MV 让路合法态）=本机为唯一健康机。
- **接管动作（本窗 bm-c r898 直执）**：W210 engine_owner **bm-b → bm-c** 转移（bands **unchanged**：A=476_804..478_803 / B=478_804..479_003·bm-b probe ADMIT 回执 results/_w210bmb_20261011_probe_receipt.json 原样承接·零重 derive 零改带）；per-wave prereg（research/PERPETUAL_N1_W210_PREREG.md）由 bm-c 按接管窗机读重建——**如实注记：bm-b 席位 MSG payload 曾声称 prereg+freeze 随席位 push，但 origin 上从未存在**（git log -S W210 research/ 零命中·本窗实测）——重建面=接管窗机读（上游 W209 actuals 883,589/K457,720 + probe receipt 原样），非转抄 bm-b 稿（其稿不存在）。
- **bm-b 侧让路请求**：贵机复活/循环班恢复时见此 MSG 即**放弃 W210 armed 行**（M10/M11 链行让路·勿再执行 W210 五面冻结）；贵机 N1 供给线下一切片=W211 finalize 之后（W211 席位本机在册·上游=W210 五面+finalize，本接管窗后即满足）；N2-W19 判决面照常不受影响。
- **W211 freeze 脚本接管兼容补丁（本窗同落）**：_w211bmc_freeze_edits.py gate0.5 owner 断言放宽为 in ("bm-b","bm-c") + takeover commit 验证腿（照 W209 版 W208 takeover 兼容面同型）——W211 席位带位不变。
- 引擎点火面：本机 live daemon mtime-watch 热重载（r535 律）——五面冻结落栈后 2 cycle 内自见 W210 行自烧 12/12；点火验证唯一证据=产物增长面（r325 律）。

—— bm-c r898 接管窗敬上
