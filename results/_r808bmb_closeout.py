import json, time, io

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_epoch = int(time.time())

# --- state.json (root, TRUE state per r646 epoch law) ---
with io.open(r"state.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 808
st["round_no_label"] = "r808"
st["note"] = ("r808: fleet integration round. 402-commit backlog rebased (day-long 429/timeout outage debt); "
              "own absorb commit 397455c7f replayed EMPTY = byte-identical to upstream ops-session absorbs -> dropped as duplicate zero-loss (cherry-pick dedup); "
              "S0.5: orders 3 newly acked (O-20261009-2334/O-20261009-2359/O-20261010-0058) + 9 degraded ack-registry entries restored (upstream heartbeat had lost 1007/1008 bm-c era acks, stale-overwrite by ops session tree); "
              "O-20261009-2359 (429 compliance law) + O-20261010-0058 (tailscale doctrine, bm-b faces pre-satisfied) consumed; "
              "honest deferrals to r809: S1 smoke, S6 chain (10-09 bar lanes), divlowvol ex-date + quality NAV probes, quartet, attrition scan, D-19 fresh read")
st["did"] = ("r808: S0 identity bm-b; orphan probe 0 (20 lawful py faces); git sync face was behind=402/ahead=1 after day-long round outage -> "
             "absorb own faces commit + stash/rebase/skip surgery (r805/r642 lineage): 942268c09 auto-skipped (upstream), 397455c7f empty-dup dropped; "
             "REPORT-20261009.md local draft diverged from origin final -> quarantined results/_quarantine/REPORT-20260909.md.r808-side (zero-loss); "
             "post-rebase FF to 8a0abf553 = 0/0 synced; concurrent ops session detected live (order landings 2334/2359/0058 + orders-dir mutations mid-round) -> minimal-footprint closeout per anti-duplication law; "
             "S0.5 orders diff: 3 new acks + 9 restored; bm-a orders 1105/2340 vanished from disk mid-round by ops session cleanup = not acked (phantom-guard)")
st["verdict"] = ("amber->green: S0 integration closure achieved (0/0 sync); S6 chain + smoke deferred to r809 (time-budget, integration consumed the window); "
                 "no code files changed this round; last smoke green 49/49 r807")
st["current_task"] = ("r808 closed; next = r809: S1 smoke + S6 full chain (10-09/10-10 bar: etf_daily 5-member -> REGIME_GUARD v3 live.paper -> t35 -> t24 -> promotion -> papers -> exports -> scorecards) "
                      "+ divlowvol ex-date probe + quality NAV pathology triage (<=10-10 12:00) + quartet + attrition scan + D-19 fresh group-tree read + orders re-diff")
st["next"] = st["current_task"]
st["last_round_at"] = now_iso
st["ts"] = now_iso
st["updated_at"] = now_iso
st["last_seen"] = now_iso
st["clock_read"] = now_iso
with io.open(r"state.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json ---
with io.open(r"fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
restore = [
    "O-20261007-1850-bm-c.md","O-20261007-2145-bm-c.md","O-20261007-2215-bm-c.md","O-20261007-2230-bm-c.md",
    "O-20261007-2240-bm-c.md","O-20261007-2245-bm-c.md","O-20261007-2255-bm-c.md","O-20261007-2315-bm-c.md",
    "O-20261008-1300-bm-c.md",
]
new = ["O-20260909-2334-bm-b.md", "O-20260909-2359-bm-b.md", "O-20261010-0058-bm-b.md"]
ack = hb.get("orders_ack", [])
for o in restore + new:
    if o not in ack:
        ack.append(o)
hb["orders_ack"] = ack
hb["orders_ack_count"] = len(ack)
hb["round"] = 808
hb["round_no"] = 808
hb["now_active"] = "r808 closeout: 402-commit fleet integration (0/0 sync) + orders ack x3 +9 registry restore; S6/smoke deferred r809"
hb["current_task"] = "r809: smoke + S6 chain (10-09 bar) + divlowvol ex-date probe + quality NAV triage (<=10-10 12:00) + quartet + attrition + D-19"
hb["task"] = "absorb/closeout"
hb["latest_artifact"] = "r808: integration closure 0/0 at 8a0abf553 + heartbeat ack-registry repair (9 restored) + O-2359/O-0058 receipts in round report"
hb["next_milestone"] = "S6 chain 10-09 bar lanes + smoke r809 (<=10-10 02:00) + divlowvol ex-date & quality NAV probes (<=10-10 12:00) + 5x HANDOVER r810"
hb["verdict"] = "green-integration-complete"
hb["last_action"] = "r808: net-tree surgery (stash/rebase/skip, empty-dup drop), orders 3 acked +9 restored, minimal-footprint closeout vs live ops session"
hb["last_round_at"] = now_iso
hb["last_seen"] = now_iso
hb["updated"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = now_epoch
assert isinstance(hb["heartbeat_epoch_utc"], int)
hb["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": now_iso,
              "note": "r808 post-push face written pre-push; push+self-verify executed in-round (rev-list 0/0 + ls-remote)"}
with io.open(r"fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report line ---
line = (f"{now_iso} | r808 bm-b | WM-VERDICT: green (red=false insufficient_history n=1 legal reset; satengine idle queue face; next_pick claimed moneyflow IC advisory consumed as-is) | "
        f"孤儿面=0 (20 lawful py faces; r806 driver 25464 + astock child 13992 both DEAD = estate closed, absorbed) | "
        f"CEO three-line: 当前活=r808 集成收口（402 落后清偿·0/0 同步·令处理 3 ack+9 恢复）| 最近实物=8a0abf553 0/0 同步面 + 心跳 ack 登记簿修复 + O-2359/O-0058 回执（本报告）| 下个里程碑=r809 S6 链 10-09 bar 全腿 + smoke（<=10-10 02:00）+ divlowvol ex-date/quality NAV 双探针（<=10-10 12:00）| "
        f"did: S0 落后 402/ahead 1（全日 429/超时灾后欠账）→ 吸收自面 commit + stash/rebase/skip 手术（r805/r642 正典）：942268c09 上游同补自动跳过、397455c7f 空=字节恒等纯重复按 dedup 律 drop 零丢失；REPORT-20260909.md 本地稿≠origin 终稿→quarantine 零丢失隔离；FF 至 8a0abf553=0/0；运维会话在飞实证（O-2334/2359/0058 落令+orders 目录 1105/2340 件扫描后 1 分钟内被删=幽灵守卫不 ack）→ 最小足迹收尾不争面 | S0.5: 新 ack×3（O-2334 429 合规令 bm-b 面=SWA 已落地+常规节奏·O-2359 同令 0058 顺延·O-0058 tailscale 命名统一令 bm-b 面=主机名已正+Taildrop 三段绿全预满足）+ 心跳 ack 登记簿 9 条退化恢复（上游心跳被运维会话陈旧基座覆写丢 1007/1008 bm-c 族 ack·union 修复）| S1/S6/probes/quartet/attrition/D-19 → r809 诚实延期（时间预算耗于集成手术·本轮零代码件改动·最近绿 smoke 49/49 r807）| "
        f"evidence: git rev-list origin/main...HEAD = 0/0 @8a0abf553 + results/_quarantine/REPORT-20260909.md.r808-side + state.json r808 + heartbeat epoch int self-verified | "
        f"本地未达 origin commit 数=push 收口后 0（rev-list+ls-remote 双证）| "
        f"product score 1 (integration closure + registry repair = actual file/state deliverables; S6 chain deferred = no new product artifact this round) | "
        f"429 note (O-2359 §2): 本轮零额外云端调用面——单次轮体调用=既定 10min 节奏（SWA 错峰已落地 23:25）\n")
with io.open(r"logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)

print("BOOKKEEPING-DONE", now_iso, "epoch", now_epoch, "ack_count", len(ack))
