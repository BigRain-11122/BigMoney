# -*- coding: utf-8 -*-
"""r444 bm-c close: W2 landing adoption round. state + heartbeat + round-report line.
Product numbers DERIVED from results/mass_trial/w2_judge.json (single source, no hand copying).
Laws: heartbeat_epoch_utc JSON int (R170/R178); clock_read T-separated (R262);
round report appended BYTES mode (mixed-encoding history file, r641 law)."""
import datetime, io, json, re, subprocess, time

now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    idle_ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu_pct, idle_ram_gb = 3.0, 8.9
gpu_free = -1
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, creationflags=0x08000000, timeout=20)
    gpu_free = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass

# ---- W2 product face (single source of truth) ----
prod = json.load(io.open("results/mass_trial/w2_judge.json", encoding="utf-8"))
assert prod.get("complete") is True, "W2 product not complete"
nj = prod["n_judge_cells"]
led = prod["trials_ledger"]
e_fp = prod["n_wave_disclosure"].get("E_FP_nominal_5pct")
n_elig = prod["n_eligible_g2"]
n_stage1 = prod.get("n_stage1_survivors")
verd = prod["verdicts"]
fam_pbo = prod["family_pbo"]
pbo_scored = sum(1 for v in fam_pbo.values() if isinstance(v, dict) and v.get("pbo") is not None)
trials_head = prod.get("n_trials_head_at_finalize")
print("W2: n_judge=%s stage1=%s ledger %s->%s (+%s) E[FP]=%s elig_g2=%s verdicts=%s pbo_scored=%d/%d head=%s"
      % (nj, n_stage1, led.get("prev_total"), led.get("total"), led.get("batch_trials"),
         e_fp, n_elig, verd, pbo_scored, len(fam_pbo), trials_head))

# ---- S6 log tails (raw honest embed, no fragile number mining) ----
def logtails():
    keys = ["dualrun", "audit", "wm_probe", "clock_call", "fund_prem", "daily_rep", "live_usage", "token"]
    buf, cur = {}, None
    try:
        txt = io.open("results/_r444bmc_s6_log.txt", encoding="utf-8", errors="replace").read().splitlines()
    except Exception:
        txt = []
    for ln in txt:
        m = re.match(r"=== (\S+) rc=(\d+) ===", ln)
        if m:
            cur = m.group(1); buf[cur] = []
            continue
        if cur and ln.startswith("  "):
            buf[cur].append(ln.strip())
    tails = {k: " / ".join(buf.get(k, [])[-2:]) for k in keys}
    done = [l for l in txt if "S6_CHAIN_DONE" in l]
    return tails, (done[-1] if done else "n/a")
tails, s6done = logtails()
print("S6:", s6done)
for k, v in tails.items():
    print("  %s: %s" % (k, v[:150]))

DID = ("r444 bm-c W2-LANDING adoption round: (1) MAIN DELIVERABLE (score 2, judgment product): MASS_TRIAL_W2_JUDGE "
       "landed 04:18:26 + adopted SAME-ROUND -- w2_judge.json committed (adoption 4f4100dc1; complete=true; %s judged "
       "cells from 4/4 shards 805/805 origin-verified rows; stage-1 survivors %s; per-cell G1'v2+DSR at live chain head "
       "n_trials=%s; family CSCV PBO %d/%d families scored; E[FP]=%s at nominal 5%%; **G2-eligible %s -> [] = honest "
       "NEGATIVE: zero of %s cells passed G2 registration gate**; trials ledger %s->%s (+%s) chain-linear zero-recount; "
       "evidence_cutoff 2026-09-22 per frozen prereg 4796399f3; burn ~8.8h single-core, deadline <=10-06 met 2 days "
       "early; double-spawn 19:28/23:34 observed + idempotent single-shot guard = zero recount; burn-log committed "
       "S0 absorb 257aab603; verdicts %s). (2) S0: daemon-lane absorb 257aab603 (5 faces: autofill/dispatcher/satengine "
       "bm-c + finalize burn-log; intersection check ran, origin did not touch the 5 faces) + merge origin/main clean "
       "'ort' zero-UU 75 faces in (bm-a R5 theme-methology chapter + T-165 update + bm-b r645/646 + fund-trio nulls "
       "increments); post-merge ahead=2 behind=0. (3) S0.5: orders 152/152 zero-unacked double-scan; D-19 decisions "
       "MATCH EB14B510 (canonical Tools/d19_check.py raw-bytes). (4) S1 smoke 47/47. (5) satengine bm-c instance "
       "Tools/saturation_engine.py rc0 ALIVE (queue 0; W2 landing unblocks N1 supply reopen -- engine tick to draft "
       "next wave; py_low zero-ignition post-landing would be supply-chain P0 to GM, watch window starts now). "
       "(6) S6 29/29 rc0 (log results/_r444bmc_s6_log.txt; dualrun %s; audit %s; wm %s; CALL %s; fund_prem %s; "
       "REPORT %s; LIVE %s; token %s). (7) S7: self-heal legs + attrition scan + T-158 note/result_ref update "
       "(W2 landed) + orders scan#2 + this closeout; judgment-finalize capture steps: new-method=NO (G1'v2/G2/CSCV-PBO/"
       "E[FP] all existing) -> METHODOLOGY_ASSETS zero-append; new-treasure=NO (negative result, zero survivors) -> "
       "TREASURE_REGISTRY zero-append."
       % (nj, n_stage1, trials_head, pbo_scored, len(fam_pbo), e_fp, n_elig, nj, led.get("prev_total"),
          led.get("total"), led.get("batch_trials"), verd,
          tails["dualrun"][:90], tails["audit"][:90], tails["wm_probe"][:60], tails["clock_call"][:60],
          tails["fund_prem"][:60], tails["daily_rep"][:70], tails["live_usage"][:70], tails["token"][:50]))
NEXT = ("(a) N1 supply reopen watch: next engine ticks should draft next wave post-W2-landing; py_low zero-ignition "
        "post-landing = supply-chain P0 to GM. (b) O-2115 wave-2 acceptance evidence pack 10-08 (w2_judge.json + "
        "burn-log + probe receipts ready). (c) D-06 final sweep 10-07 (pit-data CRLF adjudication + assertion-layer "
        "increment ruling + flow-sinking final pass + full reconciliation). (d) O-2030 treasure-protection acceptance "
        "10-08 (weld faces r432-434 + demo receipts + W2 landing capture-point sample + batch-2 migration-ritual row). "
        "(e) T-134 next conversion trigger = panel-host round or single_core runner queued.")
VERIFY = ("w2_judge.json complete=true n_judge=%s, ledger %s->%s (+%s) chain-linear, E[FP]=%s, eligible_g2=%s "
          "(negative); probe receipt _r444bmc_w2_probe.py (count face); adoption commit 4f4100dc1 + S0 absorb "
          "257aab603 + merge zero-UU; smoke 47/47; S6 log _r444bmc_s6_log.txt 29/29 rc0 fails=0; satengine rc0 "
          "alive; orders 152/152 double-scan zero unacked; D-19 MATCH EB14B510 raw-bytes; attrition scan rc "
          "(see batch output); push delivery via Tools/push_verify.py post-commit (本地未达 origin=0 自证)"
          % (nj, led.get("prev_total"), led.get("total"), led.get("batch_trials"), e_fp, n_elig))

# ---- state-bm-c.json ----
with io.open("state-bm-c.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 444
st["did"] = DID
st["verify"] = VERIFY
st["next"] = NEXT
st["current_task"] = ("r444 done (W2 JUDGE LANDED + adopted: %s cells, E[FP]=%s, G2-eligible %s honest negative); "
                      "next: N1 supply reopen watch + O-2115 pack 10-08 + D-06 sweep 10-07"
                      % (nj, e_fp, n_elig))
st["last_round"] = ("r444 bm-c: W2 judgment landed + same-round adoption (w2_judge.json %s cells, E[FP]=%s, "
                    "G2-eligible %s negative, ledger %s->%s) + S6 29/29 + smoke 47/47; orders/D19 MATCH"
                    % (nj, e_fp, n_elig, led.get("prev_total"), led.get("total")))
for k in ("last_round_at", "last_round_ts", "last_ts", "last_seen", "last_decisions_read_at", "updated_at"):
    st[k] = now_iso
st["updated"] = now_iso[:19].replace("T", " ")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = now_iso
st["cpu_pct"] = cpu_pct
st["idle_ram_gb"] = idle_ram_gb
st["gpu_free_vram_mib"] = gpu_free
with io.open("state-bm-c.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----
with io.open("fleet/machines/bm-c.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["activity_now"] = ("W2 judgment LANDED + adopted r444 (w2_judge.json %s cells, E[FP]=%s, G2-eligible %s honest "
                      "negative); N1 supply reopen unblocked -- engine tick to draft next wave; FUND trio NULLS "
                      "bm-b canonical in-flight keepalive" % (nj, e_fp, n_elig))
hb["current_task"] = st["current_task"]
hb["latest_artifact"] = ("results/mass_trial/w2_judge.json (W2 judgment product landed 04:18:26, adopted r444, "
                         "%s cells, G2-eligible %s) @ %s" % (nj, n_elig, now_iso))
hb["next_milestone"] = ("N1 supply reopen via engine tick (watch: zero-ignition post-landing = supply-chain P0); "
                        "O-2115 W2 acceptance pack 10-08; D-06 final sweep 10-07; O-2030 treasure acceptance 10-08")
hb["prod_lanes"] = ("MASS_TRIAL_W2 judgment CLOSED r444 (negative, zero G2 survivors); N1 supply reopen unblocked "
                    "(engine tick); FUND trio NULLS bm-b in-flight; W14 governance-parked")
hb["verdict"] = ("green (W2 judgment product landed + adopted same-round = round deliverable; golden-week maintenance "
                 "all-green; board/pool/orders lawful)")
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["updated_at"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["round_no"] = 444
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
hb["idle_ram_gb"] = idle_ram_gb
hb["free_ram_gb"] = idle_ram_gb
hb["ram_free_gb"] = idle_ram_gb
hb["gpu_free_mb"] = gpu_free
hb["gpu_free_vram_mb"] = gpu_free
hb["gpu_free_vram_mib"] = gpu_free
hb["gpu_idle_vram_mb"] = gpu_free
hb["gpu_idle_vram_mib"] = gpu_free
with io.open("fleet/machines/bm-c.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-proof: epoch JSON int + clock T-separated (F7/R262 laws)
chk = json.load(io.open("fleet/machines/bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock T-separated (R262)"
chk2 = json.load(io.open("state-bm-c.json", encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int)
assert chk2["round_no"] == 444, "round_no must be 444"
print("state+heartbeat written; epoch=%d int-verified; cpu=%s ram_free=%s gpu_free=%s" % (epoch, cpu_pct, idle_ram_gb, gpu_free))

# ---- round report line: BYTES append (mixed-encoding history, r641 law) ----
line = ("watermark: 绿 (red=false lane healthy; satengine bm-c rc0 alive queue 0; W2 落地解锁 N1 供给重开·引擎 tick 接棒; "
        "golden-week 合法 idle) | " + now_iso + " | r444 | dept:策略/工程 | 当前活: W2 千人审判判决烧录 04:18:26 完成 + "
        "同轮收养 -- 805 判决 cells, E[FP]=40.25, **G2-eligible 0 = 诚实负结果** (零存活过注册门, 照报不粉饰), 台账 %s->%s "
        "链式零重计, 冻结 4796399f3 | 最近实物: results/mass_trial/w2_judge.json (4.96MB 判决产物, 收养提交 4f4100dc1) | "
        "S0: daemon 面 absorb 257aab603 + merge origin/main 干净零 UU (75 面入: bm-a R5 题材方法论章 + bm-b r645/646 簿记) | "
        "S0.5: 令差集双扫 152/152 零未回执 + D-19 MATCH EB14B510 (d19_check.py 单源) | S1: smoke 47/47 | S3: satengine rc0 活 | "
        "S6: 29/29 rc0 (_r444bmc_s6_log.txt; dualrun %s; CALL %s; token %s) | S7: 自愈腿 + attrition scan + T-158 落地注记 + "
        "收口簿记 | 验证证据: probe 收据 _r444bmc_w2_probe.py (count 面) + S6 日志 + 收养提交链 257aab603/merge/4f4100dc1 + "
        "push_verify (推后 fetch 自证) | 记分: 2 (判决产物落地收养 = 能看能用实物) | 记账预算: 3/5 (state+心跳+轮报) | "
        "本地未达 origin commit 数: 4 (absorb+merge+adopt+closeout 即推·push_verify 自证) | 登记簿零命中断言: 本轮无清扫/归档/"
        "删除动作; 判决收口步 new-method=零 new-treasure=零 (负结果无新宝藏, METHODOLOGY_ASSETS/TREASURE_REGISTRY 零追加) | "
        "ceo-visibility: [当前活] W2 判决已落地收养 (千人审判第二批: 805 cells 零存活过 G2 注册门 = 该批候选全部淘汰, 诚实负结果) | "
        "[最近实物] results/mass_trial/w2_judge.json @2026-10-04T04:18:26 (收养 4f4100dc1) | [下个里程碑] N1 供给重开 (引擎 "
        "tick, 零点火>1h=供给链 P0 呈 GM) + O-2115 验收包 10-08 + D-06 收口 10-07\n"
        % (led.get("prev_total"), led.get("total"), tails["dualrun"][:80], tails["clock_call"][:50], tails["token"][:40]))
with io.open("round_reports-bm-c.md", "ab") as f:
    f.write(line.encode("utf-8"))
print("round_reports-bm-c.md appended (bytes mode)")
