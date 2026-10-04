"""r686 bm-b: append HANDOVER five-x increment entry r676-r680 (append-only,
single entry, exact-once marker count asserted pre/post per r679 turn-replay law)."""
import io

ROOT = "research/HANDOVER.md"
marker = "bm-b round 680 五倍数核对"
txt = open(ROOT, encoding="utf-8", errors="replace").read()
assert txt.count(marker) == 0, "marker already present (r679 replay law)"

entry = """

> bm-b round 680 五倍数核对（2026-10-04 16:3x·增量窗 r676-r680 五轮·前窗 r671-r675 已由 r675 行覆盖）：增量窗 r676-r680=bm-b 面（**FUND 三族 NULLS 值守主线续窗+N1 引擎双波供给线+W3/集成收口**——r676 S6 34 腿 rc0 红腿清零〔update_lhb r675 exit2 SSL flap→refetch rc0 自愈闸兑现〕+LogonType 三源定谳律〔LoopWatchdog InteractiveToken=D-20261002-02 裁定后正典面零动作·禁按旧令字面重注册〕；r677 **N1-W116 freeze（106th engine wave·bm-b 第 39 波 owned）**〔seat MSG-20261004-1515 pre-push DELIVERED 4b0409196+r565 律+per-wave prereg DELIVERED bc1e82773+bands A 275_004..277_003/B 62_701..62_900 machine-derived ADMIT〔pre-seat probe+freeze gate 双窗恒等 hops 0/0·banned gate 0〕+anchor=W115 finalize K=250,920·net head 617,548+pf 9/9 含 §4 skip-semantics pin 腿+n1 selftest PASS W116 leg live〕；r678=死会话〔W118 freeze 五面+席位已 commit 经 daemon push DELIVERED origin〕→r679 收养收口〔MSG-1520 move 收账+簿记三写补齐+S6 38/38+引擎 W116 自燃 shard-0 done 15:56+w3-screen-1of4 in flight〕+trio watch V833/Q650/D491；r680〔本轮〕=S0 r437 预对齐净路〔pull--rebase 被 daemon 脏面阻→checkout origin pool face origin-newer-wins〔W3 shard-3 flip 在 origin〕→merge r685 bm-a 波零 UU→sync_face settle 库函数驱动 status=settled——本版本 CLI 无 sync_face 子命令=r446 落文件律驱动件〕+**D-19 双水位双键 MATCH 两连假警自捕**〔①decisions 大小写形态（wm 存大写 vs hexdigest 小写）→r503 upper() 归一正典在位②orders r458 口径律原坑复现（state 键=SHA-1 40-hex·探针首算 SHA-256=假 CHANGED·逐键 method 对齐复算 68947C17 MATCH）——两假警均探针面非正典工具缺陷〕+S6 38/38 rc0〔results/_r686bmb_s6_log.txt·ZERO-DRIFT streak 51·REPORT/LIVE-2026-10-04 再生 ORANGE cap50·四 lane-guard stale-takeover derive O-2100 s2.4〕+r643 三证零并发〔codely_in_repo=1·trio_burn_eta 16:15:51 写手=本会话 r675 探针自跑谜当场闭案〕）产物清单漂移=results/trio_burn_eta.json 逐轮刷新〔r676/r679/r680〕+results/_r67{6,7,9}bmb_*+results/_r68{0,6}bmb_{closeout,s6_chain,syncface,concurrency_probe,d19_check} 工件族+docs/daily_report/REPORT-2026-10-04.*+docs/live_usage/LIVE-2026-10-04.*〔逐轮再生件〕+results/p2cal_ext/n1_w116/shard-{0,1}-of-12.json〔W116 首两片〕；统一链 **625,977 实读平持**（live head=results/perpetual_faces/n1_w115_results.json science_gates.ledger.total·窗 +0=W116 2/12 在飞未 finalize+FUND NULLS 校准烧+MASS_TRIAL_W3 screen 波 4909/4909 complete 但 w3_screen_summary/finalize 未落〔bm-c 已声明其下里程碑〕）；池态=FUND 三族 NULLS bm-b canonical burner 在飞〔V841/Q657/D497 of 2000 @16:15·42.0/32.9/24.9pct·rates 24.3/20.5/18.0/h·ETA V 10-06T15/Q 10-07T09/D 10-08T03·finalize 候选窗 10-05 10:30..10-09·预演 r672 三族 ALL-GREEN 收据在场·finalize 轮必同窗池面双翻 r668 律〕+N1-W116 2/12 shards〔RAM floor 2.7-3.2GB<4.0GB 闸·自燃面〕+MASS-TRIAL-W3-SCREEN 四分片全 done〔4909/4909〕+W14-GENERATE 治理 park 维持+moneyflow IC next_pick claimed（bm-a 面板 source-blocked 53/5222·本机 no-op 车道）；orders 154/154 双扫零未回执全窗维持；smoke 48/48 全窗；D-19 4E5BE321（decisions SHA-256）+68947C17（group orders SHA-1）双 MATCH 全窗零消费；月度三件=10-02 已跑核验〔BRIEF-202609/SELF-REVIEW-202609/science_audit〕；指针：**V 烧完（~10-06T15）→首族 finalize 候选（三族窗 10-06..10-08·r668 池面双翻律·判词面按冻结路径如实出）+T-148 contest 终表 10-08 前刷新+O-2115/O-2030 验收 10-08+开市 10-09 数据道恢复+月界首考 10-31**；下一 5x=bm-b r685。
"""

with io.open(ROOT, "a", encoding="utf-8", newline="") as f:
    f.write(entry)
txt2 = open(ROOT, encoding="utf-8", errors="replace").read()
assert txt2.count(marker) == 1, "marker count must be exactly 1 after append"
assert len(txt2) > len(txt), "append must grow file"
print("HANDOVER increment appended; marker count == 1; delta bytes:", len(txt2) - len(txt))
