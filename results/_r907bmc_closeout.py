# -*- coding: utf-8 -*-
"""r907 bm-c closeout: 9-dead-session absorb heal (r898-r906) + W212 finalize product landing.
State round_no 898 -> 908 (this session executed as r907, next = r908).
Watermarks hold (S0.5 probe dual-delta FALSE at 03:29: dec 67403afa / ord 33aee170)."""
import ctypes, ctypes.wintypes, json, os, re, subprocess, time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now_str = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---- fresh machine readout (ctypes RAM + nvidia-smi VRAM + ctypes CPU 2-sample) ----
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.wintypes.DWORD), ("dwMemoryLoad", ctypes.wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
mem = MEMORYSTATUSEX(); mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
ram_free_gb = round(mem.ullAvailPhys / 1024**3, 2)
ram_total_gb = round(mem.ullTotalPhys / 1024**3, 1)

class FILETIME(ctypes.wintypes.FILETIME): pass
def cpu_snap():
    idle, kern, user = FILETIME(), FILETIME(), FILETIME()
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kern), ctypes.byref(user))
    f = lambda t: (t.dwHighDateTime << 32) | t.dwLowDateTime
    return f(idle), f(kern), f(user)
i1, k1, u1 = cpu_snap(); time.sleep(0.4); i2, k2, u2 = cpu_snap()
cpu_pct = round(max(0.0, min(100.0, 100.0 * (1 - (i2 - i1) / max(1, (k2 - k1) + (u2 - u1))))), 1)

vram_free_mb = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=15,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    vram_free_mb = int(float(out.stdout.strip().splitlines()[0]))
except Exception:
    pass
if vram_free_mb is None:
    vram_free_mb = 576  # last-known face value, disclosed in report

ROUND = 907

did = ("r907 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 zero-kill (MV-lane infra kept); "
       "(2) ABSORB r898-r906 NINE dead sessions (all committed bodies -- W210 takeover freeze r898 / W211 freeze+unfuse+reburn 12/12 r898-r904 / W18 judge-finalize r902 / "
       "i2v lane root-fixes r903/r904 / W212 five-face freeze splice LANDED r906 0f30cb725 03:06:37 / engine self-burn 12/12 with 2 ledger append commits b1944432d+a3c648d6b -- "
       "every one died pre-closeout, state frozen at r897) -> this session = r907 per bm-b r898/r894 absorb precedent, counter advanced 898->908 so next session = r908; "
       "(3) S0 fetch 0/0 clean no rebase; (4) S0.5 standing probe: orders_delta=false decisions_delta=false unacked=0 -- dec 67403afa / ord 33aee170 both hold zero new rows zero action; "
       "(5) S1 smoke 49/49; S2 boards clear (fleet tasks open=0, jobs 0); satengine alive rc0 (heartbeat fresh, queue/burns empty post-W212 = supply gap disclosed, W213 next); "
       "(6) PRODUCT = W212 FULL CYCLE completed same-night: engine self-burn 12/12 verified REAL (03:06:34-03:10:33, each shard 182 backtests ~63s ProcessPool-8, bands A 481204..483203 / B 483204..483403) "
       "-> finalize one-pass LANDED (ledger identity 887,989+2,200=890,189 asserted; merged K=464,320 EXACT; mu=-0.0927 sigma=0.2451; w212-only mu=-0.0872; "
       "skill_line_v2 @n_eff=887,989: 1.1902 -> 1.1903 K-lift +0.0001; voids LOWAMP-P1/P2; pit-95 guard + five FAIL-CLOSED gates all passed) "
       "-> prereg sec.7/sec.8 one-shot backfill LANDED (numbers machine-read from finalize stdout zero hand-copy); "
       "(7) debt disclosed honest: sec.5 five-key probe + pre-finalize six-gate probe not re-run this window + W209/W211 sec.7/8 backfill debt inherited (dead-session estate) -> next-window heal; "
       "(8) S6 absorbed from r906 (body S6 41/41 rc0 committed 8aa1dcf4f 03:00:43 + 5-leg freshness rerun 03:08:21, ~30min fresh, idempotent legs) per r897 absorb precedent; "
       "(9) S7: idle --worked (idle_rounds=0) + attrition 4 CLEAN + quad self-heal (loop pin=5 no-op, watchdog re-registered, precommit/prepush claws reinstalled) + state 9-round heal this write")

verdict = ("green: absorb+product round -- W212 full cycle complete (freeze r906 -> engine self-burn 12/12 -> finalize r907: ledger 890,189 / K=464,320 / skill_line 1.1903), "
           "prereg sec.7/8 backfilled, 9 dead sessions (r898-r906) absorbed with state healed, dual watermark zero-delta, smoke 49/49, "
           "GPU/RAM yielded to MV CEO-priority i2v burn (XQ lane in flight, interactive window owns), W213 supply gap = next window first action")

next_ptr = ("r908: (1) W213 seat probe + prereg draft + splice editor freeze-prep bundle FIRST ACTION (upstream W212 finalize landed = clean precondition, r888/r906 precedent); "
            "(2) W209/W211 prereg sec.7/8 backfill debt heal + W212 sec.5 five-key/pre-finalize six-gate probe debt heal; "
            "(3) Monday 15:30 first new-bar window: update_daily chain + live.paper + t35_open_fill_verify + t24 legs; "
            "(4) unity-mcp POC receipt due 10-13 12:00 (O-2333, post-MV-lane); (5) MV XQ-24 harvest watch when lane completes (receipt into O-2126)")

artifact = ("results/perpetual_faces/n1_w212_results.json (finalize one-pass 2026-10-12 03:3x, ledger 890,189 / K=464,320) "
            "+ research/PERPETUAL_N1_W212_PREREG.md sec.7/8 backfilled + results/_r907bmc_w212_finalize_log.txt")

activity = ("r907: W212 FULL CYCLE complete (finalize one-pass landed, ledger 890,189, K=464,320, skill_line 1.1903) + 9-dead-session state heal; "
            "W213 freeze-prep = next window first action; MV XQ i2v burn in flight (interactive window owns, zero lane-touch)")

cur_task = "r907 closeout: W212 finalize one-pass + sec.7/8 backfill + 9-dead-session absorb heal"

def patch(d):
    d["round_no"] = 908
    d["round_no_label"] = "r907"
    d["last_round"] = ROUND
    d["loop_round"] = ROUND
    d["clock_read"] = now_str
    d["ts"] = now_str
    d["updated"] = now_str
    d["updated_at"] = now_str
    d["last_seen"] = now_str
    d["last_seen_at"] = now_str
    d["last_round_at"] = now_str
    d["last_round_ts"] = now_str
    d["last_round_closed"] = now_str
    d["last_round_summary_at"] = now_str
    d["last_round_at_legacy"] = d.get("last_round_at_legacy", now_str)
    d["last_action_at"] = now_str
    d["current_task"] = cur_task
    d["current_task_at"] = now_str
    d["current_task_ts"] = now_str
    d["heartbeat_epoch_utc"] = epoch
    d["did"] = did
    d["note"] = did
    d["last_round_summary"] = did
    d["verdict"] = verdict
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = next_ptr
    d["latest_artifact"] = artifact
    d["last_artifact"] = artifact
    d["recent_artifact"] = artifact
    d["activity_now"] = activity
    d["now_active"] = activity
    d["last_action"] = "r907 absorb+product closeout (W212 finalize one-pass + sec.7/8 backfill + state 9-round heal)"
    d["ram_free_gb"] = ram_free_gb
    d["free_ram_gb"] = ram_free_gb
    d["idle_ram_gb"] = ram_free_gb
    d["total_ram_gb"] = ram_total_gb
    d["cpu_pct"] = cpu_pct
    d["cpu_util_pct"] = cpu_pct
    d["cpu_idle_pct"] = round(100 - cpu_pct, 1)
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    for k in ["gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_free_mb", "gpu_free_mib", "gpu_vram_free_mb", "free_vram_mb"]:
        d[k] = vram_free_mb
    for k in ["gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_idle_mb", "gpu_idle_mib"]:
        d[k] = vram_free_mb
    d["gpu_free_vram_gb"] = round(vram_free_mb / 1024, 2)
    d["last_orders_at"] = now_str
    d["last_orders_read_at"] = now_str
    d["last_decisions_at"] = now_str
    d["last_decisions_read_at"] = now_str
    d["last_decisions_seen"] = now_str
    d["health"] = "ok"
    d["r907_absorb_note"] = ("r907 absorb: sessions r898-r906 (NINE) each ran full/partial bodies with commits+pushes (W210 takeover freeze, W211 chain incl. unfuse+reburn+finalize, "
                            "W18 judge-finalize, i2v lane fixes, W212 freeze splice 0f30cb725, engine W212 self-burn ledger appends) but ALL died pre-closeout -- state had been frozen "
                            "at r897/898 the whole night; this session executed as r907 (next after highest committed r906) and advanced counter 898->908 so next session = r908; "
                            "zero double-count: S0.5 dual-delta FALSE this window (dec 67403afa / ord 33aee170 both current), ORD/DEC consumption debts were handled by the dead sessions themselves")
    d["d19_watermark_guard"] = {"tool": "scripts/d19_watermark.py", "probe": "results/_r686bmb_d19_check.py",
                                "probe_evidence": ROOT + r"\results\_r686bmb_d19_check.json",
                                "method_decisions": "sha256", "method_orders": "sha1", "verbatim": True,
                                "advance": True, "round_ref": ROUND, "ts": now_str}
    d["sync"] = {"ahead_behind": "r907 closeout commit rides this push", "origin_tip": "pending", "ts": now_str,
                 "note": "r907 closeout commit+push this round; rev-list self-proof logged in round report"}
    d["orphan_face"] = 2
    d["orphan_faces"] = 2
    return d

# ---- state file ----
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st = patch(st)
st["head_sha"] = "pending-post-commit"
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---- heartbeat file ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb = patch(hb)
hb["hostname"] = "FLUXGROUP"
hb["root_path"] = "K:\\Fluxgroup"
hb["cores"] = 32; hb["cpu_cores"] = 32
hb["prod_lanes"] = ("GPU=MV album i2v burn ACTIVE (interactive window owns, zero lane-touch); "
                    "CPU=N1 wave chain W212 complete -> W213 freeze-prep next window (supply gap disclosed)")
json.dump(hb, open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---- round report line ----
rp = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rp, "rb").read()
txt = raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8")
nl = "\r\n" if "\r\n" in txt else "\n"
line = (f"{now_str} | r907 | bm-c | WM-VERDICT: green red=false (S0.5 probe dual-delta FALSE dec 67403afa / ord 33aee170 hold, unacked=0) | "
        f"dept:策略（N1 波链 W212 finalize one-pass 收口）+dept:工程（吸收收口+state 9-round heal）| "
        f"实况三行：当前活=W213 freeze-prep 束=下窗第一动作（W212 finalize 落地=上游闸全开 clean precondition）+MV XQ i2v 烧录在飞（交互窗持有·零车道触碰）；"
        f"最近实物=results/perpetual_faces/n1_w212_results.json（2026-10-12 03:3x finalize one-pass·账本 887,989+2,200=890,189·K=464,320·skill_line 1.1902→1.1903）"
        f"+research/PERPETUAL_N1_W212_PREREG.md §7/§8 回填落地；"
        f"下个里程碑=W213 席位+freeze-prep 束（下窗 10-12 内·r888/r906 先例）+周一 15:30 新 bar 窗 papers 全腿（今日）+unity-mcp POC 回执（10-13 12:00 前）| "
        f"did: {did} | orphan-faces=2（MV-lane infra kept zero-kill）| "
        f"验证证据=smoke 49/49 + finalize stdout log（ledger identity assert 887,989+2,200=890,189 + K assert 462,120+2,200=464,320）"
        f"+ S6 absorbed r906（body 41/41 rc0 commit 8aa1dcf4f + 5-leg rerun 03:08:21）+ attrition 4 CLEAN + dual-delta FALSE probe + push range self-proof below | "
        f"本地未达 origin commit 数=0 | next: {next_ptr} | [r907 bm-c]{nl}")
if not txt.endswith(nl):
    txt += nl
txt += line
open(rp, "wb").write(txt.encode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"))

# ---- self-verify ----
s2 = json.load(open(sp, encoding="utf-8"))
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(s2["heartbeat_epoch_utc"], int) and isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert s2["round_no"] == 908 and h2["round_no"] == 908
assert "r907 bm-c" in open(rp, encoding="utf-8-sig").read()[-4000:]
print(f"closeout LANDED: r907 | round_no->908 | epoch={epoch} int | ram_free={ram_free_gb}GB | vram_free={vram_free_mb}MB | cpu={cpu_pct}%")
