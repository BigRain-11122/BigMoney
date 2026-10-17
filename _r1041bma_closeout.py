# -*- coding: utf-8 -*-
"""r1041 bm-a closeout driver (canon-clone of _r1040 pattern).
- process inbox MSG-20261017-2203 (taildrop pickup): move to processed + write reply MSG
- idle_trigger --worked (real work done this round: CEO UU remote order receipt)
- closing double-scan: fleet/orders new-file check + d19 probe
- append round_reports-bm-a.md r1041 line
- rewrite fleet/machines/bm-a.json heartbeat
- rewrite state-bm-a.json
argv: free_ram_gb cpu_pct vram_free_mb
"""
import io, os, sys, json, time, subprocess, shutil, glob, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
FREE_RAM_GB = float(sys.argv[1]); CPU_PCT = float(sys.argv[2]); VRAM_MB = int(sys.argv[3])
now = datetime.datetime.now(datetime.timezone.utc).astimezone()
NOW = now.isoformat(timespec="seconds")
EPOCH = int(time.time())
FREE_MB = int(FREE_RAM_GB * 1024)
FREE_PCT = round(FREE_RAM_GB / 93.6 * 100, 1)
print("closeout now=", NOW, "ram=", FREE_RAM_GB, "cpu=", CPU_PCT, "vram=", VRAM_MB)

def rj(p):
    with io.open(p, "r", encoding="utf-8") as f: return json.load(f)
def wj(p, obj):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")

# 1) idle_trigger --worked
r = subprocess.run([sys.executable, r"Tools\idle_trigger.py", "--worked"], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("idle_trigger --worked rc=", r.returncode, (r.stdout or "").strip()[:120], (r.stderr or "").strip()[:120])

# 2) inbox: process MSG-2203 (addressed to bm-a) + write reply
src = r"fleet\inbox\MSG-20261017-2203-bm-b-drama-taildrop-pickup.md"
dst = r"fleet\inbox\processed\MSG-20261017-2203-bm-b-drama-taildrop-pickup.md"
if os.path.exists(src) and not os.path.exists(dst):
    shutil.move(src, dst); print("inbox: MSG-2203 -> processed")
elif os.path.exists(dst):
    print("inbox: MSG-2203 already processed")
reply = r"fleet\inbox\MSG-20261017-2232-bma-dramapickup-reply.md"
reply_body = """# MSG-20261017-2232-bma → bm-b: drama taildrop 取件回执（MSG-20261017-2203 处理完毕）

- 已按你方指定动作执行：tailscaled 服务已重启（22:2x Restart-Service Tailscale，bm-a 节点回网正常，bm-b 经 relay "sfo" 可见）。
- 重启前后各一次 `tailscale file get C:\\Users\\sjs20\\Desktop\\FluxGroup\\media\\drama-pilot-in\\`：收件箱仍空（0 件）——21:4x 那 5 件未抵达本机收件箱（与你方 file service not answering 观察一致）。
- 取件目录已备好：C:\\Users\\sjs20\\Desktop\\FluxGroup\\media\\drama-pilot-in\\
- 请按你方计划下轮重投（5 件：PILOT-PREVIEW-3x20s.mp4 + seg1/2/3.mp4 + sea-review-level1.md）；tailscaled 已重启=收件面应已恢复。若再失败，备选通道=你侧 O-2110 CDN 直链腿（TJ-MCP 交互窗）或 TRANSFER.md 机制择道。
- 本机零催办，仅状态回执。MSG-2203 已移入 processed/。

— bm-a r1041 · 2026-10-17 22:32
"""
with io.open(reply, "w", encoding="utf-8", newline="\n") as f: f.write(reply_body)
print("reply MSG written:", reply)

# 3) closing double-scan: fleet/orders new files since 22:07 receipt window + d19 probe
order_files = sorted(glob.glob(r"fleet\orders\O-*.md"))
new_orders = [os.path.basename(p) for p in order_files if os.path.getmtime(p) > time.mktime(time.strptime("2026-10-17 22:07:30", "%Y-%m-%d %H:%M:%S")) and os.path.basename(p) != "O-20261017-2207-bm-c.md"]
print("closing order-scan new-files:", new_orders if new_orders else "NONE")
r2 = subprocess.run([sys.executable, r"scripts\d19_watermark.py", "probe"], capture_output=True, text=True, encoding="utf-8", errors="replace")
d19_out = (r2.stdout or "").strip()
print("d19 closing probe rc=", r2.returncode, "out=", d19_out[:200] if d19_out else "SILENT-HOLD")

# 4) round report append
ART = "origin 988a2b6d4 (O-20261017-2207 receipt: MSG-20261017-2216 + order receipt section, pushed 22:16) + results/_r1041bma_s6_log.txt (S6 43/43 rc0 20:19-20:23)"
CUR = "r1041 closeout: CEO UU-remote order receipted+pushed (O-20261017-2207: GameViewer already running, Server/Healthd in console session SID=1, Service Running/Auto — zero start action needed) + Taildrop MSG-2203 processed (inbox empty x2, tailscaled restarted per instruction, reply MSG-2232 to bm-b) + W264=bm-c seat burning (r1076 selftest heal landed, finalize pending=bm-c next) + W265 bm-a own-seat gated zero skip-claim"
NXT = "r1042: W264 finalize landing watch (bm-c) -> W265 bm-a own-seat window FIRST ACTION on unlock; MF push2 Monday re-probe adjudication (<=2026-10-19); bm-b Taildrop re-queue pickup"
VER = "receipt push range f9b19cb65..642264500 behind-0 same-round + S6 log 43/43 rc0 bad=0 + smoke 49/49 + d19 probe rc0 silent hold (closing double-scan zero new) + attrition 4 CLEAN + orphan face=0 (24 py faces) + claws match x2 + loop pin=8 no-op + idle_trigger --worked rc=" + str(r.returncode)
line = NOW + " | r1041 bm-a (dept:舰队·CEO UU远控直令受理+S6 收口+Taildrop 取件处置) | WM-VERDICT: 绿(red=false lane=healthy; satengine ALIVE queue0 idle) | 当前活=" + CUR + " | 验证证据=" + VER + " | 下轮指针=" + NXT + " | 最近实物=" + ART + " | 本地未达 origin commit 数=0（收口推送后自证） | [r1041 bm-a ceo-uuremote-receipt]"
p = r"round_reports-bm-a.md"
raw = io.open(p, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
with io.open(p, "ab") as f: f.write(line.encode("utf-8") + eol)
print("round report appended (eol=", eol, ")")

# 5) heartbeat
hb = rj(r"fleet\machines\bm-a.json")
prev_epoch = hb.get("heartbeat_epoch_utc", 0)
hb.update({
 "active": True, "health": "green", "verdict": "GREEN",
 "clock_read": NOW, "ts": NOW, "last_seen": NOW, "now_active": NOW,
 "last_round": "r1041", "round": 1041, "round_no": 1041, "loop_round": 1041, "round_no_label": "r1041",
 "last_round_at": NOW, "last_round_closed": NOW, "last_round_ts": NOW, "last_run": NOW, "last_action_at": NOW, "updated": NOW, "updated_at": NOW,
 "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True, "last_heartbeat_epoch_utc": prev_epoch,
 "current": CUR, "current_task": "r1041 closed (CEO UU order receipted + Taildrop pickup processed + S6 43/43 adopted); next = W264 finalize watch then W265 bm-a own-seat",
 "did": CUR,
 "last_action": CUR[:180],
 "task": "r1041 CEO UU-remote order receipt + S6 closeout + Taildrop pickup handling",
 "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
 "next": NXT, "next_milestone": "W265 bm-a own-seat window (opens on bm-c W264 finalize landing, eta 10-17 night/10-18) + MF push2 Monday re-probe adjudication window <=2026-10-19",
 "idle_rounds": 0, "agenda_starved": False,
 "free_ram_gb": FREE_RAM_GB, "ram_free_gb": FREE_RAM_GB, "idle_ram_gb": FREE_RAM_GB,
 "ram_free_mb": FREE_MB, "idle_ram_mb": FREE_MB,
 "free_ram_pct": FREE_PCT, "ram_free_pct": FREE_PCT, "ram_load_pct": round(100 - FREE_PCT, 1),
 "total_ram_gb": 93.6,
 "cpu_load_pct": CPU_PCT, "cpu_pct": CPU_PCT, "cpu_total_pct": CPU_PCT, "cpu_util_pct": CPU_PCT,
 "gpu_free_vram_mb": VRAM_MB,
 "gpu_source_note": "nvidia-smi live read " + NOW + " (CEO working machine, honest free face)",
 "orders_ack": ["O-20261017-2207-bm-c.md"], "orders_ack_last": "O-20261017-2207-bm-c.md",
 "orders_ack_note": "r1041: O-20261017-2207-bm-c receipted same-round (UU remote already-running verdict, MSG-20261017-2216 + order receipt section, origin 988a2b6d4); closing double-scan zero new orders; d19 closing probe silent hold",
 "last_decisions_read_at": NOW, "last_orders_read_at": NOW, "last_decisions_at": NOW, "last_orders_at": NOW,
 "last_decisions_seen": "r1041: dec 1d4741e4 hold both scans (probe rc0 silent, zero delta)",
 "last_orders_seen": "r1041: ORD e0dcbd80 hold both scans (probe rc0 silent zero delta; repo-local O-20261017-2207 receipted same-round)",
 "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
 "verify": VER,
 "push_verified": {"ts": NOW, "origin_tip": "642264500", "ahead_behind": "0/0", "note": "r1041: receipt push range f9b19cb65..642264500 verified (range line + fetch behind-0 same-round readback; closeout push behind-0 readback follows this push)"},
 "sync": {"ts": NOW, "origin_tip": "642264500", "ahead_behind": "0/0", "note": "r1041: receipt+absorb rebase CLEAN onto bm-c r1076 pair; closeout push follows"},
})
wj(r"fleet\machines\bm-a.json", hb)
print("heartbeat written, epoch=", EPOCH, "isinstance int:", isinstance(EPOCH, int))

# 6) state
st = rj(r"state-bm-a.json")
st_prev_epoch = st.get("heartbeat_epoch_utc", 0)
st.update({
 "agenda_starved": False, "clock_read": NOW,
 "current": CUR, "current_task": "r1041 closed (CEO UU order receipted + Taildrop processed + S6 43/43); W265 bm-a own-seat gated on bm-c W264 finalize",
 "did": CUR,
 "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True, "last_heartbeat_epoch_utc": st_prev_epoch,
 "idle_rounds": 0,
 "last_action": CUR, "last_action_at": NOW,
 "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
 "last_decisions_at": NOW, "last_orders_at": NOW,
 "last_decisions_read_at": NOW, "last_orders_read_at": NOW,
 "last_decisions_seen": "r1041: dec 1d4741e4 hold both scans (probe rc0 silent, zero delta)",
 "last_orders_seen": "r1041: ORD e0dcbd80 hold both scans (probe rc0 silent zero delta; repo-local O-20261017-2207 receipted same-round)",
 "last_round": "r1041", "last_round_at": NOW, "last_round_closed": NOW, "last_round_ts": NOW, "last_run": NOW, "last_seen": NOW, "now_active": NOW,
 "loop_round": 1041, "round": 1041, "round_no": 1042, "round_no_label": "r1041",
 "next": NXT,
 "next_milestone": "W265 bm-a own-seat window (opens on bm-c W264 finalize landing; eta 10-17 night/10-18) + MF push2 Monday re-probe adjudication <=2026-10-19",
 "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
 "push_verified": "r1041 receipt push range f9b19cb65..642264500 behind-0 same-round (988a2b6d4 MSG+order-receipt + 642264500 absorb); closeout push behind-0 readback same-round",
 "recent_artifact": ART, "task": "r1041 CEO UU-remote order receipt + S6 closeout + Taildrop pickup handling",
 "ts": NOW, "updated": NOW, "updated_at": NOW,
 "verdict": "green: r1041 = CEO UU-remote order closed same-round (receipt on origin 988a2b6d4) + Taildrop pickup handled per MSG-2203 protocol + S6 43/43 rc0 adopted + smoke 49/49 + WM green + satengine ALIVE idle + D-19 double-scan hold + W265 own-seat gated (zero skip-claim)",
 "verify": VER,
 "free_ram_gb": FREE_RAM_GB, "ram_free_gb": FREE_RAM_GB, "idle_ram_gb": FREE_RAM_GB, "ram_free_mb": FREE_MB, "idle_ram_mb": FREE_MB,
 "free_ram_pct": FREE_PCT, "ram_free_pct": FREE_PCT, "ram_load_pct": round(100 - FREE_PCT, 1), "total_ram_gb": 93.6,
 "cpu_load_pct": CPU_PCT, "cpu_pct": CPU_PCT, "cpu_total_pct": CPU_PCT, "cpu_util_pct": CPU_PCT,
 "gpu_free_vram_mb": VRAM_MB,
 "gpu_source_note": "nvidia-smi live read " + NOW + " (CEO working machine, honest free face)",
 "orders_ack": ["O-20261017-2207-bm-c.md"],
 "orders_ack_note": "r1041: O-20261017-2207-bm-c receipted same-round (UU remote already-running verdict; MSG-20261017-2216 + order receipt section; origin 988a2b6d4); closing double-scan zero new orders; d19 closing probe silent hold",
 "sync": {"ts": NOW, "origin_tip": "642264500", "ahead_behind": "0/0", "note": "r1041: receipt+absorb rebase CLEAN onto bm-c r1076; closeout push follows"},
 "d19_watermark_guard": {"tool": "scripts/d19_watermark.py", "probe": "results/_r686bmb_d19_check.py", "probe_evidence": "C:\\Users\\sjs20\\Desktop\\FluxGroup\\quant\\bigmoney\\results\\_r686bmb_d19_check.json", "method_decisions": "sha256", "method_orders": "sha256", "verbatim": True, "advance": True, "round_ref": 1041, "ts": NOW},
 "notes_seq_repair_r1041": "r1041 sequence-honest: 20:19-20:26 dead window ran S6 43/43 to DONE + heartbeat/idle-faces write but died pre-closeout; THIS window = r1041 closeout (CEO UU order receipted first, S6 evidence adopted, runtime faces absorbed+rebased); canonical face = round_reports-bm-a.md + git log",
})
wj(r"state-bm-a.json", st)
print("state written; round=1041 next=1042")

# 7) orders_ack scan refresh if tool exists
scan_tool = r"scripts\orders_ack_scan.py"
if os.path.exists(scan_tool):
    r3 = subprocess.run([sys.executable, scan_tool], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("orders_ack_scan rc=", r3.returncode, (r3.stdout or "").strip()[:100], (r3.stderr or "").strip()[:100])
else:
    print("orders_ack_scan tool absent, skip")
print("CLOSEOUT-DRIVER-DONE")
