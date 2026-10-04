# r707 bm-a S7 bookkeeping: state + heartbeat (programmatic absolute-value writes, r694 law)
import json, io, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
NOW_SHORT = NOW[:16] + "+08:00"
EPOCH = int(time.time())
assert isinstance(EPOCH, int)

# ---------- state-bm-a.json ----------
sp = "state-bm-a.json"
s = json.load(io.open(sp, encoding="utf-8"))
old = s.get("round_no", 0)
s["round_no"] = old + 1
s["round"] = "r707"
s["last_round"] = "r706"
s["last_round_at"] = "2026-10-05T01:38:06+08:00"
s["last_round_ts"] = NOW_SHORT
s["updated"] = NOW_SHORT
s["current_task"] = ("r707 closeout: dead-r707 session adopted (grammar-key P0 fix db7c8697e + shard-0/1/2 ckpts + pit-engine entry absorbed); "
                     "origin 29-commit wave merged 35-UU canon-resolved DELIVERED ffe9bc7df; judge burn resumed fleet-wide (6/12 ckpts landed); W3-JUDGE verdict verified in-tree (bm-c adoption, 0 G2-eligible)")
s["did"] = ("r707: S0 dead-session absorb dcb7be144 + merge ffe9bc7df (35 UU: 19 regen theirs-fresh, 9 paper ours, fuse per-sig 78/55, pool 9 entries theirs-newer, "
            "3 jsonl zero-loss unions) + push DELIVERED behind=0 + daemon auto-resumed (tick self-pushes def1cecee+) + orders 154/154 dual-sweep zero-unacked + "
            "D-19 dual MATCH (755428F8/e79e15f9) + smoke 48/48 + satengine alive rc0 idle + judge 6/12 ckpts (0,1,2,6,7,8) + S6 38/38 rc0 "
            "(REPORT/LIVE-2026-10-05 regen, dualrun ZERO-DRIFT streak 8) + self-heal 4/4 + attrition CLEAN 4 ledgers")
s["next"] = ("r708: judge 12/12 watch -> judge-finalize (ledger PERPETUAL-N2-W15-JUDGE + prereg sec.7/8 backfill + r668 pool double-flip same window; "
             "my berth per MSG-0125); moneyflow EM fuse self-heal watch -> panel -> IC reference batch prereg (bandit next_pick); "
             "trio NULLS finalize watch 10-05..09 (bm-b canonical); tailscale bm-c CEO one-click pending")
s["verify"] = ("smoke 48/48; merge DELIVERED ffe9bc7df + daemon ticks def1cecee (behind=0 post-push fetch verify); orders/D-19 dual-scan MATCH x2; "
              "attrition CLEAN; claws parity installed; loop pin8 no-op + watchdog re-registered; guard scan 4 ledgers healed-note")
s["last_action"] = "r707: absorb+merge+push chain delivered; judge burn unblocked fleet-wide; W3 verdict in-tree verified"
s["heartbeat_epoch_utc"] = EPOCH
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
    f.write("\n")
json.load(io.open(sp, encoding="utf-8"))
print("state: round_no", old, "->", old + 1, "| round r707 | epoch", EPOCH)

# ---------- fleet/machines/bm-a.json ----------
hp = "fleet/machines/bm-a.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = NOW_SHORT
h["current_task"] = ("r707 done: judge-grammar P0 fix adopted+pushed, 29-commit origin wave merged (35 UU canon), "
                     "N2-W15 judge burn resumed fleet-wide 6/12 ckpts; S6 38/38, smoke 48/48")
h["cpu_cores"] = 32
h["cores"] = 32
h["cpu_pct"] = 8.1
h["cpu_util_pct"] = 8.1
h["free_ram_gb"] = 52.5
h["gpu_free_vram_gb"] = 5.5
h["gpu0_free_vram_gb"] = 5.5
h["verdict"] = "ok"
h["health"] = "ok"
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW_SHORT
h["now_active"] = "N2-W15 judge 12-shard burn fleet-wide in flight (6/12 ckpts landed: 0,1,2,6,7,8; grammar-key fix live) + trio NULLS bm-b canonical burning"
h["latest_artifact"] = "merge ffe9bc7df (35-UU canon-resolved origin wave incl W3-JUDGE ADOPT_PASS verdict) + dead-session products absorb dcb7be144 @ 2026-10-05T03:0x"
h["next_milestone"] = "judge 12/12 -> judge-finalize + prereg sec.7/8 backfill (window <=10-08; ETA burn completion ~03:4x tonight) + trio NULLS finalize 10-05..09"
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write("\n")
h2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], "clock must be T-separated"
print("heartbeat: epoch int", h2["heartbeat_epoch_utc"], "| clock", h2["clock_read"], "| self-proof PASS")
