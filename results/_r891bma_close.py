# r891 bm-a closeout bookkeeping: state bump + watermark repairs + heartbeat + round report line
# (per-round scratch; r890 close pattern; epoch int per R170/R178; clock_read T-separated per R262;
#  report -> ROOT round_reports-bm-a.md per r844 law)
import json, os, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MID = "bm-a"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")

# --- state bump (round 891 closed; r890 state-write landed via r890 close script, sequence honest)
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "round_no": 891, "round": 891, "last_round": 891, "loop_round": 891,
    "last_round_at": TS, "last_round_ts": TS, "last_round_closed": TS,
    "last_run": TS, "last_seen": TS, "updated": TS, "ts": TS,
    "last_decisions_sha": "ee70cef0f4a5e3b8db4c67936ce2a2aeee222fff8d03f33339b390eac814ac8c",
    "last_decisions_at": TS, "last_decisions_ts": TS,
    "last_decisions_seen": ("r891: DEC watermark provenance repair -- canonical python raw-bytes re-read ee70cef0 == r889 canonical "
        "(content UNCHANGED since r889; r890's 54b242ac = bad-provenance artifact produced inside the 17:55-20:00 gitsilent-winexe "
        "PS-not-waiting window per ORD ~20:0x row, third instance of the r814/r831/r832 family; D-05..08 rows already consumed by "
        "r888/r889 tip lineage, zero re-consume, zero BigMoney dispatch on the board)"),
    "last_orders_sha": "caef5b781651e8e1178df5dc866f0e6851b0710255e35f6ec2c3b7ee0326bce2",
    "last_orders_at": TS,
    "last_orders_seen": ("r891: ORD 2a5ec5a3 -> caef5b78 delta consumed (3 rows past r890's 308-313: 10-08 19:25 全面开工令 "
        "(bm-a machine resume already executed 19:12 by co-window session, VRAM 11315MB pinned, receipt-only; MV/bm-c sub-items "
        "observed; bm-b unreachable disclosed) + 10-08 ~20:0x gitsilent winexe 形态补正 self-receipt (bm-a own row, explains the "
        "DEC bad-provenance window) + 10-08 19:33 吸嘟嘟全速推进令 (Biggame domain, executed by MiniGame session, zero BigMoney action)"),
    "current_task": "W190 freeze chain next window (prereg buildgen + freeze-edits five-face insertion + tick ignite; seat published r891 per r565; A 432_804..434_803 / B 434_804..435_003; W191+ re-derive-MANDATORY) + 10-08 sina late-bar absorb watch (panel cutoff 09-30) + GM bm-b reroute decision watch",
    "did": ("r891: W189 pre-finalize three-gate probe GREEN (r831 half-open; receipt _r891bma_w189_prefinalize_probe.json) -> finalize one-pass EXACT "
        "(merged mu -0.0929 sigma 0.2452 K 413,720; ledger 820,928+2,200=823,128 == projection; skill_line 1.1863->1.1866 K-lift +0.0003) "
        "-> n1 selftest PASS incl W189 materializer + pf 9/9 -> W190 pre-seat probe ADMIT (A 432_804..434_803 staircase FIFTIETH / "
        "B 434_804..435_003 mutual-exclusion; receipt _r891bma_w190_probe_receipt.json) -> W190 seat MSG published=reserved (r565) "
        "-> S6 39/39 rc0 (new_bar=False sina 10-08 bar absent at source; dualrun streak 51 pre-resolve; post-resolve reconcile: "
        "compute_audit drift observation-phase recorded) -> push race with bm-c r776 window: 14-UU canonical resolve (7 via merge_lane_views "
        "ALL_FACES + 7 manual snapshot/twin same-side byte-copy, resolver _r891bma_resolve.py; r863 daemon-churn rebase-continue pit hit "
        "and cured per canon TEMP-backup->checkout->continue->restore) -> c177bf73b pushed CLEAN"),
    "last_action": "r891 closeout: state/heartbeat/report writes + closeout commit",
    "last_artifact": "results/perpetual_faces/n1_w189_results.json (K 413,720, ledger 823,128 == projection EXACT) + results/_r891bma_w190_probe_receipt.json + fleet/inbox/MSG-2026-10-08-2035-bma-w190-seat.md",
    "latest_artifact": "results/perpetual_faces/n1_w189_results.json (K 413,720, ledger 823,128 == projection EXACT) + W190 seat published on origin",
    "next": ("W190 chain (prereg buildgen + freeze-edits five-face insertion + tick ignite; seat 2035 on origin; A 432_804..434_803 / "
        "B 434_804..435_003; W191+ naive A 434_804..436_803 / B 435_004..435_203 re-derive-MANDATORY) + 10-08 sina late-bar absorb on landing "
        "(REGIME_GUARD v3 enforce + live.paper family + marks settle face) + GM bm-b reroute A/B decision watch"),
    "now_active": "r891 closed: W189 finalize EXACT landed (K 413,720 / ledger 823,128) + W190 seat published; engine idle queue 0; W190 freeze next",
    "verify": ("W189 finalize EXACT (K 413,720 / ledger 823,128 == published projection) + n1 selftest PASS incl W189 materializer + pf 9/9 + "
        "smoke 49/49 + S6 39/39 rc0 (new_bar=False) + attrition CLEAN (4 ledgers) + orphan face=0 (probe rc0) + self-heal quad green "
        "(loop pin=8 no-op + watchdog + both claws) + 14-UU canonical resolve + r863 pit cured + DEC/ORD watermarks canonical + "
        "orders unacked=0 + inbox processed"),
})
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat
hp = os.path.join(ROOT, "fleet", "machines", f"{MID}.json")
hb = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
idle = json.load(open(os.path.join(ROOT, "results", "idle_trigger.bm-a.json"), encoding="utf-8"))
import psutil
ram_free_gb = round(psutil.virtual_memory().available / (1024**3), 1)
hb.update({
    "last_seen": TS,
    "current_task": "r891 closed: W189 finalize EXACT + W190 seat published + S6 39/39; W190 freeze chain next",
    "cpu_cores": os.cpu_count(),
    "free_ram_gb": ram_free_gb,
    "gpu_free_vram_gb": idle.get("vram_free_gb"),
    "verdict": ("r891: WM green (red=false lane healthy); engine ALIVE rc0 idle-after-burn W189 12/12; W189 finalize one-pass EXACT "
        "(K 413,720 ledger 823,128 == projection; merged mu -0.0929 sigma 0.2452; skill_line K-lift +0.0003); W190 seat published=reserved "
        "(A 432_804..434_803 staircase 50th / B 434_804..435_003); S6 39/39 rc0 sina 10-08 bar absent at source honest no-op watch; "
        "ORD 3-row delta consumed (全面开工 receipt / gitsilent 补正 / 吸嘟嘟 zero-action); DEC watermark provenance-repaired to canonical "
        "ee70cef0 (r890 54b242ac = winexe-window artifact, content unchanged, zero re-consume); push-race 14-UU canonical resolve + "
        "r863 churn pit cured; bm-b 29.2h starvation reroute A/B pending GM; W190 freeze next rounds"),
    "idle_rounds": 0,
    "agenda_starved": False,
    "heartbeat_epoch_utc": epoch,
    "clock_read": TS,
    "ts": TS,
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock_read T-separated"
print("state+heartbeat written; epoch int ok; clock T ok; ram_free_gb=", ram_free_gb)

# --- round report line (ROOT per r844/r872 law)
rp = os.path.join(ROOT, "round_reports-bm-a.md")
line = (
    f"{TS} | r891 | bm-a | dept:research/engine (perpetual line+engineering) | "
    "WM-VERDICT: green (red=false lane healthy; engine ALIVE rc0 idle-after-burn W189 12/12 queue 0; next_pick moneyflow IC claimed=advisory panel-source-blocked; py_watermark rc0) | "
    "当前活: r891 收尾 (孤儿面=0·14 py faces; W189 finalize one-pass EXACT + W190 seat published) | "
    "实物: ①results/perpetual_faces/n1_w189_results.json (W189 finalize: 3-gate GREEN -> merged mu -0.0929 sigma 0.2452 K 413,720; ledger 820,928+2,200=823,128 == projection EXACT; skill_line 1.1863->1.1866 K-lift +0.0003; n1 selftest PASS incl W189 materializer + pf 9/9) "
    "②results/_r891bma_w190_probe_receipt.json + fleet/inbox/MSG-2026-10-08-2035-bma-w190-seat.md (W190 pre-seat probe ADMIT: A 432_804..434_803 staircase FIFTIETH hops=1 / B 434_804..435_003 mutual-exclusion hops=1; anchor W189 ledger 823,128 machine-read; seat published=reserved per r565 push-before-freeze) "
    "③results/_r891bma_s6_chain.json (S6 39/39 rc0 bad NONE; new_bar=False sina 10-08 节后首 bar 源面未发布诚实 no-op·panel cutoff 09-30; dualrun streak 51; post-resolve reconcile compute_audit drift=观察相如实记录) "
    "④results/_r891bma_resolve.py (push-race with bm-c r776 window: 14-UU 全共享名再生面 canonical resolve=7 ALL_FACES merge_lane_views (union+ts-probe take-new :3: bm-a 侧全胜) + 7 manual snapshot/twin 同侧字节拷贝 (REPORT/LIVE 双孪生 md 字节同侧 r329 律); r863 rebase-continue 零 UU 仍拒=daemon churn 敏感面 TEMP 备份->checkout->continue->回移正法实弹治愈; c177bf73b pushed CLEAN ahead=0/behind=0) "
    "| 下轮指针: ①W190 freeze chain (prereg buildgen+freeze-edits+tick ignite; A/B per seat 2035; W191+ re-derive-MANDATORY) ②sina bar 发布后 S6 补跑 (REGIME_GUARD enforce+live.paper+marks settle) ③GM bm-b 改派裁定消费 ④DEC ee70cef0/ORD caef5b78 水位键已更新 canonical | "
    "验证: smoke 49/49 + S6 39/39 rc0 + attrition CLEAN (4 ledgers) + ORD 双扫 unacked=0 + DEC 水位 provenance 修复 (r890 54b242ac=winexe 窗伪影·内容未变·零重消费) + 自愈四件套绿 (loop pin=8 no-op/watchdog/双爪) + 孤儿面=0 + 本地未达 origin commit 数=0 (push 后 fetch+rev-list 自证) + token: L1 零 API [via bm-a r891]"
)
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line + "\n")
print("round report appended")
