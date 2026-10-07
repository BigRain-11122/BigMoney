# -*- coding: utf-8 -*-
"""r858 bm-a closeout writer: state 857->858, ROOT round report line,
heartbeat nine fields, pit-pool direct-write + receipt, inbox move.
Fresh-read-modify-write per multi-writer law (r159 pit); UTF-8 no BOM.
"""
import hashlib
import json
import os
import shutil
import io
import sys
from datetime import datetime, timezone, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                             errors="replace")
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---------- 1. state-bm-a.json ----------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round"] = 858
st["round_no"] = 858
st["loop_round"] = "r858"
st["current_task"] = ("r858 closed: S0 double-storm rebase resolved + "
                      "cycle_position 3-axis census landed; next=15:30 "
                      "market-reopen re-arm (zt_pool FIRST accrual)")
st["last_round"] = "r858"
st["last_round_at"] = TS
st["last_round_ts"] = TS
st["last_run"] = TS
st["last_seen"] = TS
st["updated"] = TS
st["ts"] = TS
st["clock_read"] = TS
st["heartbeat_epoch_utc"] = int(NOW.timestamp())
st["last_action"] = ("r858: S0 double-storm canon-resolved (14-UU mlv x6 "
                     "lanes + r858 twins resolver; 5-UU mlv + 4 byte-takes; "
                     "r857 delivered origin/main a663edfa1) + census landed")
st["did"] = (
    "r858: S0-1 anchor bm-a + orphan probe (py_faces 15, orphans=1 BigDomain "
    "cross-company read-only, r857 posture held) + S0 writer-pause double "
    "rebase storm canon-resolved (storm#1 14-UU vs bm-c r718 same-window S6 "
    "dual-run: mlv resolve x6 ALL_FACES lanes + results/_r858_uu_resolve.py "
    "twins/solo block take-new all-ours-bm-c-newer; storm#2 5-UU vs bm-c "
    "r719: mlv lhb + dashboard/scorecard x4 stage-:2 byte takes; stash "
    "runtime faces restored; PS stash@{0} splat trap hit+recovered via "
    "python subprocess) + PUSH DELIVERED r857 content origin/main "
    "a663edfa1 not-at-origin=0 (stranded machine-branch content landed) + "
    "compute_audit.bm-a lane 201->1 adjudicated r85 window key-set survival "
    "PASS no-heal (shared-ledger reset propagated from cross-machine chain; "
    "git archive intact at merge-base commits; sustained-window self-heals "
    "in-round) + S0.5 orders 51/51 zero-unacked + DEC/ORD identical "
    "(ee659451/2bb2ee75 case-normalized r711 law) + smoke 49/49 + watermark "
    "red=false next_pick claimed advisory + saturation engine alive-idle "
    "queue empty (W181 seat watch: no action due) + PRODUCT LANDED: "
    "cycle_position 3-axis census (scripts/cycle_position_census.py selftest "
    "8/8 + results/cycle_position_census.json: 12td frozen-pilot panel, "
    "N_zt med 53.5 p99 101.5 max 103, N_dt med 9.5 max 56 (09-28 sole "
    ">=4x spike marker, matches r857 observation), zb_rate med 0.2325, "
    "zero-attack-day null honest; next-day associations illustrative N=11: "
    "n_dt_t vs n_zt_t1 spearman -0.336, zb_t vs n_zt_t1 +0.296; descriptive "
    "census not-a-judged-face, prereg awaits forward zt_pool accrual) + S6 "
    "35 legs rc0 + 4 bar-conditioned skip-legal pre-market (dualrun streak "
    "51 zero-drift; compute_audit flags pool_starvation+supply_floor -> "
    "standing-line response: census=REGIME-5 supply next piece + 15:30 "
    "re-arm queued; py_watermark verdict py_low_board_clear legal idle) + "
    "attrition CLEAN + idle --worked idle_rounds 0 + quartet 4/4 (pin=8 "
    "no-op, watchdog, both claws) + own-session inbox claim msg processed "
    "(superseded by landed pilot)")
st["next"] = (
    "r859: 10-08 15:30 market-reopen data chain re-arm (update_daily drops "
    "10-08 bar -> all gates re-collect incl. zt_pool FIRST REAL accrual "
    "day; REGIME_GUARD v3 enforce; live.paper+t35_open_fill_verify+t24 legs "
    "on new bar) -> after first accrual: pilot panel-face re-verify (J2 "
    "identity real rows vs same-day re-fetch) -> census re-anchor when "
    ">=10td forward zt_pool history -> REGIME-5 supply prereg draft "
    "(usable ~10-22) + N_dt independent-info carried into three-axis gate "
    "design + W181 seat watch")
st["verify"] = (
    "census selftest 8/8 + run rc0 + smoke 49/49 + S6 35 legs rc0 + dualrun "
    "streak 51 + attrition CLEAN + orders 51/51 + DEC/ORD identical + "
    "orphan face=1 + quartet 4/4 + not-at-origin=0 post-push + engine "
    "alive-idle")
st["latest_artifact"] = ("scripts/cycle_position_census.py + "
                         "results/cycle_position_census.json @" + TS)
st["last_artifact"] = st["latest_artifact"]
st["now_active"] = ("r858 closed (census landed); next = 15:30 "
                    "market-reopen re-arm + pilot re-verify")
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc")
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state 857->858 written, ts", TS)

# ---------- 2. ROOT round report line ----------
rp = "round_reports-bm-a.md"
line = (
    "2026-10-08 03:3x | r858 | S0 writer-pause double rebase storm "
    "canon-resolved (14-UU: mlv x6 ALL_FACES lanes + _r858 resolver "
    "twins/solo all-ours-newer; 5-UU: mlv lhb + x4 stage byte-takes; stash "
    "restored; PS stash@{0} splat recovered) + r857 content DELIVERED "
    "origin/main a663edfa1 not-at-origin=0 + compute_audit.bm-a lane 201->1 "
    "adjudicated r85 survival PASS no-heal (git archive intact) + orders "
    "51/51 + DEC/ORD identical + smoke 49/49 + PRODUCT: cycle_position "
    "3-axis census landed (selftest 8/8; 12td panel N_zt med 53.5/p99 "
    "101.5, N_dt med 9.5/max 56 with 09-28 sole spike, zb med 0.2325; "
    "associations illustrative N=11; descriptive non-judged face; "
    "REGIME-5 supply next piece) + S6 35 legs rc0 + 4 bar-conditioned "
    "skip-legal (dualrun streak 51; supply_floor responded=census+15:30 "
    "re-arm; watermark py_low_board_clear legal) + attrition CLEAN + "
    "quartet 4/4 + orphan face=1 (BigDomain cross-company read-only) + own "
    "inbox claim processed | selftest 8/8 + run rc0 + smoke 49/49 + "
    "not-at-origin=0 | next: 15:30 re-arm (zt_pool FIRST accrual + "
    "REGIME_GUARD enforce + bar legs) -> pilot panel re-verify -> census "
    "re-anchor >=10td -> REGIME-5 prereg ~10-22\n")
with open(rp, "a", encoding="utf-8", newline="") as fh:
    fh.write(line)
print("round report line appended (ROOT canonical)")

# ---------- 3. heartbeat nine fields ----------
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
try:
    it = json.load(open("results/idle_trigger.bm-a.json", encoding="utf-8"))
    ram = it.get("ram_free_pct")
    vram = it.get("vram_free_gb")
except Exception:
    ram = vram = None
hb["last_seen"] = TS
hb["current_task"] = ("r858: S0 double-storm resolved + cycle_position "
                      "census landed; next 15:30 re-arm")
hb["cpu_cores"] = 32
if ram is not None:
    hb["ram_free_pct"] = ram
if vram is not None:
    hb["gpu_free_vram_gb"] = vram
hb["verdict"] = "legally-idle-board-clear (pool supply_floor responded: census landed + 15:30 re-arm queued)"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = int(NOW.timestamp())
hb["clock_read"] = TS
hb["ts"] = TS
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], \
    "clock_read must be T-separated"
print("heartbeat written, epoch int + clock T-form verified")

# ---------- 4. pit-pool.md direct-write + receipt ----------
entry = (
    "\n- [2026-10-08 03:3x r858 bm-a] **共享账本重置经 S0 风暴传播进 lane 镜像坑+r85 "
    "存活核裁定法（r858 双 rebase 风暴实弹）**：跨机同窗 S6 双跑使 S0 pull --rebase "
    "一轮双风暴（14-UU+5-UU）时，ALL_FACES 共享账本（compute_audit history 201 行）"
    "可在对岸链上已被先行重置（→1 行），本机 S0 拉取后生产者 write_lane 把重置面原样"
    "镜像进自家 lane（bm-a lane 201→1）——lane 结构副本被共享面回退吞没（r288 族面语"
    "义变体：共享回退吞 lane）。裁定法=①r85 窗内键集存活核先行（以生产者窗口首行 ts "
    "为界差集；窗内零丢失=合法勿治·禁按行数直判丢失禁旗标升级）②git 史全保（旧史在 "
    "merge-base 前提交逐行可考）③持续窗判据面一轮自愈（15min 窗样本自然回填）④禁手工 "
    "union 回填 lane——lane=镜像非权威，回填即被下轮生产者镜像覆盖白干。How to apply："
    "风暴后见 lane/共享账本行数坍缩→先跑存活核再定性；双连 rebase 勿 abort（writer-"
    "pause 窗+staged resolver 复用连解；r858 分工=mlv lane+块取新 force_side 孪生耦"
    "合 resolver）。\n")
pp = "research/pit-pool.md"
raw = open(pp, "rb").read()
main_before = os.path.getsize("CODELY.md")
eb = entry.encode("utf-8")
with open(pp, "ab") as fh:
    fh.write(eb)
rc = {
    "ts": TS,
    "author": "bm-a r858",
    "action": "pit direct-write (main at red line, margin 114B < entry)",
    "precedent": "r666/r672 direct-write pattern",
    "target": pp,
    "entry_bytes": len(eb),
    "entry_sha256": hashlib.sha256(eb).hexdigest(),
    "target_bytes_before": len(raw),
    "target_bytes_after": os.path.getsize(pp),
    "main_codely_bytes": main_before,
    "main_untouched": True,
    "law_ref": "D-20261002-06 main <=30KB; new-pit direct-write at red line",
}
with open("results/_r858bma_pit_direct_write.json", "w",
          encoding="utf-8", newline="\n") as fh:
    json.dump(rc, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print("pit-pool entry +%dB (after %dB), receipt written"
       % (len(eb), os.path.getsize(pp)))

# ---------- 5. inbox move ----------
src = ("fleet/inbox/MSG-2026-10-08-0250-bma-ALL-"
       "s501-zt-pilot-prereg-claim.md")
dst = ("fleet/inbox/processed/MSG-2026-10-08-0250-bma-ALL-"
       "s501-zt-pilot-prereg-claim.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox: own-session claim msg -> processed/ (superseded by "
          "landed pilot, no reply due)")
print("CLOSEOUT WRITER DONE")
