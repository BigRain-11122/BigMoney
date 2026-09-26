# -*- coding: utf-8 -*-
"""R263 bm-a close-out: state bump, heartbeat, CODELY.md appends, round report line.
All writes byte-mirror probed faces (R254/R255/R257 five-face law)."""
import io
import json
import time

NOW = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
CLOCK = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def faces(path):
    raw = open(path, "rb").read()
    return {
        "bom": raw[:3] == b"\xef\xbb\xbf",
        "crlf": b"\r\n" in raw,
        "trail_nl": raw.endswith(b"\n"),
    }


def mirror_write_json(path, obj, f):
    body = json.dumps(obj, ensure_ascii=False, indent=1)
    if f["bom"]:
        body = "\ufeff" + body
    if f["crlf"]:
        body = body.replace("\n", "\r\n")
    if f["trail_nl"] and not body.endswith("\r\n" if f["crlf"] else "\n"):
        body += "\r\n" if f["crlf"] else "\n"
    open(path, "wb").write(body.encode("utf-8"))


def mirror_append(path, text):
    f = faces(path)
    raw = open(path, "rb").read()
    sep = b"\r\n" if f["crlf"] else b"\n"
    add = text.encode("utf-8")
    if f["trail_nl"]:
        body = raw + add + sep
    else:
        body = raw + sep + add + sep
    open(path, "wb").write(body)


# ---- 1. state-bm-a.json: round 262 -> 263
P = "state-bm-a.json"
st = json.loads(open(P, encoding="utf-8-sig").read())
st.update({
    "round_no": 263,
    "did": "R263 dead-round residue adoption full arc + O-1355 receipt: adopted 18:08 dead session (25min timeout kill, API generateJson failure mid-edit), completed half-written h4 prev-audit fix (syntax half-line + C7 fixture vs _corr min_overlap=20), selftest 15/15, verify real face 3332=days-1, 5th launch landed 22.3s (ledger 187741+104=187845, g1/g2 all-False honest negative), harvest gate PASS + pool flipped done; T-83 (O-1355) scoped claim mechanical lane + L9 orders index artifact (83 orders / 33 cross-refs); S6 24 legs exit 0",
    "verdict": "R263: residue arc closed end-to-end (prereg frozen by predecessor -> 5-launch crash arc -> h4 fix -> landed -> harvested done); CN-CORE-DDCTL-P1 judged NEGATIVE honest (dd-gating on CORE ballast beats no gate lines); O-1355 late-arriving order caught by S7 double-scan and receipted via T-83 claim+artifact",
    "next": "(1) T-83 mechanical lane continuation (s2 cross-doc contradiction grep) -- s1/s3 governance faces reserved GM session; (2) 09-28 Monday new-bar chain (cutoff 09-24); (3) 10-01 monthly trio + REGIME_GUARD v3 date gate + 5x HANDOVER at R265; (4) T-70 C-arm verdict window 10-09",
    "ts": NOW, "last_round_ts": NOW, "updated_at": NOW,
    "current_task": "idle (round 263 closed)",
    "last_run": NOW, "last_round_at": NOW, "last_round": 263, "updated": NOW,
})
mirror_write_json(P, st, faces(P))

# ---- 2. heartbeat fleet/machines/bm-a.json
P = "fleet/machines/bm-a.json"
hb = json.loads(open(P, encoding="utf-8-sig").read())
ack = set(hb.get("orders_ack", "").split())
ack.add("O-20260926-1355-bm-a.md")
hb.update({
    "last_seen": NOW,
    "current_task": "R263 closed: CN-CORE-DDCTL residue arc landed+harvested (judged negative honest); T-83 scoped claim (mechanical lane) started",
    "cpu_cores": 32,
    "cpu_pct": 8.7,
    "free_ram_gb": 58.9,
    "gpu_free_vram_gb": 15.0,
    "verdict": "GREEN R263: dead-round residue adopted and closed (h4 fix + 5th launch landed 22.3s, ledger 187845, harvest PASS pool done); O-1355 caught by S7 double-scan -> T-83 scoped claim + orders index artifact; smoke 25/25; S6 24 legs exit 0",
    "orders_ack": " ".join(sorted(ack)),
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": CLOCK,
})
mirror_write_json(P, hb, faces(P))
chk = json.loads(open(P, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"], "F7 face"
print("heartbeat self-verify: epoch int", chk["heartbeat_epoch_utc"], "clock T-sep OK, ack", len(ack))

# ---- 3. CODELY.md: pit-law + O-1355 execution record (行级追加)
P = "CODELY.md"
pit = ("[2026-09-26 19:0x] 坑律（bm-a R263·死轮残骸收养面+夹具阈值面·E1 收养期自捕零外泄）："
       "**收养死轮半截修复必先编译+selftest——前任 25min 超时被杀时文件写到一半（np.array 缺 `]`），"
       "且 hermetic 夹具期数必须清家族函数阈值默认（_corr min_overlap=20：5 天夹具走 corr 路径返 None face；"
       "值数须与索引数恒等（[x]*5=25 值 vs d6[1:]=24 位崩）**；正律=①收养即 py_compile+selftest 全绿才重发"
       "②夹具期数≥阈值+1（25 期 overlap 24>20）③收养 commit 带出处（R241 范式）。"
       "指针=results/_r263bma_h4_prev_verify.py+scripts/cn_core_ddctl_p1.py selftest [C7]+commit ef5c27c9")
rec = ("[2026-09-26 19:0x] 执行记录（bm-a R263·O-20260926-1355 晚到令回执）：S7 双扫捕到随 rebase 拉入的 "
       "O-1355（法熵大审视令·S0.5 扫描后到窗），同轮回执=派工票 T-83 scoped 认领（机械扫车道：s2 脚本面+L9 令索引；"
       "s1 清点/s3 七件治理面=GM 会话保留未碰）+首件 L9 原料 results/orders_index.json（83 令/33 真交叉引用/取代链裁定留 GM）；"
       "orders_ack 82->83。指针=results/_r263bma_orders_index.py+fleet/tasks/T-2026-09-26-83-P1.json claim_scope_note")
for line in (pit, rec):
    mirror_append(P, line)

# ---- 4. round report line
P = "logs/iteration-loop/round_reports-bm-a.md"
rr = ("2026-09-26 19:0x | R263 bm-a | watermark: GREEN-tinted insufficient_history (18:43 probe n=1 window reset post-batch-launch; "
      "pool-supply-gap CLOSED SAME ROUND: CN-CORE-DDCTL landed+harvested; compute_audit FLAG idle_with_work = transient sampled 25s post-launch batch not yet spun) | "
      "did: S0 fetch in-sync 13082605 -> adoption commit a5a2bd08 push collision (bm-b r266 + O-1355 incoming 2 commits) -> rebase clean -> push ef5c27c9; "
      "S0.5 round-start scan 82/82 zero diff; **S7 close double-scan CAUGHT late-arriving O-20260926-1355 (governance order rode the rebase)** -> receipted same round via T-83 scoped claim (mechanical lane: s2 scripts + L9 index; s1/s3 GM faces untouched) + first artifact results/orders_index.json (83 orders, 33 real cross-refs after self-cite phantom purge 95->33, 1 honest empty-quote; supersession adjudication reserved GM) + orders_ack 83; "
      "S1 smoke 25/25; S2 job_list empty + board T-83 only open -> claimed; "
      "S3 MAIN = R263 DEAD-ROUND RESIDUE ADOPTION (18:08 session killed by 25min timeout @18:33, API generateJson failure; forensics run_180801.log + .out tail): predecessor arc = CN-CORE-DDCTL-P1 prereg frozen on-chain + runner pooled + 4-launch crash arc (naming bug x2 / dead-condition bug caught mid-finalize and killed = zero-ledger-pollution / h4 prev-audit n-1 index crash) -> adopted half-written h4 fix: completed syntax half-line (np.array missing bracket written at kill moment) + C7 hermetic fixture (5-period draft returned None face vs _corr min_overlap=20 -> 25 periods, overlap 24; values==index-length assert) -> selftest 15/15 -> real-face verify _r263bma_h4_prev_verify.py all prev cells 3332=days-1 -> commit ef5c27c9 (R241 adoption provenance) -> manual autofill tick 5th launch pid 37364 runner c4161eec -> **LANDED 22.3s** 4 cells differentiated (CORE_DD10 0.1048 / CORE_DD20 0.3086 / SAT40_DD10 0.3796 / SAT40_DD20 0.4477 = dead-condition fix production-verified) + trials_ledger 187741+104=187845 + g1/g2 all-False **CN-CORE-DDCTL judged NEGATIVE honest** (dd-gating on CORE ballast clears no gate line; R261 doctrine residual consumed, no reopen) -> harvest gate _r263bma_coreddctl_harvest.py PASS (canonical scanner head 187845 re-derived + dead-condition differentiation guard + arithmetic) -> pool entry+shard flipped done harvest_note landed (field-level 4+/3- byte-mirrored); "
      "S6 24 legs ALL exit 0 (weekend no-ops: audit FLAG idle_with_work transient; watermark probe insufficient_history n=1 batch-burning; update_daily 0 rows cutoff 09-24; regime ORANGE d2 shadow hs300<MA200 breadth 0.77; clock CALL-2026-09-24 ORANGE_COOL 4/0; lhb 28min throttle; heat weekend; futures/options/sina/moneyflow cutoff-throttle no-ops; ths same-day idempotent; AH spawn throttled 24min next-round self-heal; fund_premium bm-c lane; fundamental 21.3h fresh; blf all_pass 5222 codes; aggr/grid marks-at-cutoff; alloc bm-b lane; t35_export 6/18 first-snapshot; scorecard 6 traders; daily_report faces=4 token=1; build_status; token_meter L2 1 leg 6135 tok local) + no-new-bar Saturday -> live.paper/t35_open_fill/t24x2 conditional legs legally skipped; "
      "S7 schtasks R49 law IterationLoop Running + Watchdog Ready; inbox 0 unread | "
      "evidence: results/cn_core_ddctl/p1_results.json (trials_ledger 187741+104=187845 evidence_cutoff 2026-09-22) + runner.log finalize line elapsed=22.3s + results/_r263bma_coreddctl_harvest.py exit 0 + results/_r263bma_h4_prev_verify.py (all cells 3332) + selftest 15-leg 0 FAIL + results/orders_index.json (83/33) + git field-level diffs (pool 4+/3-, ticket 5+/2-) + S6 exit codes 24x0 in transcript + heartbeat epoch int self-verified | "
      "next: (1) T-83 mechanical lane continuation (s2 cross-doc contradiction grep script) -- s1/s3 = GM session; (2) 09-28 Monday new-bar chain (cutoff 09-24); (3) 10-01 monthly trio + REGIME_GUARD v3 date gate + 5x HANDOVER at R265; (4) T-70 C-arm verdict window 10-09")
mirror_append(P, rr)
print("close-out writes complete:", NOW)
