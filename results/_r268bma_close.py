"""r268 bm-a closeout: state-bm-a.json + heartbeat + round report line.
Byte-face mirror law (R254/R255/R257): both JSONs probed = no BOM, CRLF lines,
indent=1, ensure_ascii=False (raw UTF-8), NO trailing newline.
Round report file = BOM + CRLF, trailing newline present; append one CRLF line.
Heartbeat epoch = python int (R170/R178); clock_read = isoformat() T-separator (R262).
"""
import json, time, subprocess
from datetime import datetime

now = datetime.now().astimezone()
now_s = now.strftime("%Y-%m-%d %H:%M")
clock = now.isoformat()
epoch = int(time.time())

def cpu_ram():
    try:
        import psutil
        return psutil.cpu_percent(interval=1), round(psutil.virtual_memory().available / (1024**3), 1)
    except Exception:
        return None, None

cpu_pct, free_ram_gb = cpu_ram()
gpu_free = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    gpu_free = round(int(out[0]) / 1024, 1)
except Exception:
    pass

# --- state-bm-a.json ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 268
st["did"] = ("R268 O-2000 migration continuation: v1 triple-abort postmortem (journal: 20:19 XML-empty / "
             "20:21 BigLife stash-face / 20:22 disable-first 40min wait on permanent interactive holder) + "
             "stash-limbo 3-repo rescue (root 12 lines restored incl untracked audit-charter/external-audit/t22 WIP; "
             "BigLife pop+drop; bigmoney pop refused by live watchdog face = r252 superseded-face law, archived "
             "results/_r268bma_autofill_stash_archive.patch then dropped) + executor v2 (precheck-first interactive "
             "wait BEFORE any mutation = zero-freeze; sentinel/refresh-puller kill-list; soft-unwind internal retry; "
             "PID lock single-instance; deadline 2026-09-29 12:00) launched detached PID 66552, precheck waiting on "
             "CEO editor (Code.exe+Tuanjie.exe) = zero mutation")
st["verdict"] = ("R268: watermark insufficient_history (new window n=1 honest); audit pool_starvation = O-1137 "
                 "legal-idle standing adjudication (weekend no-new-bar, board 0 open, bandit 0, pool 49/49 done, "
                 "MF_IC_P1 awaits moneyflow panel 53/5222 source-blocked); smoke 25/25; post_review 29 YES/0 NO/5 WAIT; "
                 "orders 84/84 acked zero diff; S6 25 legs exit 0")
st["next"] = ("(1) S0 FIRST: migration state check -- new root C:\\Fluxgroup present -> five-receipt assembly per O-2000 "
              "(receipt=results/fluxgroup_migration_receipt_bma.json) + first push from new root; absent -> journal tail "
              "+ lock PID 66552 liveness; if v2 dead and window open (deadline 09-29 12:00) relaunch "
              "results/_r268bma_fluxgroup_migration_v2.ps1 detached; (2) 09-28 Mon new-bar chain (cutoff 09-24); "
              "(3) MF_IC_P1 on moneyflow panel completion; (4) 10-01 monthly trio + REGIME_GUARD v3 date gate")
st["ts"] = now_s; st["last_round_ts"] = now_s; st["updated_at"] = now_s
st["current_task"] = "R268 closed (O-2000 executor v2 armed + stash-limbo rescue); migration auto-fires on CEO editor close"
st["last_run"] = now_s; st["last_round_at"] = now_s; st["last_round"] = 268; st["updated"] = now_s
open(sp, "wb").write(json.dumps(st, ensure_ascii=False, indent=1).replace("\n", "\r\n").encode("utf-8"))

# --- heartbeat ---
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = now_s
hb["current_task"] = st["current_task"]
hb["cpu_pct"] = cpu_pct if cpu_pct is not None else hb.get("cpu_pct")
hb["free_ram_gb"] = free_ram_gb if free_ram_gb is not None else hb.get("free_ram_gb")
hb["free_ram_mb"] = int(free_ram_gb * 1024) if free_ram_gb else hb.get("free_ram_mb")
hb["idle_ram_gb"] = hb["free_ram_gb"]
if gpu_free is not None:
    hb["gpu_free_vram_gb"] = gpu_free
    hb["gpu_idle_vram_gb"] = gpu_free
    hb["gpu_idle_vram_mb"] = int(gpu_free * 1024)
    hb["gpu0_free_vram_gb"] = gpu_free
    if isinstance(hb.get("gpu"), dict):
        hb["gpu"]["idle_vram_free_gb"] = gpu_free
hb["verdict"] = ("GREEN R268: O-2000 executor v2 armed (precheck-first, waiting on CEO editor close, deadline 09-29 12:00, "
                 "zero mutation while waiting), stash-limbo 3-repo rescue done zero-loss, smoke 25/25, S6 25 legs exit 0 "
                 "(weekend no-ops, OPT rank + AH panel spawns self-healing), post_review 29/0/5, orders 84/84, board 0 open")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 268
hb["task"] = ("R268: v1 triple-abort postmortem + stash rescue + executor v2 launch (PID 66552 precheck waiting); "
              "next = S0 migration-state check (receipt assembly or v2 relaunch), 09-28 new-bar chain, MF_IC_P1, 10-01 trio")
open(hp, "wb").write(json.dumps(hb, ensure_ascii=False, indent=1).replace("\n", "\r\n").encode("utf-8"))

# --- round report line (BOM+CRLF file, append one CRLF line) ---
line = (
    "2026-09-26 21:2x | R268 bm-a | (dept:\u5de5\u7a0b/\u8230\u961f) \u6c34\u4f4d=insufficient_history\uff08probe \u65b0\u7a97 n=1 \u8bda\u5b9e\u77ed\u7a97\uff1b"
    "\u5ba1\u8ba1\u65d7 pool_starvation=R266/R267 \u540c\u9762 O-1137 legal-idle \u767d\u540d\u5355\uff1a\u5468\u672b\u65e0\u65b0 bar\u3001\u677f 0 open\u3001bandit 0\u3001\u6c60 49/49 done\u3001"
    "MF_IC_P1 \u5f85 moneyflow \u9762\u677f 53/5222 \u6e90\u963b\u65ad\u81ea\u6108\u2014\u2014\u7981\u9020\u6570\u51d1\u70e7\u6052\u5728\uff09\u3002did: O-2000 \u8fc1\u79fb\u7eed\u6218\u4e3b\u95ed\u73af\u2014\u2014v1 \u4e09\u8d25\u6536\u5c38\uff08journal \u5b9e\u8bc1\uff1a20:19 XML \u7a7a\u4ef6\uff08cmd \u5d4c\u5957\u5f15\u53f7\u5df2\u4fee\uff09/"
    "20:21 BigLife stash \u4e0d\u51c0\uff08record-only \u5df2\u6539\uff09/20:22 disable-first 40min \u65e0\u754c\u7b49\u5728 Code.exe+PopupWitness \u540e 21:03 ABORT\u2014\u2014\u4f46 abort \u672a\u56de pop \u5df2\u626b\u79bb stash=\u4e09\u4ed3\u5de5\u4f5c\u6811\u9759\u9ed8\u5931\u8054\uff09\uff1b"
    "stash \u60ac\u7a7a\u4e09\u4ed3\u56de\u6551\uff08root pop 12 \u884c\u96f6\u4e22\u5931\u542b audit-charter/external-audit/t22 WIP \u672a\u8ddf\u8e2a\u4ef6\u3001BigLife pop+drop\u3001"
    "bigmoney pop \u88ab\u62d2=watchdog \u6d3b\u5199\u624b\u88ab\u8d85\u8d8a\u9762 r252 \u5f8b\u2192\u5b58\u6863 _r268bma_autofill_stash_archive.patch+drop\uff09\uff1b"
    "\u6267\u884c\u5668 v2 \u91cd\u8bbe\u8ba1+\u70b9\u706b\uff08precheck-first\uff1a\u4ea4\u4e92\u9762 Code/Tuanjie \u63a2\u6d4b\u5148\u4e8e\u4efb\u4f55\u7a81\u53d8=\u7b49\u5f85\u671f\u96f6\u51bb\u7ed3\u3001"
    "\u54e8\u5175/\u5206\u79bb\u5237\u65b0\u817f kill-list\uff08checkpoint \u81ea\u6108\u8bbe\u8ba1\uff09\u3001\u8f6f\u89e3\u7ed5\u5185\u90e8\u91cd\u8bd5\u3001PID \u9501\u5355\u5b9e\u4f8b 66552\u3001deadline 09-29 12:00 \u786c\u9876\uff1b"
    "\u626b\u63cf\u7ba1\u7ebf\u5f53\u573a\u5b9e\u8bc1 9 \u8fdb\u7a0b\u6b63\u786e\u5206\u7c7b\uff1bdetached precheck \u7b49\u5f85\u4e2d=\u96f6\u7a81\u53d8\uff0cCEO \u5173\u7f16\u8f91\u5668\u5373\u81ea\u52a8\u89e6\u53d1\uff09\uff1b"
    "S0.5 \u53cc\u626b orders 84/84 \u96f6\u5dee\u96c6+decisions \u96f6\u65b0\u884c\uff08P-32 \u96f6\u52a8\u4f5c\uff09\uff1bS1 smoke 25/25\uff1bS2 job_list \u7a7a+\u677f 0 open\uff0830 \u7968\u5168 claimed\uff09+inbox 0\uff1b"
    "S6 25 legs ALL exit 0\uff08\u5468\u672b no-op \u65cf\u3001OPT rank-spawn+AH panel spawn \u81ea\u6108\u4e2d\u3001fund_premium/alloc=\u4ed6\u673a\u8f66\u9053\u8bda\u5b9e no-op\u3001"
    "\u5468\u516d\u65e0\u65b0 bar\u2192live.paper/t35v/t24 \u6761\u4ef6\u817f\u5408\u6cd5\u8df3\u8fc7\uff09\uff1bpost_review 29 YES/0 NO/5 WAIT \u96f6\u2717\uff1b"
    "CODELY \u70ed\u51b7\u6574\u7f16 r268 \u6279\uff0851,363B\u219229.1KB\u00b726 \u6668\u6279\u5751\u5f8b\u884c\u5165 202609 \u51b7\u5c42 multiset \u96f6\u4e22\u5931+form-feed \u8f6c\u4e49\u8150\u8680\u81ea\u4fee+\u672c\u673a autocrlf \u4f20\u8f93\u9762\u5f52\u4e00\u96f6 diff\uff09"
    "\uff5cevidence: journal C:\\Users\\sjs20\\fluxgroup-migration-journal.log+results/_r268bma_fluxgroup_migration_v2.ps1+_r268bma_recompile.py "
    "gates \u5168 PASS+archive patch+smoke 25/25+S6 exit codes in transcript+post_review.jsonl \u672c\u8f6e run \u884c"
    "\uff5cnext: (1) \u4e0b\u8f6e S0 \u9996\u67e5\u8fc1\u79fb\u6001\uff1aC:\\Fluxgroup \u5728\u4f4d\u2192\u4e94\u4ef6\u56de\u6267\u7ec4\u88c5\uff08receipt=results/fluxgroup_migration_receipt_bma.json\uff09+\u65b0\u6839\u9996\u63a8\uff1b"
    "\u672a\u5728\u4f4d\u2192journal tail+lock 66552 \u6d3b\u6027\u6838\uff0cv2 \u6b7b\u800c\u7a97\u672a\u5c3d=\u91cd\u53d1 v2\uff1b(2) 09-28 \u5468\u4e00\u65b0 bar \u94fe\uff08cutoff 09-24\uff09\uff1b(3) MF_IC_P1 \u9762\u677f\u5b8c\u5907\uff1b(4) 10-01 \u6708\u9996\u8f6e\u4e09\u4ef6\u5957"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "ab") as f:
    f.write((line + "\r\n").encode("utf-8"))

# --- self-verify ---
s2 = json.loads(open(sp, "rb").read().decode("utf-8"))
h2 = json.loads(open(hp, "rb").read().decode("utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"], "clock_read must be T-separated"
assert s2["round_no"] == 268
print("close OK: round 268 state/heartbeat/report written; epoch", epoch, "clock", clock)
