"""R256 bm-a close: state file + heartbeat update (four-face mirror)."""
import io
import json
import subprocess
import time

# ---- state-bm-a.json (faces: no BOM / LF / indent=1 / ascii=False)
j = json.load(io.open("state-bm-a.json", encoding="utf-8"))
j["round_no"] = 256
j["did"] = (
    "R256: T-73 s3 slice-3 CN-REGIME-POLICY full arc ONE ROUND (supply-"
    "line answer to R255 starvation flag, one round ahead of committed "
    "schedule): scope-down design decision per s2-sliceB digest -> "
    "probe frozen (510300 3483 bars, v3 full-cover G/Y/R/O "
    "1674/1238/528/43, ADV20 cap margin 3.8x) -> prereg frozen "
    "124b360c BEFORE any run (3 judged cells + 990 exhaustive C(12,4) "
    "nulls zero-RNG, N=993, A/B/C three-face) -> runner selftest 18/18 "
    "-> pool entry 16:17:58 ff690469 -> autofill launch -> landed 28.7s "
    "-> deterministic harvest PASS (r244 law, same-round) -> VERDICT "
    "NEGATIVE: A-face policy-axis-value FALSE (full Sharpe 0.23<0.2998 "
    "sole failing condition; OOS + maxDD conditions pass = 2024-10 "
    "opportunity-cost face real), B-face no month-set signal (P4B "
    "improvement -0.0698, p=0.7798/495), C-face 0/3 (line 0.5691) -> "
    "CN-REGIME-POLICY judged negative, no paper account, policy-"
    "calendar axis DOUBLE falsified (s2+s3), third CN-native family "
    "negative, no-reopen law; family evidence: v3 ladder on 510300 "
    "does not beat buy-hold after x2 costs (0.2998 vs 0.309, drawdown "
    "face improved -37.13% vs -46.30%); ledger 186592+993=187585, "
    "attrition row 47; P0 same-round: post_review check-ROT NO row "
    "(sliding -5 git window on hot ticket) -> git_log_file depth arg "
    "(selftest ALL PASS) + row reconciled depth 30 + new claim row "
    "registered -> reviewer 20 YES/0 NO/5 WAIT; CODELY check-rot pit "
    "law appended; S6 25 legs all exit 0 Saturday no-ops"
)
j["verdict"] = (
    "GREEN research slice closed loop SAME-ROUND (prereg->run->harvest-"
    ">review full arc); honest negative verdict per frozen prereg")
j["next"] = (
    "remaining s2 slices (retail-herding/factor-history/style-rotation) "
    "+ GRID-SLEEVE combo prereg (R253 pointer) + CORE-SATELLITE blocked "
    "on T-57 satellite supply; 09-28 new-bar chain; 10-01 month trio + "
    "v3 date gate; T-70 verdict window 10-09")
ts = time.strftime("%Y-%m-%d %H:%M:%S")
j["ts"] = ts
j["last_round_ts"] = ts
j["updated_at"] = ts
j["current_task"] = ("T-73 s3 chain (family closure + s2 slices) + "
                     "fleet maintenance")
j["last_run"] = "R256 " + time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
j["last_round_at"] = j["last_run"]
j["last_round"] = time.strftime("%Y-%m-%dT%H:%M")
j["updated"] = time.strftime("%Y-%m-%d %H:%M")
with io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(j, fh, ensure_ascii=False, indent=1)

# ---- fleet/machines/bm-a.json heartbeat (own file only)
h = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
h["last_seen"] = ts
h["current_task"] = j["current_task"]
h["verdict"] = j["verdict"]
epoch = int(time.time())
assert isinstance(epoch, int)
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
h["round_no"] = 256
import psutil
vm = psutil.virtual_memory()
h["free_ram_gb"] = round(vm.available / 1e9, 1)
h["cpu_pct"] = psutil.cpu_percent(interval=1)
h["cpu_cores"] = psutil.cpu_count()
try:
    import subprocess as sp
    out = sp.run(["nvidia-smi", "--query-gpu=memory.free",
                  "--format=csv,noheader,nounits"],
                 capture_output=True, text=True).stdout.strip()
    h["gpu_free_vram_gb"] = round(float(out.split("\n")[0]) / 1024, 1)
except Exception:
    pass
with io.open("fleet/machines/bm-a.json", "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(h, fh, ensure_ascii=False, indent=1)

# self-verify epoch int type (R170/R178 law)
chk = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(chk["orders_ack"], str) and len(
    chk["orders_ack"].split()) == 82
print("state round 256 + heartbeat written, epoch int",
      chk["heartbeat_epoch_utc"], "orders_ack 82/82 intact")
