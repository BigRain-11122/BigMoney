import json, time, subprocess, os
repo = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = time.time()
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(now))

# --- 1. round report append (bytes-level, CRLF-tail preserve) ---
rr = os.path.join(repo, "round_reports-bm-c.md")
line = ("2026-10-02T02:5x:00+08:00｜r344｜dept:研究（W41 冻结+同窗 12/12 烧毕）+dept:工程（r343 遗产补交付 S0 整合）+dept:舰队（T-143 认领）｜watermark verdict=绿（red=false·probe py_low_with_work_cands=T-131 网络采集在飞+W41 引擎波烧毕后的合法工作面·板 0 open·bars 假期无新 bar）｜S0: r343 宣称-实况背离定谳并补交付——n1_w39_results.json（W39 finalize 产品·活链头 448,340 物理载体）与 LA-EDGE legacy_x2 cells+cont（LOWAMP-P3 13th cell·grid 15/16 缺位件）均为 untracked 唯一副本从未上 origin（log --all 空）·prereg s7/s8 回填同样滞留——CAS 外科 payload 清单漏主产品件（r310 外科面变体·已入 CODELY 坑律）；定向 commit 11 件 2965+（dee8469f3 前身 e486590fc）+rebase 撞 pool_core_samples UU 冲突按 r294 域律 union 解（origin 6 行+本机 2 行 ts 序·字节级行尾保持 42 CRLF）+r501 净路过假拒绝（commit -C 手工落 pick+quit+update-ref）+送达核验 ls-tree blob 恒等全绿。MAIN PRODUCT: W41 FREEZE 第三十一枚引擎波 bm-c 第十枚自有波（first-free-number after bm-b W40·A 125_004..127_003/B 43_401..43_600 双侧算术零跳位==W40 行 W41+ 公示投影·ADMIT 回执 _r344bmc_w41_band_gate.py leg0-leg3 全过含 N3-R1 腿+探针簇腿+origin 号位净空·banned_direction_gate ADMIT·selftest PASS 含 W41 材料面腿+PASS 串·prereg 锚=W39 实测·K 投影 88,120/链头投影 452,940）+引擎 per-tick 重读抢跑点火（commit 前 shard-0/1/3 已落盘=D-20261002-03 修法自然行为·确定性律恒等）+冻结 commit 764a377af 后 12/12 烧毕同窗闭环（比 W39 更快：冻结→烧毕一窗）·finalize 链序待 W40（bm-b 烧录在飞）FAIL-CLOSED。T-143 月考准备票认领（accounts face=bm-c primary·deliverable 10-29·prep-only）。S6 链全绿 rc0：dualrun ZERO-DRIFT streak 29/3·compute_audit 两旗如实记（cap_violation=W41 烧录窗瞬时 97% 采样·supply_floor=池 ready 1/3）·regime ORANGE·market_clock ORANGE_COOL·scorecard/paper_export/daily_scorecard/build_status 四件 stale-takeover 合法（bm-a 心跳 63-65min>O-2100 20min）·attrition CLEAN·b_layer 4 门 PASS·token L2 0·S1 smoke 47/47·orders 差集 0/143·D-19 MATCH。本地未达 origin commit 数=0（收尾后核）｜下轮指针=(r345) W41 finalize 待 W40 落账（bm-b 道）+LOWAMP-P3 E1 四腿（16/16 已齐）+T-134 s2 p1e_synth+T-131 liveness+T-143 accounts face 起步\n")
raw = open(rr, "rb").read()
if not raw.endswith(b"\n"):
    raw += b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
nl = b"\r\n" if raw.count(b"\r\n") * 2 > raw.count(b"\n") else b"\n"
open(rr, "ab").write(line.replace("\n", nl.decode("ascii")).encode("utf-8"))
print("round_report appended")

# --- 2. CODELY pit entry append ---
cl = os.path.join(repo, "CODELY.md")
pit = ("- [2026-10-02 02:5x r344 bm-c] 外科推送 payload 清单漏主产品件坑（r310 族外科面变体·r343 遗产实弹）：r343 宣称「W39 finalize same commit」「13th cell delivered」，实况=n1_w39_results.json（活链头 448,340 物理载体）+LA-EDGE legacy_x2 cells/cont（grid 15/16 缺位件）+prereg s7/s8 回填全为 untracked 唯一副本从未 commit——CAS 外科推送只推 10 件列名 payload（主产品件不在清单）+daemon harvest flip 只翻池面不含产物件（r310）=双面叠加漏交付，W41+ finalize 链序消费面险崩（r540 族）。修法=r344 S0 定向补交付 11 件+送达核验三面。How to apply：外科/commit-tree 推送 payload 清单必含 finalize 产品件+prereg 回填（主产品优先级最高）；轮收尾宣称 delivered 前必 git log --all -- <产品件> 自证 commit+push+fetch ls-tree 送达三面（宣称-实况一致律的机证面）。\n")
raw2 = open(cl, "rb").read()
nl2 = b"\r\n" if raw2.count(b"\r\n") * 2 > raw2.count(b"\n") else b"\n"
if not raw2.endswith(b"\n"):
    raw2 += nl2
open(cl, "ab").write(pit.replace("\n", nl2.decode("ascii")).encode("utf-8"))
print("CODELY pit appended")

# --- 3. state-bm-c.json update ---
sp = os.path.join(repo, "state-bm-c.json")
st = json.load(open(sp, "rb"))
st["round_no"] = 344
st["last_round_at"] = "r344"
st["last_round_ts"] = now_iso
st["updated"] = now_iso
st["last_seen"] = now_iso
st["last_round"] = "2026-10-02 r344 bm-c: r343 carry rescue (W39 finalize product + LOWAMP-P3 13th cell delivered, 15/16->16/16) + W41 FREEZE + 12/12 same-window burn + T-143 claim + S6 chain"
st["did"] = "r344: S0 carry rescue delivery (11 files, r310-surgical-variant pit) + W41 freeze/burn 12/12 + T-143 claim + S6 chain rc0"
st["current_task"] = "W41 burned 12/12 (finalize awaits W40 bm-b landing, FAIL-CLOSED chain); LOWAMP-P3 16/16 on origin (E1 four-leg next); T-131 backfill in flight; T-143 claimed (accounts face)"
st["next"] = ("(r345)(a) W41 finalize when W40 finalize lands (bm-b lane, FAIL-CLOSED chain order, K projection 88,120 / ledger 452,940, r538 one-pass law); "
              "(b) LOWAMP-P3 E1 four-leg mandatory pre-consumption + finalize (grid 16/16 complete after r344 delivery; prereg research/LOWAMP-P3.md; r301/r522 methodology); "
              "(c) T-134 s2 p1e_synth conversion (r304 paradigm, measure-first); "
              "(d) T-131 liveness watch + completion closeout (network-bound backfill); "
              "(e) T-143 accounts face assembly start (27 experimental accounts on bm-c host, deliverable 10-29, prep-only); "
              "(f) register_satengine_task.ps1 S4U-first dead-code cleanup (window 10-04); "
              "(g) month-boundary first exam 10-31")
st["verify"] = ("r344: S0 surgical-claim-vs-reality heal (r343 claimed-delivered products were untracked-only: n1_w39_results.json NEVER on origin per log --all + LA-EDGE legacy_x2 15/16 gap; 11-file carry commit dee8469f3 lineage + ls-tree delivery verified blob-identical + AHEAD=0/BEHIND=0) "
                "+ W41 FREEZE one-commit product (THIRTY-FIRST wave, bm-c tenth-owned, first-free after bm-b W40; both-sides arithmetic zero-skip A 125_004..127_003 / B 43_401..43_600 == W40 row W41+ projection; ADMIT receipt leg0-leg3 + N3-R1 + probe-cluster + origin slot vacancy; banned gate ADMIT; selftest PASS incl W41 materializer face; commit 764a377af delivered) "
                "+ engine per-tick re-read PRE-COMMIT ignition observed live (shards 0/1/3 on disk before freeze commit = D-20261002-03 natural behavior, determinism holds) + 12/12 burned same-window + engine state wave_complete_flags includes 41 "
                "+ T-143 claimed (accounts face=bm-c primary, deliverable 10-29) "
                "+ S6 spine rc0 (dualrun ZERO-DRIFT streak 29/3; compute_audit flags cap_violation=W41 burn-window transient 97% + supply_floor pool 1/3 disclosed; watermark py_low_with_work_cands = T-131 network-bound legal; regime ORANGE; market_clock ORANGE_COOL; stale-takeover legal x4 [scorecard/paper_export/daily_scorecard/build_status] bm-a hb stale 63-65min per O-2100 s2.4; attrition CLEAN; b_layer 4 gates PASS; token L2 0; smoke 47/47; orders diff 0/143; D-19 MATCH) "
                "+ inbox MSG-013x = to bm-b (zero action by addressing)")
st["heartbeat_epoch_utc"] = int(now)
st["clock_read"] = now_iso
st["last_ts"] = now_iso
open(sp, "wb").write((json.dumps(st, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
print("state updated round 344")

# --- 4. heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(repo, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, "rb"))
h["prod_lanes"] = "r344: W41 FREEZE + 12/12 same-window burn (THIRTY-FIRST wave, first-free after bm-b W40, both-sides zero-skip, ADMIT receipt _r344bmc_w41_band_gate.py; finalize awaits W40 bm-b); r343 carry rescue (W39 finalize product + LOWAMP-P3 16/16 completion delivered); T-131 backfill in flight"
h["round_no"] = 344
h["updated_at"] = now_iso
h["last_seen"] = now_iso
h["last_seen_at"] = now_iso
h["current_task"] = "W41 burned 12/12 finalize-pending (W40 chain); LOWAMP-P3 16/16 E1-next; T-131 backfill in flight; T-143 claimed (accounts face)"
h["activity_now"] = "r344: S0 carry rescue (11-file delivery, r310-surgical-variant pit closed) + W41 freeze/burn one-window + T-143 claim + S6 chain rc0 + smoke 47/47 + orders diff 0 + D-19 MATCH"
h["latest_artifact"] = "results/p2cal_ext/n1_w41/shard-0..11-of-12.json 12/12 burned (freeze commit 764a377af) + results/perpetual_faces/n1_w39_results.json delivered (ledger 448,340) + results/lowamp_p3/cells_LA-EDGE_legacy_x2.jsonl (grid 16/16)"
h["next_milestone"] = "W41 finalize (after W40 bm-b lands, window <=48h); LOWAMP-P3 E1 four-leg + finalize (<=48h); T-143 accounts face (Oct, deliverable 10-29); month-boundary first exam 10-31"
h["verdict"] = "healthy (W41 freeze+burn same-window closed; engine idle post-W41 = queue empty; T-131 network-bound in flight = legal work face for wm; LOWAMP-P3 grid complete E1-next; wm red=false)"
h["heartbeat_epoch_utc"] = int(now)
h["clock_read"] = now_iso
open(hp, "wb").write((json.dumps(h, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
ep = h.get("heartbeat_epoch_utc")
assert isinstance(ep, int), "epoch must be int"
print("heartbeat updated; epoch int verified:", ep)
