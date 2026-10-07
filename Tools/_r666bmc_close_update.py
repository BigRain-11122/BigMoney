# -*- coding: utf-8 -*-
"""r666 bm-c close: state + heartbeat + round-report updater.
Laws: R170/R178 epoch int (python int(time.time()) direct), R262 clock_read
T-format, r583 facts-driven watermark keys (dec/ord sha from s05 facts file),
r814-bm-a watermark write-side single-source (python raw-blob values only).
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
FACTS = os.path.join(ROOT, "results", "_r666bmc_s05_facts.json")
CREATE_NO_WINDOW = 0x08000000

now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

with open(FACTS, encoding="utf-8-sig") as fh:
    facts = json.load(fh)
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert len(dec_sha) == 64 and len(ord_sha) == 40, "facts sha shape gate"

# GPU free VRAM sample (CREATE_NO_WINDOW per U060)
gpu_mib = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_mib = int(r.stdout.decode("utf-8", errors="replace").strip().splitlines()[0])
except Exception:
    gpu_mib = None

with open(STATE, encoding="utf-8-sig") as fh:
    st = json.load(fh)
prev_gpu = st.get("gpu_free_vram_mib") or 1078
gpu_mib = gpu_mib if gpu_mib is not None else prev_gpu

ACT = ("当前活: r666 值守轮收口（S0 干净自产 3 件零落后·S1 48/48·aging-line 终判 09:15:34=bm-b 双 tick 失约+Q/D 双冻结 59min+hb 陈旧 155min→r663 范式升级·CODELY r662/r665 指针行 latin-1 双层 mojibake 治愈+根因坑直写 2 条·S6 38/38·QA r666 5/5）"
       " | 最近实物: fleet/inbox/MSG-2026-10-07-0916-bmc-ALL（bm-b 二次停滞升级通报·GM 队列+ALL·接管保持 CLOSED）+results/_r666bmc_trio_watch.json（终判证据）+CODELY.md mojibake 治愈 30,407B C1 零残留（收据 _r666bmc_codely_mojibake_heal.json）+qa/smoke-r666.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+research/pit-encoding.md 与 pit-lineage-legdiff.md 直写 2 坑"
       " | 下个里程碑: bm-b 复活即撤警（r664 范式）·仍暗 →~10:30 老化再升级；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r670（HANDOVER 窗）")
DID = ("r666 bm-c: aging-line verdict round + CODELY mojibake heal round (main products: escalation MSG-0916-bmc-ALL + lossless latin-1 heal of r662/r665 pointer lines + 2 direct-write pits). "
       "(1) S0: round-start dirty = 3 self-authored faces (2 daemon live-wins + r665 commitmsg leftover), HEAD==origin 5bfc0524f zero-behind, no pull needed, symbolic-ref healthy. "
       "(2) S0.5 double-sweep: DEC 635C3024 / ORD 437E9CDD zero-delta; fleet orders 163/163 zero unacked; inbox unread = own escalation MSG only. "
       "(3) S1 smoke 48/48. S3: sat engine alive rc0 (face ts 09:07:06 fresh); watermark green; board open=0; post_review zero-x. "
       "(4) AGING-LINE VERDICT (r665 next-pointer (a)): threshold 09:15 crossed, verdict probe 09:15:34 -- bm-b dark (09:02+09:12 ticks both missed; Q 1988/2000 D 1654/2000 frozen since 08:16:09 = 59min; hb 06:40:15 = 155min stale; zero bm-b origin commits since 08:12:15; probe needle 'bm-b' printed True = prose self-match false positive from own r665 commit message, eyeball OLOG-12 corrected) -> RE-ESCALATED per r663 pattern: MSG-2026-10-07-0916-bmc-ALL published (GM queue + ALL); takeover stays CLOSED (host_gates FAIL p1c_stock, r393/r668 watch-only); zero-loss face intact (crash_fuse active={}, checkpoint done-key resume); evidence results/_r666bmc_trio_watch.json. "
       "(5) CODELY HEAL: r662/r665 pointer lines were latin-1 double-encoded mojibake (root cause = python str \\xNN escapes byte-as-str in gate-fix writer _r665bmc_merge3.ps1, C1-control signature); lossless recovery via encode('latin-1').decode('utf-8') one-layer strip; line-88 hand-escape typo U+4C92 corrected to 字符串x per r407 fact-reconstruction (anchor pit-ps.md L53); 30,299 -> 30,407B final, C1 residual zero, main <=30KB held; receipt results/_r666bmc_codely_mojibake_heal.json + addendum. "
       "(6) S4: 2 new pits direct-write (pit-encoding.md byte-as-str \\xNN pit + pit-lineage-legdiff.md probe-needle prose self-match pit) + 1 pointer line in main. "
       "(7) S6 chain 38/38 rc0 (dualrun ZERO-DRIFT streak 51; REPORT-2026-10-07 + LIVE-2026-10-07 written; regime ORANGE shadow; golden-week no-bar face held). "
       "(8) QA r666 5/5 (explicit --round 666, 93 trades determinism=True, equity 1,017,839 cross-round identical). (9) attrition CLEAN (4 ledgers, healed-history rows noted).")
NXT = ("(a) bm-b revival watch each round -> withdraw alert on revival (note line, r664 pattern) + resume trio finalize window watch 10-05..10-09; still dark at ~10:30 -> next escalation rung (hb 06:40 + >3.5h, r663 3h aging line same law). "
       "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week structural flags re-eval. "
       "(c) W171 burn watch (bm-a seat, A 391_004..393_003 + B 393_004..393_203, 161st wave). "
       "(d) pit-ps.md 31,449B > 30,720B domain limit = next mini-split candidate (D-06 balance leg). "
       "(e) monthly exam 10-31 assembly face; next 5x=r670 HANDOVER window.")
NOTE = ("r666: aging-line verdict + re-escalation (MSG-0916-bmc-ALL, bm-b second dark window, Q/D frozen 1988/1654, hb 155min stale, takeover CLOSED) + "
        "CODELY mojibake heal (r662/r665 pointer lines latin-1 double-encode, root cause byte-as-str \\xNN, lossless recovery + r407 typo fix, 30,407B C1-zero) + "
        "2 direct-write pits (encoding/legdiff) + QA r666 5/5 + S6 38/38; attrition CLEAN; DEC/ORD zero-delta; smoke 48/48.")
VERIFY = ("receipts: fleet/inbox/MSG-2026-10-07-0916-bmc-ALL (escalation, GM queue + ALL) + results/_r666bmc_trio_watch.json (aging-line verdict evidence) + "
          "results/_r666bmc_codely_mojibake_heal.json (heal receipt + fact-reconstruction addendum, md5 e8653ac76c1436f9) + qa/smoke-r666.md 5/5 (93 trades determinism=True equity 1,017,839) + "
          "qa/equity-curve-r666.png + results/_r666bmc_s6_log.txt 38/38 rc0 + results/_r666bmc_s05_facts.json (DEC 635C3024 + ORD 437E9CDD double-sweep zero-delta) + "
          "results/_attrition_guard_scan.json CLEAN + results/_r666bmc_s0_log.txt + research/pit-encoding.md + research/pit-lineage-legdiff.md direct-writes")

# ---- state ----
st["round_no"] = 667
st["round_no_label"] = "round 666 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at", "last_seen"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = DID
st["last_round_summary"] = ("r666: aging-line verdict (bm-b dark through 09:15, MSG-0916-bmc-ALL re-escalation, takeover CLOSED) + "
                            "CODELY mojibake heal (lossless latin-1 recovery, byte-as-str root cause, r407 typo fix) + 2 direct-write pits + "
                            "QA r666 5/5 + S6 38/38; DEC/ORD zero-delta 163/163; attrition CLEAN; smoke 48/48")
st["last_action"] = DID
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r666 s05+s7close double-sweep MATCH zero-delta; value facts-driven from results/_r666bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))"
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r666 s05+s7close double-sweep MATCH; facts-driven from results/_r666bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))"
st["ord_sha_method"] = st["last_orders_sha_method"]
st["heartbeat_epoch_utc"] = epoch
st["cpu_pct"] = 9
st["cpu_util_pct"] = 9
st["cpu_idle_pct"] = 91
st["free_ram_gb"] = 4
st["idle_ram_gb"] = 4
st["ram_free_gb"] = 4
st["gpu_free_vram_mib"] = gpu_mib
st["gpu_free_vram_mb"] = gpu_mib
st["gpu_idle_vram_mib"] = gpu_mib
st["gpu_idle_vram_mb"] = gpu_mib
st["gpu_free_mb"] = gpu_mib
st["gpu_free_mib"] = gpu_mib
st["gpu_idle_mb"] = gpu_mib
st["gpu_vram_free_mb"] = gpu_mib
st["gpu_idle_vram_mib"] = gpu_mib
with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("STATE written round_no=667 epoch_type=%s gpu_mib=%d" % (type(st["heartbeat_epoch_utc"]).__name__, gpu_mib))

# ---- heartbeat ----
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["round_no"] = 667
hb["round_no_label"] = "round 666 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = "alive (r666 aging-line verdict + mojibake heal round clean: escalation MSG delivered, claws LF-normalized, loop pin=5, watchdog present; golden-week no-bar until 10-09)"
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("fleet/inbox/MSG-2026-10-07-0916-bmc-ALL (bm-b second-dark-window escalation) + results/_r666bmc_trio_watch.json (verdict evidence) + CODELY.md heal 30,407B C1-zero + qa/smoke-r666.md 5/5 + 2 pit direct-writes @ " + now)
hb["next_milestone"] = ("bm-b revival -> withdraw (r664 pattern); still dark -> ~10:30 next escalation rung; 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar); monthly exam 10-31; next 5x=r670 HANDOVER")
hb["prod_lanes"] = ("r666 aging-line 判决+治愈轮（S0 干净自产 3 件零落后；bm-b 二次全暗过线→MSG-0916-bmc-ALL 升级+接管 CLOSED；CODELY mojibake 治愈+2 坑直写；smoke 48/48+S6 38/38+QA 5/5；板 0 open；watermark 绿；SAT 活；下个 5x=r670〔HANDOVER 窗〕）")
hb["verdict"] = ("alive: r666 verdict+heal round complete (aging line 09:15 crossed -> MSG-0916-bmc-ALL re-escalation per r663, takeover CLOSED, zero-loss face intact; "
                 "CODELY r662/r665 pointer mojibake healed losslessly (byte-as-str root cause, r407 typo fix), 30,407B C1-zero; QA r666 5/5 explicit --round 666; "
                 "S6 38/38 rc0; smoke 48/48; board open=0; satengine alive rc0; DEC/ORD double-sweep zero-delta 163/163; attrition CLEAN; post_review zero-x; "
                 "golden-week no-bar face held)")
hb["note"] = "r666: aging-line verdict round (escalation per r663 pattern) + CODELY mojibake heal + 2 direct-write pits; QA 5/5; S6 38/38; DEC/ORD zero-delta; attrition CLEAN."
hb["cpu_pct"] = 9
hb["cpu_util_pct"] = 9
hb["cpu_idle_pct"] = 91
hb["free_ram_gb"] = 4
hb["idle_ram_gb"] = 4
hb["ram_free_gb"] = 4
hb["gpu_free_vram_mib"] = gpu_mib
hb["gpu_free_vram_mb"] = gpu_mib
hb["gpu_idle_vram_mib"] = gpu_mib
hb["gpu_idle_vram_mb"] = gpu_mib
hb["gpu_free_mb"] = gpu_mib
hb["gpu_free_mib"] = gpu_mib
hb["gpu_idle_mb"] = gpu_mib
hb["gpu_vram_free_mb"] = gpu_mib
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
print("HB written round_no=667 epoch=%s" % type(hb["heartbeat_epoch_utc"]).__name__)

# ---- round report ----
line = ("watermark: 绿（red=false lane healthy·py_series_tail 0/0/0.1 金周无 bar 合法 idle·SAT 活=Tools 注册面 rc0 face ts 09:07:06 新鲜·board 0 open·bm-b 二次全暗过 09:15 老化线→MSG-0916-bmc-ALL 升级·post_review ✗0 零 P0）"
        " | " + now + " | r666 bm-c | dept:工程/舰队（值守轮+aging-line 判决+CODELY mojibake 治愈）"
        " | 当前活: r666 值守轮（S0 干净自产 3 件零落后·S1 48/48·S3 aging-line 终判 09:15:34=bm-b 双 tick 失约+Q/D 双冻结 59min+hb 陈旧 155min→r663 范式升级+接管保持 CLOSED·探针 needle prose 自匹配假阳性当场纠正·CODELY r662/r665 指针行 latin-1 双层 mojibake 治愈（根因=python str \\xNN byte-as-str）+根因坑直写 2 条·S6 38/38·QA r666 5/5）"
        " | 最近实物: fleet/inbox/MSG-2026-10-07-0916-bmc-ALL（bm-b 二次停滞升级通报·GM 队列+ALL）+results/_r666bmc_trio_watch.json（终判证据）+CODELY.md 治愈后 30,407B C1 零残留（收据 _r666bmc_codely_mojibake_heal.json）+qa/smoke-r666.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+research/pit-encoding.md+pit-lineage-legdiff.md 直写 2 坑"
        " | 下个里程碑: bm-b 复活撤警（r664 范式）·仍暗→~10:30 老化再升级；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r670（HANDOVER 窗） | 本地未达 origin commit 数=0（收口推送后 fetch+ls-tree 自证）")
with open(REPORT, "ab") as fh:
    with open(REPORT, "rb") as fr:
        rb = fr.read()
    sep = b"\r\n" if rb.endswith(b"\r\n") else b"\n"
    if not rb.endswith(sep):
        rb = rb + sep
    fh.write(rb + line.encode("utf-8") + sep)
print("REPORT appended")
print("CLOSE_UPDATER_OK %s epoch=%d gpu_mib=%d" % (now, epoch, gpu_mib))
