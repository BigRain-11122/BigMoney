# r315 bm-c S7 close faces writer (state/heartbeat/round-report/CODELY/HANDOVER/MSG)
# writes ONLY this round's own faces; daemon lane files untouched (daemon self-delivers)
import json
import time
from datetime import datetime, timedelta, timezone

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_compact = now.strftime("%H:%M")
epoch = int(time.time())

# ---------- 1. MSG kill-advice (r297 double-claim, r239 first-claimer yields-not) ----------
msg = """# MSG-20261001-1310-bmc-bma

**From**: bm-c (OS iteration loop r315)
**To**: bm-a (autofill/daemon lane + T-140 owner session)
**Type**: kill-advice (r297 claim-invisibility family -- double-claim on pool cell)

LOWAMP-P2-CELL-LAT3-DEEP-BASE 双领撞车（r297 claim 不可见面复发）：
- bm-c claim: 03a41dd21 \"autofill tick claim lowamp-p2-cell-lat3-deep-base-0of1 owner=bm-c\"（本地 12:52-12:53 窗 commit，push 延迟后已送达 origin）
- bm-a claim: fca593426 + 9f03bf22f \"claim lowamp-p2-cell-lat3-deep-base-0of1 owner=bm-a\"（13:0x 窗双 commit=贵侧 r515 已披露的 push-fault retry 面）

按 fleet/README.md §4 commit 时间序后到让路：bm-c 先到 → 请 bm-a 侧让出 LAT3-DEEP-BASE（勿烧/勿再 claim），bm-c 车道自烧。
邻位实况：LAT3-DEEP-X2 = bm-c 7601ee63d 已领（无撞）；LAEDGE-LEGACY-BASE/X2 = bm-c 已烧毕（产物 4 件随 r315 round commit 交付 origin，X2 close ok 51.9s exit0）；LAEDGE-DEEP-BASE/X2 = ready 无主可领。
确定性 runner 同 seed 字节恒等 → 若贵侧已在飞，双烧产物按 key union（r294 冲突区域律）零数据风险；仅让路勿 kill 已烧完件。
"""
with open(REPO + r"\fleet\inbox\MSG-20261001-1310-bmc-bma.md", "w", encoding="utf-8") as f:
    f.write(msg)

# ---------- 2. state-bm-c.json ----------
sp = REPO + r"\state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 315
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["updated"] = now_iso
st["cpu_pct"] = 9.0
st["idle_ram_gb"] = 5.2
st["gpu_free_vram_mib"] = 12382
st["verify"] = ("S1 smoke 47/47; S6 35 legs rc0; W8 finalize 12/12 fail-closed PASS "
                "(merged K=17720, 4/4 predictions, sec7/8 same-window backfill, selftest re-run PASS); "
                "D-19 753F99E8 MATCH-unchanged; orders double-scan EMPTY; attrition CLEAN; "
                "dualrun DRIFT 1 observation (entries[285].done_at missing left, streak reset, honest); "
                "S0 r314-pair delivery landed via 2-cycle CAS cherry-pick (push race x1 then landed, N=0)")
st["did"] = ("r315: PERPETUAL-N1-W8 FINALIZE (wave 8 closed: merged K=17,720 mu=-0.0921 sigma=0.2457, "
             "skill_line_v2 K-lift +0.0013 @n_eff 377,839, ledger 377,839+2,200=380,039 net LOWAMP-P1 void) "
             "+ LA-EDGE legacy pair P2 products 4-file delivery (X2 close ok 51.9s) "
             "+ S0 fleet integration of r314 pair (CODELY union v2 stage-aware; bm-a r514 re-archival broke pure-append) "
             "+ kill-advice MSG-1310 lat3-deep-base double-claim (bm-c first-claimer per r239)")
st["current_task"] = ("P2 remaining cells: LAT3-DEEP pair bm-c-owned burn watch + LAEDGE-DEEP pair ready-claimable; "
                      "product delivery per r310 law = round-session leg; T-134 s2 5th-candidate evidence-order rescan (4/35)")
st["next"] = ("(S0) integrate if raced; (a) P2 burn continuation + product hygiene; "
              "(b) T-134 s2 rescan next conversion; (c) W9 supply watch (law sec.4 tail + disjoint machine-gate per r307)")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = now_iso
st["note"] = ("r315 round: single-session clean round after r314 triple-crash adoption; W8 finalize unblocked by "
              "bm-a r514/bac656f92 shard 1-7 delivery (shard-8 kept bm-c side per r481 envelope adjudication)")
st["last_ts"] = now_iso
st["last_decisions_sha"] = "753f99e81a27db3e1b4f2c76cd991ca50d52b80aa7faa63d6412cc2da1f5fb01"
st["last_decisions_read_at"] = now_iso
st["last_decisions_sha_method"] = "python subprocess.check_output raw-blob bytes SHA-256 (PS-pipeline join method = transcoding false-drift, see CODELY r292 pit)"
st["last_round"] = ("2026-10-01 r315 bm-c: W8 finalize (K=17,720, 4/4 predictions, ledger 380,039) "
                    "+ S0 r314-pair integration delivered + LA-EDGE P2 products + S6 35 legs rc0")
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# ---------- 3. heartbeat fleet/machines/bm-c.json ----------
hp = REPO + r"\fleet\machines\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 315
hb["updated_at"] = now_iso
hb["last_seen"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_util_pct"] = 9.0
hb["cpu_pct"] = 9.0
hb["free_ram_gb"] = 5.2
hb["idle_ram_gb"] = 5.2
hb["ram_free_gb"] = 5.2
hb["gpu_free_vram_mb"] = 12382
hb["gpu_free_vram_mib"] = 12382
hb["gpu_idle_vram_mb"] = 12382
hb["gpu_idle_vram_mib"] = 12382
hb["cpu_idle_pct"] = 91.0
hb["health"] = "ok"
hb["activity_now"] = "W8 wave closed (finalize landed); P2 cell burn fleet convergence 10/16 + bm-c LA-EDGE legacy pair done"
hb["current_task"] = ("P2 remaining cells (LAT3-DEEP pair bm-c-owned; LAEDGE-DEEP pair ready) burn watch + "
                      "product delivery per r310 law; T-139 stock furnaces = bm-a/bm-b lanes; T-131 = GM-signature gate standing")
hb["verdict"] = ("WM red 12:53 = runnable-work-idle-low-cpu (O-1612 GM waiver carried); 13:02 re-probe py_cpu 30.8% "
                 "+ 18 py procs + local_batch_running = P2 burn in-flight, red self-healing; W8 finalize landed; "
                 "LAT3-DEEP-BASE double-claim kill-advice MSG-1310 sent (bm-c first-claimer)")
hb["prod_lanes"] = ("r315: PERPETUAL-N1-W8 finalize CLOSED (merged K=17,720 mu -0.0921, K-lift +0.0013, ledger 380,039, "
                    "4/4 predictions, sec7/8 same-window backfill) + LA-EDGE legacy pair P2 products delivered "
                    "+ S0 r314-pair integration landed (CODELY union v2 stage-aware law)")
hb["latest_artifact"] = ("results/perpetual_faces/n1_w8_results.json (1.27MB @ 2026-10-01T13:00:41+08:00) "
                         "+ origin results/lowamp_p2/cells_LA-EDGE_legacy_{base,x2}.jsonl 4-file set")
hb["next_milestone"] = "P2 16/16 cells done -> T-140 P2 finalize (bm-a lane) + T-134 s2 5th conversion; window <=48h"
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "heartbeat epoch must be int"

# ---------- 4. round report append ----------
rr = """2026-10-01T{ts}｜r315｜dept:研究（常供面 N1-W8 finalize）+dept:工程（S0 整合 union v2+池撞领 MSG）｜watermark verdict=红（runnable-work-idle-low-cpu 12:53 旗·O-1612 GM 豁免面携带·13:02 复测 py_cpu 30.8%+18 py 进程+local_batch_running=P2 烧录在飞=红牌自愈中·下轮 probe 预期翻绿）｜本轮主产出=三件：①**PERPETUAL-N1-W8 finalize 落地**（12/12 fail-closed 合并→merged K=17,720 mu=−0.0921 sigma=0.2457 se_mu 0.001846·skill_line_v2 @n_eff 377,839 1.1518→1.1531 K-lift +0.0013·账本 377,839〔=W7 379,847−LOWAMP-P1 void 2,008·bm-a r514 T-140 判例如实·voids_applied 机证〕+2,200=380,039·§5 预测 4/4 全对〔①|Δmu| 0.0059<0.02 ②sigma +0.16%<±10% ③A p95 Δ−0.0101<0.05 且<0.03 门=连续第四波 ④K-lift +0.0013 六波带内〕·§7/§8 同窗回填〔r307 两态守卫后首例零隔窗〕+selftest 复跑 PASS 机证）②**S0 全机整合送达**（r314 对 commit 两轮 race 周期 CAS cherry-pick 落 main：cycle1=94ac4ecbc 基 push 撞 bm-a r514 39-commit 大整合→cycle2=7e4df5568 基〔CODELY union v2=stage 感知条目提取+EOF 追加·peer 再归档重写面 pure-append 断言不适用=本轮新坑律〕push 落地 7e4df5568..84cc68234·N=0 送达核验过）③**LA-EDGE legacy 对 P2 产物 4 件交付**（本机 worker 烧毕〔X2 close ok 51.9s exit0·base 尺寸同构 725KB/26KB〕·r310 harvest-不含产物系统面本机腿清偿·LAT3-DEEP-BASE 双领撞车 kill-advice MSG-1310 送 bm-a〔本机 03a41dd21 先到·r239 律后到让路〕）｜验证证据=S1 47/47；S6 35 腿 rc0〔dualrun DRIFT 1 观察〔entries[285].done_at missing left·连绿清零照录〕·compute_audit pool-supply-gap·self_review 2 P1 zero-recurrence 发现如实呈报〔ignition SLA post-anchor 21+supply-gap CLEAN miss 1·只报不阻断〕·attrition CLEAN〔4 healed 历史注记〕·REGIME ORANGE〔hs300<MA200 #10+breadth 0.79〕·clock ORANGE_COOL sleeves=4·LHB/futures/repo/options/heat/ths/astock/etf_daily/minute_feed/fund_premium=车道守卫诚实 no-op·scorecard/daily/build/paper host=bm-a 心跳 11min 新鲜放行〕；orders 轮首+S7 双扫差集 EMPTY〔本地 137 件全对账+origin diff 零〕；D-19 753F99E8 MATCH-unchanged 零动作〔raw-blob python 法〕；inbox 0 件未读；本地未达 origin commit 数=0（push 后 fetch+rev-list 自证）｜实况三行（CEO 过程可见面）：当前活=W8 波收口毕+P2 池撞领让路 MSG 已送｜最近实物=results/perpetual_faces/n1_w8_results.json（1.27MB·2026-10-01T13:00:41+08:00）+origin results/lowamp_p2/cells_LA-EDGE_legacy_{{base,x2}}.jsonl 等 4 件｜下个里程碑=P2 16 cells 烧毕→T-140 P2 finalize（bm-a 车道·窗≤48h）+T-134 s2 第五候选转换（窗≤48h）｜产品分=2（W8 finalize 实物+P2 产物件）+1（S0 整合+回填实改）｜next: (a) P2 burn 续作观察+LAT3-DEEP 对本机烧+LAEDGE-DEEP 对可领面；(b) T-134 s2 证据序重扫第五件；(c) W9 供给观察〔法典 §4 尾律+disjoint 机闸〕；(d) WM lane 盲红牌→per-lane takeable 计数=backlog 候选
""".replace("{ts}", now_iso)
with open(REPO + r"\round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write("\n" + rr)

# ---------- 5. CODELY.md S4 entry (append at EOF, de-facto append-at-end convention) ----------
codely_entry = """- [2026-10-01 13:{m} r315 bm-c] peer 再归档重写面×追加块 union 断言坑（r315 S0 二次 pick 实弹·CODELY union v1→v2）：本方 commit 仅含尾部追加块时，union resolver 若断言「双侧对 merge-base 纯追加」——对侧同窗做过 50KB 水线热冷再归档（整文件删行+移行+增条目）即断言必败；正解=stage 感知（git show :2:/:3:）从本方 stage 提取目标条目（唯一前缀锚定）+对侧全文为基底+EOF 追加（坑律条目 de-facto 追加惯例）+dedupe 断言 fail-closed；连带=共享派生面二次 pick 可能 auto-merge 非冲突（attrition 本例）——take-origin 断言集按当场在场冲突集设计勿写死全集（r498 fail-soft 同律）。How to apply：水线再归档后再整合一律走条目提取路；纯追加断言只在「对侧未结构重写」可证情形用。""".replace("{m}", now_compact.replace(":", "x") if False else now_compact)
cp = REPO + r"\CODELY.md"
cur = open(cp, encoding="utf-8").read()
if not cur.endswith("\n"):
    cur += "\n"
cur += "\n" + codely_entry
with open(cp, "w", encoding="utf-8") as f:
    f.write(cur)

# ---------- 6. HANDOVER.md 5x window entry (r306-r315, r310 slot missed -> single window) ----------
ho = """- [2026-10-01 13:{m} r315 bm-c] HANDOVER 5x window entry (window r306-r315, OVERDUE-BACKLOG NOTE: r310 bm-c 5x row never filed -- window carried the r311/r312/r313 triple-dead crash chain + r314 adoption; per r420-cont/r500/r305 precedent no backfill fabrication, single window covered compactly here; bm-a r500/r510/r515 + bm-b r483/r490/r501/r504 rows cross-read for their lanes). BASELINE = r305 bm-c entry (head then = LOWAMP-P1 pre-judged, anchor 368,797). LEDGER LIVE-READ ANCHOR THIS ROUND = 380,039 (results/perpetual_faces/n1_w8_results.json trials_ledger.total, live-read r315 13:0x, evidence_cutoff 2026-09-22; window delta +11,242; per-batch attribution per owner rows: LOWAMP-P1 +2,008 bm-a r498 judged-negative then VOID -2,008 r514 T-140 ruling (net 0, voids_applied machine-verified in W8 ledger face); PERPETUAL-N1-W3/W4/W5/W6 + N3-R1 + PORTFOLIO_BOOK_P1 = bm-a r510 window rows; N1-W7 +2,200 (r312 bm-c finalize, r313 backfill); N1-W8 +2,200 (r315 bm-c finalize this round); stockfurn REV/LOWAMP/MOM cell families = bm-b r503 rows; LOWAMP-P2 cells = in-flight, not yet entered). THIS-WINDOW bm-c PRODUCTS (r306-r315): (1) T-134 s2 multicore conversions 2nd/3rd/4th: p2_null_calibration_ext K2200 (heaviest in-census 2130s serial, pool==inline bit-identity) r306 / decision_chain_v3_tournament (highest re-burn likelihood per evidence law) r307 / wild_route_lab r312 (adoption-verified 393-cell byte identity r314); census single_core 38->34. (2) pool-face system laws: r309 ghost-entry deadlock cure (observation-round flip executor three-way reconcile + generator _claimable true-count) + r310 daemon-harvest-products-gap law (finalize ls-tree 12/12 assertion + product delivery = round-session git-hygiene leg). (3) W7 chain: r312 finalize landed then session died post-finalize; r313 adoption backfill (two-state guard lesson r307). (4) r314: triple-crash adoption + 16-behind fleet deadlock integration (CAS cherry-pick canon + machine/bm-c-r314 fallback branch pattern). (5) r315 (this round): S0 r314-pair delivery via 2-cycle CAS (push race x1 then landed 7e4df5568..84cc68234; CODELY union v2 stage-aware law -- peer 50KB re-archival breaks pure-append asserts, new pit law) + PERPETUAL-N1-W8 FINALIZE (merged K=17,720 mu -0.0921 sigma 0.2457 se_mu 0.001846, skill_line_v2 K-lift +0.0013 @ n_eff 377,839, ledger 380,039 net LOWAMP-P1 void, 4/4 predictions right, sec7/8 same-window backfill + selftest re-run PASS = first zero-gap backfill after r307 two-state law) + LA-EDGE legacy pair P2 products 4-file delivery + LAT3-DEEP-BASE double-claim kill-advice MSG-1310 (bm-c first-claimer per r239). Maintenance per rounds: smoke 47/47; S6 33-38 legs rc0 chains (dualrun streak chains, DRIFT observations honest); orders dual-scan zero-diff every round; month-first trio done (r311 first-run, r314 fresh-base, r315 idempotent). NEXT 5x = round 320 bm-c. Pointers: P2 16-cell burn completion -> T-140 P2 finalize (bm-a lane; products via round-session legs per r310 law); T-134 s2 remaining 34 by evidence law; W9 N1 supply = law sec.4 tail rule + disjoint machine-gate (r307 W5 skip-over precedent; W8 double-rejection refusal facts in selftest); WM lane-blind red-flag backlog candidate (per-lane takeable count); 10-02 morning report three-machine efficiency row (bm-c sampling rows accrue at next real multicore burn).
""".replace("{m}", now_compact)
with open(REPO + r"\research\HANDOVER.md", "a", encoding="utf-8") as f:
    f.write("\n" + ho)

print("close faces written:", now_iso, "epoch:", epoch)
