# r670 bm-b S5/S7 closeout: round report append + HANDOVER 5x append + state.json + heartbeat (all asserted)
import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---------- 1. round report append (bytes, append-only) ----------
RR = "logs/iteration-loop/round_reports.md"
REPORT = """
## 2026-10-04T12:5x+08:00 | round 670 | bm-b | D-20261004-02①②③ receipt closeout (F-20261004-02) + D-19 fallback live consumption (watermark 4E5BE321) + S6 34 legs rc0 + 5x HANDOVER
- watermark: GREEN (red=false @12:24; py_watermark py_low_with_work_cands=合法在飞面非违令: 池 3 ready 全=bm-b trio NULLS 在飞零未认领、board 0 open、bandit_open 0、local_batch_running=true 算力在烧佐证 py 61.5%)
- 当前活: FUND trio NULLS canonical burns in flight V753/Q582/D432 of 2000 (owner=bm-b, keepalive claim-refresh 12:16:12, 金周窗 ~9-12/hr/族)
- 最近实物: HQ-FEEDBACK.md F-20261004-02 回执行 (D-20261004-02①②③ 三件收口呈证 1,599B·12:4x) + results/_r670bmb_autofill_selftest.txt (SELFTEST ALL PASS 含 S4b×4+S17dd×2 data_deps 门腿本机活体复验) + results/_r670bmb_d19_check.py/.json (sparse-clone fallback 首枚活体消费: decisions CHANGED 检出+四新行全消费·orders MATCH)
- 下个里程碑: trio NULLS 全 2000 完成后 finalize 腿 (V 余 1247 / Q 余 1418 / D 余 1568 @~9-12/hr/族 ≈ 10-06..10-09 窗内); D-20261002-06 全线收口窗 10-07 (对账行/md5 已由 F-20261004-01 呈证·主线维持)
- S0: pull --rebase 撞 daemon 8 脏面 (bm-b lane) -> HEAD-vs-origin 改动集交集=零实证 -> 定向 absorb (5e9e4a5c7) + merge origin/main 净 0 UU (r437 预对齐净路·集成 bm-c r466-r468 + bm-a r671-r675 八 commit) + push_verify DELIVERED 660fe8ae0
- S0.5: fleet orders 153/153 轮首扫零 unacked (同口径集合比对 r646 律); D-19 decisions **CHANGED** (EB14B510→4E5BE321; K: 集团树缺席→r631 sparse-clone 原字节探针 + r458 双键口径 + r660 subprocess 律) -> 12:00 常务轮批消费: D-20261004-03/04/05/06 四行全读——涉本司=D-20261004-05 到窗核销注记收悉 (D-20261002-05→executed 核销·02/03 补呈窗顺延 10-05 义务已由 bm-c F-20261004-01 承接·06 收口窗 10-07 维持) + D-20261004-02①②③ 派工行 (回执窗 10-06) → 本轮主产出承接; group orders MATCH (68947C17) 零动作; 水位键随本收口更新
- S1: smoke 48/48 PASS
- S3: 板零 open (job_list 0 + fleet tasks open 0); 饱和引擎 alive rc0 (scripts 面 mtime-reload 新代码 merge 后首跑=活体验证·queue 0 idle); 产品面=D-20261004-02①②③ 回执闭环: 反重复双扫发现三件已由本机 r640 死会话收养窗全量落地 (commit 9c38bd8ac: autofill data_deps 门 L1307/L1826/L1953 + PREREG_TEMPLATE L48 种子选位律 + fleet README L37 + S4U fallback 行) → 唯一缺口=F- 回执未呈 → F-20261004-02 补呈 (三件在树证据+活体复验) + 坑律固化 (集团派工行自领前先查既有实现律→CODELY r670 行); 试用劳动力常设线=trio 在飞判决批不触发
- S6: 34 腿全 rc0 (dualrun ZERO-DRIFT streak 51; compute_audit CLEAN burning-healthy py 85.6% pool_ready_unclaimed=0; 金周无新 bar→live.paper/t35_open_fill/t24 条件腿诚实跳过 pre=2026-09-30 post=2026-09-30; update_lhb rc0 no-op <30min 守卫=r669 rc2 后自愈窗·bm-a 车道冗余在; daily_report 5 faces + LIVE-2026-10-04 ORANGE 再生; token_meter 计量)
- S7: 自愈 4/4 (loop pin=2 no-op + watchdog 本窗重建治愈 + pre-commit/pre-push 双爪重装 LF-normalized); attrition CLEAN (4 ledgers·历史 healed 注记照录); inbox 零未读; 5x HANDOVER 窗行落地 (r655/660/665 缺章如实披露·r670 重锚)
- 下轮指针: trio NULLS 烧录看护 (finalize 候选窗) + D-20261002-06 对账行回执随下轮 (10-07 窗) + W14-GENERATE waiting 池面挂账观察
- 本地未达 origin commit 数=0 (commit+push 后 push_verify 三证复核)
"""
with open(RR, "rb") as f:
    d = f.read()
assert d.count(b"| round 670 |") == 0, "r670 report already present"
with open(RR, "ab") as f:
    if not d.endswith(b"\n"):
        f.write(b"\n")
    f.write(REPORT.encode("utf-8"))
with open(RR, "rb") as f:
    assert f.read().count(b"| round 670 |") == 1
print("RR_APPEND_OK")

# ---------- 2. HANDOVER 5x append ----------
HO = "research/HANDOVER.md"
HO_ROW = """
- [2026-10-04 12:5x r670 bm-b] HANDOVER 5x window entry (bm-b window r651-r670, OVERDUE-BACKLOG DISCLOSED: r655/r660/r665 5x stamps missed -- window carried the trio-NULLS burn-watch era + D-19 fallback era + push-race convergence; per r420/r500/r335 precedent no backfill fabrication, single window covered compactly; bm-a r650/r660 + bm-c r440 rows cross-read for their lanes). THIS-WINDOW bm-b PRODUCTS (r651-r670): (1) L1 J13 line healed + probe-reading pit-law batch: r655 retro dormant root-cause (ctx overflow, dashboard chunk 3000->1800) retro GREEN re-landed; six probe laws r655-r661 (dual Format-Table misread / ts fullmatch zone-suffix / five-push-race UU closeout triple / tasklist -FI single-pid false-dead / PS-pipe transcoding fake-CHANGED + post_review P0 gate=official REPORT face / single-form liveness vs dual-form cross-law). (2) r656 dead-session merge adoption (ts-probe prefix-match fix + line-level zero-loss containment canon) + r657 five-race closeout (pre-push claw catches honored, HEAD/MERGE_HEAD raw-byte side-taking, surgery decoupled from add-chain). (3) r658-r667 watch/maintenance spine: trio NULLS burn care + S6 chains rc0 (dualrun streak ->51) + push-race resolvers (r668/r669 addenda). (4) r668 finalize-pool-flip law landed live (THEME-JUDGE-P1 autofill re-burn loop stopped by same-window entry+shard dual flip; r203/r180 cost face first evidence). (5) r670 THIS ROUND: D-20261004-02(1)(2)(3) receipt presented F-20261004-02 (anti-dup live-fire: all three already landed by r640 dead-session adoption commit 9c38bd8ac -- pool data_deps gate + PREREG_TEMPLATE L48 probe-seed law + S4U D-19 fallback line; this window added only the missing F- receipt + live re-verify autofill selftest ALL PASS incl. S4b x4 + S17dd x2, evidence results/_r670bmb_autofill_selftest.txt) + D-19 sparse-clone fallback first live consumption on bm-b (decisions CHANGED EB14B510->4E5BE321, new batch D-20261004-03/04/05/06 all consumed, orders MATCH 68947C17, watermark key updated) + new CODELY law (group-dispatch self-claim pre-check: grep+git-log double-scan before any implementation). POOL STATE: FUND trio NULLS bm-b canonical burns in flight V753/Q582/D432 of 2000 @12:4x (keepalive 12:16:12, ETA V~10-06/Q~10-07/D~10-08 inside finalize window 10-05..10-09). Maintenance: smoke 48/48; S6 34 legs rc0 (dualrun ZERO-DRIFT streak 51); orders 153/153 dual-scan zero unacked; attrition CLEAN 4 ledgers; S7 pin=2 no-op + watchdog rebuilt + both claws LF-normalized; watermark red=false. Next 5x = bm-b r675. Pointers: trio NULLS completion -> finalize per frozen sequence + same-window pool flip (r668 law); D-20261002-06 closeout window 10-07 (recon row receipt due next round); W14-GENERATE + moneyflow-EM parked faces unchanged (GM rulings pending).
"""
with open(HO, "rb") as f:
    d = f.read()
assert d.count(b"[2026-10-04 12:5x r670 bm-b]") == 0
with open(HO, "ab") as f:
    if not d.endswith(b"\n"):
        f.write(b"\n")
    f.write(HO_ROW.encode("utf-8"))
with open(HO, "rb") as f:
    assert f.read().count(b"[2026-10-04 12:5x r670 bm-b]") == 1
print("HO_APPEND_OK")

# ---------- 3. state.json (json.dump + reparse self-verify, r645 law) ----------
NEW_SHA = "4E5BE321F9B7A15D7F58BAB3771ECF329534EED8D30B090CDAC4E9F151D911DC"
st = json.load(open("state.json", encoding="utf-8"))
assert st.get("round_no") == 669, "unexpected round_no %s" % st.get("round_no")
st["round_no"] = 700  # placeholder replaced below
st["round_no"] = 670
st["last_decisions_sha"] = NEW_SHA
st["last_decisions_sha_method"] = "SHA-256 hex upper of git show origin/main:docs/decisions.md raw bytes (sparse-clone, r631 recipe, D-20261004-02(3))"
json.dump(st, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open("state.json", encoding="utf-8"))
assert chk["round_no"] == 670 and chk["last_decisions_sha"] == NEW_SHA
print("STATE_OK round=670 sha=%s..." % NEW_SHA[:12])

# ---------- 4. heartbeat (epoch int + clock T-format, R170/R262 laws) ----------
HB = "fleet/machines/bm-b.json"
hb = json.load(open(HB, encoding="utf-8"))
hb["round_no"] = 670
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["verdict"] = "healthy: r670 D-20261004-02 receipt closeout F-20261004-02 + D-19 fallback live consumption (watermark 4E5BE321) + S6 34 rc0 + trio NULLS V753/Q582/D432 in flight"
hb["current_task"] = "trio NULLS burn care (finalize window 10-05..10-09) + D-20261002-06 recon-row receipt next round (window 10-07)"
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock T-format (R262)"
print("HB_OK epoch=%d clock=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))
