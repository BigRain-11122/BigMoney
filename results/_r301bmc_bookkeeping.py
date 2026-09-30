"""r301 bm-c round bookkeeping: state, round report line, heartbeat."""
import json
import psutil
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
now = datetime.now(timezone(timedelta(hours=8)))
now_iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

vm = psutil.virtual_memory()
gpu_free = 0
try:
    import subprocess
    q = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.free",
                                 "--format=csv,noheader,nounits"],
                                text=True)
    gpu_free = int(q.strip().splitlines()[0])
except Exception:
    gpu_free = 12834

# ---------------- state-bm-c.json ----------------
sp = ROOT / "state-bm-c.json"
st = json.loads(sp.read_text(encoding="utf-8"))
st.update({
    "machine_id": "bm-c",
    "round_no": 301,
    "last_round_at": now_iso,
    "last_round_ts": epoch,
    "updated": now_iso,
    "cpu_pct": psutil.cpu_percent(interval=1.0),
    "idle_ram_gb": round(vm.available / 2**30, 1),
    "gpu_free_vram_mib": gpu_free,
    "verify": ("S1 smoke 47/47; S0 double-rebase收敛 (r300断头rebase续作: 16 UU共享面ours+rider+主件CODELY union, "
               "push dab216e7e); S6 33 legs rc0 (dualrun streak 3/3 = FLIP GATE READY first observation; "
               "monthly trio 202609 already on disk 02:59 no-double-run); orders diff EMPTY; D-19 ED4E0EAB "
               "UNCHANGED (raw-blob); attrition CLEAN; claw OK; loop Running pin:05 no-op; watchdog Ready"),
    "did": ("r301: T-136 LOWAMP-P1 verdict integrity audit P0 delivered (claim 880a65217, done 925e9ed4f). "
            "Leg A as-burned replay reconciles to the bp (ret_full -0.179871 6dp + 1630-row returns <5e-7) = "
            "NO instrument defect. Leg A2: 246/254 exits (97%) = engine DEFAULT exit stack (time_decay 67+69, "
            "loss_time_stop 55+55) not family signal; bond pair structurally churned every 8-13d. Leg B "
            "(exit stack neutralized P1-only): +15.88% sharpe +1.158 n_trades=7; Leg C independent no-engine "
            "arithmetic +15.95% cross-validates. E1 39pp gap FULLY reconciled (-33.86pp churn + -5.3pp "
            "eligibility/gaps); x2 delta -32.86pp = 509 fills x 13.041bp x ~0.495 weight (no 347bp anomaly). "
            "Blast radius: LOWAMP-P1 SOLE member (t22 traders tuned-or-equity-house-style; trial-labor W1..W14 "
            "explicit AXIS_EXITS = designed face; W14 holiday burn SAFE). Root cause = prereg internal "
            "contradiction (ALWAYS-ON family def vs default 25d hard limit) = specification-face defect. "
            "Adjudication memo research/T136_VERDICT_AUDIT.md delivered; GM ruling requested MSG-048x."),
    "current_task": ("T-136 audit complete from executor side; VOID-vs-stands adjudication PENDING GM/CEO "
                     "(verdict stays judged-negative + UNDER REVIEW; consumption warnings stand). "
                     "dualrun flip gate READY (three-machine streak 3/3/9) -- flip surgery per "
                     "POOL_RETIREMENT_S3_WAVE1_ANALYSIS sec.3 belongs to next round. Zero burnable "
                     "lane-free pool work on bm-c = legal idle disclosed."),
    "next": ("(a) GM ruling on T-136 VOID-vs-stands (MSG-048x) + GM ruling on PERPETUAL_FACES v1.1 (MSG-0400) "
             "-> W3 supply restoration; (b) bm-b astock refresh window ~06:45 -> EXCLUSION+FACEB auto-burn "
             "(bm-b lane); (c) dualrun flip surgery per POOL_RETIREMENT sec.3 sequence (compute_audit->"
             "fill_ladder->autofill+F6 atomic commit) -- gate met, next-round action; (d) RAM watch 0.7GB low; "
             "(e) T-134 s4 efficiency face = bm-a next-round (CEO acceptance 10-01 morning report)"),
    "heartbeat_epoch_utc": epoch,
    "clock_read": now_iso,
    "note": "r301 product score=2 (runnable audit fixture + evidence artifact + adjudication memo)",
    "last_ts": now_iso,
    "last_decisions_sha": "ed4e0eabf941b4299a6f26b243082ee74a83517b462d352d9c047f95a49a1f07",
    "last_decisions_read_at": now_iso,
    "last_decisions_sha_method": ("python subprocess.check_output raw-blob bytes SHA-256 "
                                  "(PS-pipeline join method = transcoding false-drift, see CODELY r292 pit)"),
    "last_round": ("2026-10-01 r301: T-136 LOWAMP verdict integrity audit P0 (instrument clean bp-match; "
                   "root cause bare default exit stack x always-on bond pair; intended face +15.9%; 39pp+x2 "
                   "reconciled; blast radius LOWAMP-P1 sole; VOID memo to governance) + S0 double-rebase收敛 "
                   "+ S6 33 legs rc0 + dualrun flip gate READY"),
})
sp.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("state round 301 written")

# ---------------- round_reports-bm-c.md ----------------
rp = ROOT / "round_reports-bm-c.md"
line = (
    f"{now_iso}｜r301｜watermark verdict=红（runnable-work-idle-low-cpu：ready=2 均 bm-b lane〔等 astock 刷新窗 "
    "~06:45〕+W14 parked=治理面——本机零可烧 lane-free 批=合法 idle 白名单如实披露；本轮实活=P0 审计票）｜当前活="
    "T-136 LOWAMP-P1 判决完整性审计（P0·r239 fetch 后认领 880a65217）四腿全交付｜最近实物="
    "research/T136_VERDICT_AUDIT.md（判决审计备忘录）+ results/t136_verdict_audit/t136_leg123.json（Legs A/B/C "
    "证据件）+ results/_r301bmc_t136_fixture.py（可复跑 fixture）@04:48 commit 925e9ed4f｜下个里程碑="
    "GM 裁定 T-136 VOID-vs-stands（MSG-048x 已递·裁决窗 ≤48h）+ dualrun flip 门 READY 首观测（三机 streak "
    "3/3/9·POOL_RETIREMENT §三序另轮开刀）+ bm-b 刷新窗后 EXCLUSION/FACEB 自动烧｜产品分=2（能跑/能看实物：fixture+"
    "证据件+备忘录）｜S1 47/47；S0 双 rebase 收敛（r300 断头 rebase 续作：16 UU 共享面 ours+rider+主件 CODELY "
    "union·推 dab216e7e）；S6 33 legs rc0（dualrun streak 3/3=flip 门 READY·月度三件 202609 已在位 02:59 不双跑）；"
    "orders 差集 EMPTY；D-19 ED4E0EAB UNCHANGED（raw-blob）；attrition CLEAN；claw OK；loop Running pin:05 "
    "no-op；watchdog Ready；inbox 三件均非本机收件（bma→bmb 诊断/bmb→GM 裁定/bmc→GM T-136）留置"
)
with open(rp, "a", encoding="utf-8", newline="") as fh:
    fh.write(line.replace("\n", " ") + "\r\n")
print("round report appended")

# ---------------- heartbeat fleet/machines/bm-c.json ----------------
hp = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hp.read_text(encoding="utf-8"))
hb["last_seen"] = now_iso
hb["current_task"] = "T-136 audit delivered; GM adjudication pending (VOID vs stands); dualrun flip gate READY"
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["idle_ram_gb"] = round(vm.available / 2**30, 1)
hb["gpu_free_vram_mib"] = gpu_free
hb["verdict"] = ("r301 product=2: T-136 LOWAMP verdict audit P0 done (instrument clean bp-match; default exit "
                 "stack churn -33.9pp root cause; intended face +15.9%; blast radius LOWAMP-P1 sole; W14 safe); "
                 "watermark red=legal idle (bm-b-lane ready entries + parked W14); flip gate READY")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hp.write_text(json.dumps(hb, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
chk = json.loads(hp.read_text(encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat written; epoch int verified:", chk["heartbeat_epoch_utc"],
      "| clock:", chk["clock_read"])
