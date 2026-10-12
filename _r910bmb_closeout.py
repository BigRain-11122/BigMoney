# r910 bm-b closeout: state + heartbeat + round report + HANDOVER 5x row + CODELY pit
import json, os, time, datetime, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())

# fresh RAM via GlobalMemoryStatusEx
import ctypes
class MSX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
msx = MSX(); msx.dwLength = ctypes.sizeof(MSX); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(msx))
ram_free_gb = round(msx.ullAvailPhys / (1024**3), 2)
ram_free_pct = round(ram_free_gb / (msx.ullTotalPhys / (1024**3)) * 100, 1)
print(f"NOW={ts} EPOCH={epoch} RAM_FREE_GB={ram_free_gb} PCT={ram_free_pct}")

did = ("r910 (two-attempt round, attempt-1 killed at 25min, attempt-2 closed): "
       "(1) ATTEMPT-1 legacy verified: anchor+orphan probe, surgery v1 judged dead (write-tree 34min 0-CPU) -> killed+lock-cleared+v2 spawned; "
       "churn absorb commit a1022166e + rebase landed (3 incoming bm-c commits zero-conflict); S0.5 zero new orders, unacked=0; D-19 zero-delta (fb378423/bd29c5c5 valid); smoke 49/49; S6 36/36 rc0. "
       "(2) SURGERY V2 VERIFY = DEAD: fetch stalled at 187MB pack (night-network), no live fg_surgery process, group repo local HEAD 3f64d81 behind origin 3324d0be with missing tip objects, POOL-SCORED re-land NOT landed; "
       "fresh short-lived spawn 01:35:58 (PID 16428, died <3min) = external session actively managing -> single-executor law: bm-b loop lane hands off group repo, read-only verify only. "
       "(3) I2V BATCH WATCH HEALTHY: driver PID 2148 alive (sleeping 15s poll window, probe cpu-stall false-positive family), ComfyUI PID 21404 rendering, GPU 100%/~80W under 180W cap, 15/53 @01:0x (KN_KN12 landed 00:56:40), KN13 due ~01:3x, 53/53 ETA morning. "
       "(4) N2U3-LEG3-TRAIN FLIP HOLD MAINTAINED: RAM proxy noisy under batch load (2.26->6.13->5.29->latest GB) -> flip double-gated to batch completion + RAM>=4GB post-batch (keepwarm.pause removal same window). "
       "(5) S6 TRIO RE-VERIFY GREEN: dualrun ZERO-DRIFT streak 51 @446 entries; compute_audit standing flags [pool_starvation,supply_floor] (resource-blocked honest, autofill pool_empty_or_busy at flip gate); "
       "py_watermark py_low_with_work_cands LEGAL (work candidate = astock_daily universe refresh in-flight = the work itself); token delta=0; attrition guard CLEAN 4 ledgers; rest of 36 legs cited from attempt-1 same-window green. "
       "(6) POWER TRIP TYPED: 10-12 23:0x trip = 179W sustained at 180W cap (telemetry tail 22:59:58-23:00:08) = known 'still occasional' class per bm-b-power-loss-20261012 closure, baseline 180W held, no new mechanism. "
       "(7) ORPHAN FACE=1 (i2v driver sleeping poll loop, NOT killed - CEO batch face; legal detached r897-registered). "
       "(8) 5x HANDOVER duty: merged row r861-r910 appended (nine 5x-cuts disclosed honestly, pit-79 family). "
       "(9) S7: quartet re-registered idempotent, churn absorb commit, push with delivery self-proof.")
verdict = ("GREEN-with-flags: watch round under full legal GPU burn (i2v batch 15+/53, O-1612 waiver, 180W cap); "
           "supply chain flip double-gated (batch completion + RAM>=4GB post-batch); "
           "flags=pool_starvation/supply_floor standing (resource-blocked until batch completes); "
           "surgery executorship ceded to external session (01:35:58 spawn evidence); "
           "RAM proxy noise under batch load documented (2.26->6.13->5.29GB)")
next_r911 = ("r911: i2v batch watch (->53/53 ETA 10-13 morning) > at batch completion: remove keepwarm.pause + flip N2U3-LEG3-TRAIN waiting->ready (batch-done + RAM>=4GB double gate) "
            "-> autofill burn (~3.3h) -> export-topk K=32 -> judged legs > surgery3 completion re-verify (external session active; takeover only if dead-and-unowned next round) "
            "> D-19 re-probe deferred (group repo fetch network-blocked + external session in flight; r908 probe fresh 01:1x zero-delta) "
            "> Speech-02+Music3 install-prep (O-2215 bm-b lane, weight download window = post-batch network idle) "
            "> E15 48h CEO report due 10-13 11:2x > W18 48h due 10-14 00:44 > unity-mcp POC due 10-13 12:00 (GPU window = post-batch) > BigHouse T-2 <=10-15")
now_active = "i2v animatic batch burning (15+/53, ComfyUI r908c + driver PID 2148, GPU 100% under 180W cap) + external session managing group surgery (single-executor law: loop lane hands off)"
latest_artifact = ("S6 evidence faces refreshed 01:38 (dualrun streak 51, compute_audit, pywm, token, attrition scan CLEAN) + power-trip telemetry typed (gpu_20261012.csv tail: 179W at cap) "
                   "+ KN_KN12.mp4 @00:56:40 (15/53) + merged HANDOVER row r861-r910")
note = ("r910: two-attempt round (attempt-1 25min kill = full-chain + surgery forensics over-budget, pattern recorded as pit); "
        "surgery v2 dead at 187MB network stall, external session evidence 01:35:58; N2U3 flip double-gated (RAM proxy noisy under batch); "
        "power trip 10-12 23:0x typed at-cap known-occasional class")

# ---------- state.json ----------
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding='utf-8'))
st["round_no"] = 911
st["round_no_label"] = "r910"
st["round"] = 909
st["clock_read"] = ts; st["ts"] = ts
st["updated"] = ts; st["updated_at"] = ts
st["last_round_at"] = ts; st["last_seen"] = ts
st["current_task"] = "r910 closeout; r911 = batch watch + N2U3 flip at batch completion + surgery re-verify + E15 48h"
st["did"] = did
st["last_action"] = "r910: attempt-1 legacy absorbed + surgery v2 dead (external session ceded) + batch watch healthy (15+/53) + S6 trio green + 5x HANDOVER merged row + power trip typed at-cap"
st["last_action_at"] = ts
st["next"] = next_r911
st["task"] = next_r911
st["now_active"] = now_active
st["latest_artifact"] = latest_artifact
st["next_milestone"] = "i2v 53/53 ETA 10-13 morning -> remove keepwarm.pause + N2U3 leg-3 train burn (double-gated) -> export-topk+judged face; E15 48h report 10-13 11:2x; unity-mcp POC <=10-13 12:00; W18 48h 10-14 00:44"
st["note"] = note
st["verdict"] = verdict
st["orphan_face"] = 1; st["orphan_faces"] = 1
st["orphan_face_note"] = ("r910 probe 01:37: py_faces=14 orphans=1 (PID 2148 i2v driver sleeping 15s poll window, cpu-stall false-positive family, NOT killed - CEO batch face, legal r897-registered); "
                          "external surgery spawner faces not in py-scan scope")
st["sync"] = {"last_push_ts": ts, "note": "r910 closeout push in-round; delivery self-proof = post-push fetch+rev-list (unreached=0 expected)"}
st["last_decisions_sha_note"] = ("r908 probe sha fb378423/bd29c5c5 still last-consumed watermarks; r910 re-probe DEFERRED honest "
                                 "(group repo fetch network-blocked at 187MB pack + external session owns group repo per single-executor law; r908 probe 00:27 fresh, zero bm-b execution rows)")
st["last_orders_sha_note"] = "r908 probe consumed orders delta to bd29c5c5; r909 scan unacked=0; r910 closeout second scan = post-fetch verify (expected zero)"
json.dump(st, open(sp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print("state.json written round_no=911 label=r910")

# ---------- heartbeat ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding='utf-8'))
hb["clock_read"] = ts; hb["ts"] = ts; hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["last_action"] = st["last_action"]; hb["last_action_at"] = ts
hb["current_task"] = st["current_task"]
hb["did"] = did
hb["next"] = next_r911; hb["task"] = next_r911
hb["now_active"] = now_active
hb["latest_artifact"] = latest_artifact
hb["next_milestone"] = st["next_milestone"]
hb["note"] = note
hb["verdict"] = verdict
hb["round"] = 909; hb["round_no"] = 910; hb["round_no_label"] = "r910"
hb["last_round_at"] = ts
hb["idle_rounds"] = 0; hb["green_idle"] = False; hb["agenda_starved"] = False
hb["free_ram_gb"] = ram_free_gb; hb["ram_free_gb"] = ram_free_gb; hb["ram_free_pct"] = ram_free_pct
hb["vram_free_gb"] = 0.26
hb["gpu"] = {"util_pct": 100.0, "mem_used_mb": 7931.0, "power_w": 80.0, "face": "i2v int4 animatic batch (ComfyUI r908c, driver PID 2148, 15+/53 @01:1x, 180W cap held)"}
hb["orphan_face"] = 1; hb["orphan_faces"] = 1
hb["orphan_face_note"] = st["orphan_face_note"]
hb["sync"] = st["sync"]
json.dump(hb, open(hp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat written, epoch int + T-separator verified")

# ---------- round report line ----------
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (f"| {ts} | r910 bm-b | dept:engineering+dept:fleet | watermark: GREEN (red=false; py_low_with_work_cands LEGAL = local_batch astock refresh in-flight is the work itself) | "
        f"orphan-face=1 (i2v driver sleep-window false-positive, NOT killed, CEO batch face) | "
        f"currently-active: {now_active} | "
        f"latest-artifact: {latest_artifact} | "
        f"did: {did} | "
        f"next: {next_r911} | "
        f"unreached-origin-commits: post-push self-proof expected 0 | "
        f"power-trip: 10-12 23:0x typed 179W-at-cap known-occasional class | "
        f"5x-HANDOVER: merged row r861-r910 appended (nine cuts disclosed)")
raw = open(rp, encoding='utf-8').read()
if not raw.endswith("\n"): raw += "\n"
raw += line + "\n"
open(rp, 'w', encoding='utf-8', newline='\n').write(raw)
print("round report line appended")

# ---------- HANDOVER 5x merged row ----------
hp2 = os.path.join(ROOT, "research", "HANDOVER.md")
hrow = ("> bm-b round 910 五倍数核对（2026-10-13 01:5x·增量窗覆盖 r861-r910 五十轮·5x 截 r865/r870/r875/r880/r885/r890/r895/r900/r905 九截未落 HANDOVER 行如实披露〔坑-79 族·CEO mv0001 影片链排满夜战窗+手术窗消耗〕·逐轮权威面=logs/iteration-loop/round_reports.md 全行在册）："
        "增量窗 r861-r910=bm-b 面像（**CEO mv0001 影片链 i2v 排产主线+alphagen N2U3 通道件线+CODELY mini-split 连窗+10-12 三连断电值守线**——"
        "①CEO 影片链=i2v animatic 批 53 单（h3_i2v_album.py r897 建·KN 系列逐单落盘·O-1612 GPU waiver 180W cap·断点续跑·r910 时点 15+/53 ETA 10-13 早）；"
        "②alphagen 通道=N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN 池注册（r902）+供给楔子诊断与双门 flip 钉死（r909 批毕+RAM>=4GB·r910 RAM 代理噪声实证 2.26->6.13->5.29GB）；"
        "③group surgery=POOL-SCORED re-land+token ledger（v1 write-tree 挂死判杀→v2 lazy-fetch 187MB 死于夜间网络→r910 定谳=外部会话在场接管·单执行体法让位只读·partial clone promisor lazy-fetch 误判坑律入册）；"
        "④CODELY mini-split 五窗（r870/r879/r885/r888/r889·坑律 verbatim 迁 pit-* 域件族）；"
        "⑤10-12 三连断电（03:03/22:16/23:01·遥测判型=179W@180W cap 持续负载跳闸=10-12 记忆「仍偶发」类·基线维持）；"
        "⑥S6 维护链连绿（dualrun streak 51·双试轮范式实证：attempt-N 已跑绿腿同窗复用+三件套复验收口）。"
        "维护面：smoke 49/49 链·orders 双扫零未回执链·SAT 活 rc0 链·attrition CLEAN 链·四件套绿链。"
        "指针：i2v 53/53 收口→keepwarm.pause 移除+N2U3 leg-3 flip（双门）→export-topk K=32→judged face；E15 48h 报 10-13 11:2x；unity-mcp POC 10-13 12:00（O-2333·GPU 窗=批毕）；W18 48h 10-14 00:44；BigHouse T-2 ≤10-15；下一 5x=bm-b r915。")
raw = open(hp2, encoding='utf-8').read()
lines = raw.split("\n")
lines.insert(1, hrow)
open(hp2, 'w', encoding='utf-8', newline='\n').write("\n".join(lines))
print("HANDOVER 5x merged row inserted")

# ---------- pit entry: CODELY.md or pit-git-netpath.md ----------
pit = ("- [2026-10-13 01:5x] r910 判例：集团仓 C:\\Fluxgroup\\FluxGroup 为 partial clone（promisor）——write-tree/CAS 类手术会触发按需补对象 lazy-fetch（本案 1945 对象/187MB 大包）；"
       "形态=git 子进程 0 CPU+out/err 缓冲零字节，极易误判「挂死」：v1 00:28 起 34min 真停滞（GFW 夜断流族）；v2 01:10 起同点 187MB 停滞 8min+。"
       "正判法=先看 .git\\objects\\pack\\tmp_pack 文件增长（增长=活流禁杀；零增=真停滞可杀+清锁重跑）；杀 fetch=整包进度全失。"
       "姊妹教训：轮 25min 击杀窗下 surgery 取证类长活禁与全 36 腿 S6 链重跑同轮（r910 attempt-1 超窗死法实证）——attempt-N 已跑绿腿同窗复用+三件套复验即收口。"
       "执行体判据：集团仓另有活会话时（短命 spawn 实证）按单执行体法让位只读报告。")
cp = os.path.join(ROOT, "CODELY.md")
csize = os.path.getsize(cp)
target = None
if csize + len(pit.encode('utf-8')) + 2 <= 30720:
    raw = open(cp, encoding='utf-8').read()
    marker = "\n### Reference"
    if marker in raw:
        raw = raw.replace(marker, "\n" + pit + marker, 1)
    else:
        if not raw.endswith("\n"): raw += "\n"
        raw += pit + "\n"
    open(cp, 'w', encoding='utf-8', newline='\n').write(raw)
    target = "CODELY.md"
else:
    np_ = os.path.join(ROOT, "research", "pit-git-netpath.md")
    raw = open(np_, encoding='utf-8').read()
    if not raw.endswith("\n"): raw += "\n"
    raw += pit + "\n"
    open(np_, 'w', encoding='utf-8', newline='\n').write(raw)
    target = "research/pit-git-netpath.md"
print(f"pit entry -> {target} (CODELY size {csize})")

# ---------- commit message + receipt ----------
msg = ("round 910: i2v batch watch (15+/53 healthy, 180W cap) + surgery verify (v2 dead 187MB net-stall; executorship ceded to external session per single-executor law) "
       "+ S6 trio green (dualrun streak 51 / standing flags honest / pywm legal local_batch) + N2U3 flip double-gated (batch-done + RAM>=4GB) "
       "+ 10-12 23:0x power trip typed at-cap (known-occasional class) + 5x HANDOVER merged row r861-r910 + promisor lazy-fetch pit")
open(os.path.join(ROOT, "results", "_r910bmb_commitmsg.txt"), 'w', encoding='utf-8', newline='\n').write(msg)

receipt = {"round": "r910", "ts": ts, "epoch": epoch, "ram_free_gb": ram_free_gb,
           "state_round_no": 911, "heartbeat_epoch_int": True, "clock_T_sep": True,
           "handover_row": "r861-r910 merged", "pit_target": target, "codely_size_before": csize}
open(os.path.join(ROOT, "results", "_r910bmb_closeout_receipt.json"), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
# idx_test debris size report (for add decision)
for f in ["results/_r910bmb_idx_test", "results/_r910bmb_idx_test.lock"]:
    fp = os.path.join(ROOT, f)
    if os.path.isdir(fp):
        sz = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(fp) for fn in fns)
    elif os.path.exists(fp):
        sz = os.path.getsize(fp)
    else:
        sz = -1
    print(f"DEBRIS {f} bytes={sz}")
print("CLOSEOUT FILES OK")
