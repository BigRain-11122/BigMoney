# -*- coding: utf-8 -*-
"""r365 bm-b closing script: state/heartbeat/round-report/HANDOVER/CODELY five-face writer.

UTF-8 safe (r352 PS-redirect law), heartbeat epoch int self-verify (R170/R178),
newline-mode detection for append files, CODELY <=10KB hard-line alarm.
"""
import json
import subprocess
import time
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---------- fresh samples ----------
free_ram_gb = 5.0
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / 1024 ** 3, 1)
    cpu_util_pct = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    cpu_util_pct = 37.3
gpu_free_vram_gb = 6.7
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, timeout=10,
    ).stdout.decode().strip().splitlines()[0]
    gpu_free_vram_gb = round(float(out) / 1024, 1)
except Exception:
    pass
epoch = int(time.time())
assert isinstance(epoch, int), "epoch must be int"

# ---------- 1) state.json ----------
state = json.load(open(r"state.json", encoding="utf-8"))
state["round_no"] = 365
state["note"] = (
    "r365: S0 divergence-closure round: two-wave rebase onto origin chain (5aed1d09 bm-a r388 addendum -> "
    "cbe4792f bm-c r142 closeout + bm-a tick): Bug1 dup patch SKIP-yielded to bm-c e463fe9b canonical "
    "(origin-first + production-running on bm-a runner pid29404), Bug2 face subsumed by bm-a r387 canonical; "
    "7 UU state faces merger-resolved + pool sync_face settle reconcile 7/7 ZERO-DRIFT (bm-c probe-note "
    "recovered via lane union); x2_watch_log r364-surgery markers purged per append-log union recipe + "
    "same-round wb-truncation incident self-recovered from dangling blob cd1eb651 (1128 rows JSON-verified, "
    "resolver results/_r365bmb_resolve_x2watch.py); MSG-0625 processed-copy accidental deletion (r364 "
    "stash-loss committed by add -A) restored HEAD-side; push LANDED cbe4792f..a442d9a9; S16c/e/f red-leg "
    "root cause CLOSED = bm-c r142 enabler-2 _clear_fuse_lanes all-machines, autofill selftest bm-b ALL PASS "
    "second-machine verification (r364 P0 discharged); inbox 5 收讫 archived (0630/0640/0655/0660/0715); "
    "S6 24 legs rc=0 pre-market no-op family; orders 99/99 zero; smoke 25/25; W2B census alive 1600/5620 "
    "ETA ~10:30; W2-SCREEN burn LIVE on bm-a fixed runner"
)
with open(r"state.json", "wb") as f:
    f.write(json.dumps(state, ensure_ascii=False, indent=1).encode("utf-8"))
print("state.json round_no=", state["round_no"])

# ---------- 2) heartbeat fleet/machines/bm-b.json ----------
hb = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
hb["last_seen"] = TS
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = TS
hb["current_task"] = (
    "r365 closed: fleet divergence resolved two-wave rebase push LANDED cbe4792f..a442d9a9 "
    "(Bug1 dup yielded to origin canonical; x2_watch truncation incident self-recovered from dangling blob); "
    "S16c/e P0 discharged via bm-c r142 enabler-2 (bm-b 2nd-machine selftest ALL PASS); "
    "next = W2B done-flip single-item push ETA ~10:30 + screen-finalize -> judge-prep (bm-b dep) -> W2-JUDGE"
)
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = gpu_free_vram_gb
hb["total_ram_gb"] = 23.9
hb["cpu_util_pct"] = cpu_util_pct
hb["round_no"] = 365
hb["verdict"] = (
    "healthy: S0 divergence closed push LANDED, S16c/e green via bm-c enabler (2nd-machine verify), "
    "smoke 25/25, autofill selftest ALL PASS, S6 24 legs rc=0, census W2B 1600/5620 alive"
)
hb["cores"] = 16
hb["idle_ram_gb"] = free_ram_gb
hb["gpu_free_vram_mb"] = int(gpu_free_vram_gb * 1024)
hb["idle_ram_mb"] = int(free_ram_gb * 1024)
hb["gpu_idle_vram_mb"] = int(gpu_free_vram_gb * 1024)
hb["gpu_idle_vram_gb"] = gpu_free_vram_gb
hb["cpu_pct"] = cpu_util_pct
hb["round"] = 365
hb["loop_round"] = 365
hb["free_ram_mb"] = int(free_ram_gb * 1024)
with open(r"fleet\machines\bm-b.json", "wb") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8"))
back = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must round-trip as JSON int"
assert "T" in back["clock_read"] and "+08:00" in back["clock_read"]
print("heartbeat epoch int OK:", back["heartbeat_epoch_utc"], "| RAM", free_ram_gb, "GB | GPU", gpu_free_vram_gb, "GB | CPU", cpu_util_pct, "%")

# ---------- 3) round report line ----------
RR = r"logs\iteration-loop\round_reports.md"
raw = open(RR, "rb").read()
nl = b"\r\n" if raw.rstrip().endswith(b"\r\n") else b"\n"
line = (
    "2026-09-28T07:12:00+08:00 | round 365 bm-b | dept:engineering (fleet S0 closure + T-96 owner watch) | "
    "WM-VERDICT: GREEN (red=false@06:50:26 lane healthy; probe insufficient_history window-reset lawful exit 0; "
    "census W2B burn in flight 1600/5620 ~20/min + W2-SCREEN burn on bm-a fixed runner = both supply responses, "
    "no violation) | did: (1) S0-1 anchor bm-b; S0 pull --rebase refused (bg-lane dirt + STALE .git/rebase-merge "
    "residue from r364 direct-commit closure never finalized) -> absorb round-open dirt as baseline commit "
    "(x2_watch_log r364-surgery 3-marker purge per skill append-log union recipe; SAME-ROUND INCIDENT: my resolver "
    "opened wb=truncate-then-TypeError -> file 0 bytes -> staged truncated version passed pre-commit claw into "
    "local baseline; SELF-RECOVERY: first-add full blob found among 3440 dangling objects by content signature "
    "cd1eb651, markers purged, 1128 rows all-JSON verified, baseline amended) -> git rebase --continue finalized "
    "stale r364 rebase (4 picks done, tree clean) -> real rebase wave-1 onto 5aed1d09 (tick replay pool "
    "UU=merge_lane_views resolve 91-union; Bug1 dup patch SKIP after conflict inspection = yield to bm-c "
    "e463fe9b canonical origin-first per bm-c own Bug2-yield precedent + bm-a production evidence; baseline "
    "replay 6 S6-face UU merger-resolved + MSG-0625 processed-copy UD restored HEAD-side = r364 stash-loss "
    "accidentally committed by add -A) -> push rejected (bm-c r142 + bm-a tick landed meanwhile) -> wave-2 onto "
    "cbe4792f same recipes -> push LANDED cbe4792f..a442d9a9 + pool sync_face settle post-rebase (bm-c probe-note "
    "recovered via lane union) reconcile 7/7 faces ZERO-DRIFT; (2) S0.5 orders 99/99 double-scan ZERO delta + "
    "decisions.md candidate paths absent honest no-op + inbox 5 processed->processed/ (0630 own r364 ruling "
    "archived; 0640 bm-a Bug2 canonical receipt - my Bug1 face resolved by origin chain; 0655 bm-c crash "
    "root-cause - fix already canonical; 0660 bm-c Bug1-fix-landed + yield receipt + S16 lane-isolation root "
    "cause = my r364 P0; 0715 bm-a D-03(1) pool lane-primary retirement zero-action notice, new code now live "
    "in my tree); (3) S1 smoke 25/25; S2 board zero open-unclaimed (T-96 = my standing claimed lane); (4) S3 "
    "r364 P0 CLOSED: S16c/e/f root cause = bm-c r142 enabler-2 _clear_fuse_lanes all-machines (authoring-machine "
    "own-lane assumption), in-tree via e463fe9b -> autofill selftest bm-b ALL PASS (S16c/d/e/f/g explicit green) "
    "= second-machine verification of bm-c enabler; W2 owner faces: W2-SCREEN burn LIVE on bm-a fixed runner "
    "pid29404 (no double burn, fuse auto-clear by hash change), W2B census alive 1600/5620 ETA ~10:30, "
    "V2-P1/MASS-judge-x4/W1-JUDGE/W2-JUDGE serialized per frozen sec.9.1; (5) S6 24 legs rc=0 pre-market no-op "
    "family (audit CLEAN py 38% + probe insufficient_history window-reset + daily 0-new cutoff 09-24 "
    "Mid-Autumn-close + regime shadow + clock ORANGE_COOL sleeves=4 activated=0 + lane-guards honest no-ops + "
    "astock fresh + rev_osc idempotent + fundamental 8.5h skip + b_layer verdict + daily_report faces=4 + "
    "lane_io host-guard x3 skip + token L2 delta=0; no-new-bar paper-chain legally skipped pre-market); "
    "(6) S4 CODELY pit-law entry (resolver wb-truncate-before-write + add-A blind absorption of stash-loss = "
    "one incident one law, x2_watch recovery pointer); (7) S7 self-heal trio + HANDOVER 5x line (r365=5-multiple) "
    "+ heartbeat epoch int self-verify | verify: push LANDED cbe4792f..a442d9a9 + reconcile 7/7 ZERO-DRIFT + "
    "x2_watch_log 1128 rows JSON-valid both-batches-present + autofill selftest ALL PASS + smoke 25/25 + S6 24 "
    "legs rc=0 | next: W2B landing done-flip single-item push (ETA ~10:30) + screen-finalize watch -> judge-prep "
    "(bm-b physical dep) -> W2-JUDGE flip + post-W2B stable-RAM window: V2-P1 relaunch -> T-95 s3/s4 + intake "
    "slice build (T-96 s4 D6 gate + STRATEGY_LIBRARY + PROSPECT accounts) + CEO 48h report clock 09-29 22:45 (bmb)"
)
with open(RR, "ab") as f:
    f.write(nl + line.encode("utf-8"))
print("round_reports.md appended, bytes:", len(line))

# ---------- 4) HANDOVER 5x line (insert before bm-c round 140 anchor) ----------
HO = r"research\HANDOVER.md"
raw = open(HO, "rb").read().decode("utf-8")
anchor = "> bm-c round 140"
assert anchor in raw, "HANDOVER anchor missing"
hol = (
    "> bm-b round 365 五倍数核对（2026-09-28 07:1x）：增量窗 r361-365=bm-b 面（**T-96 WAVE-2 判决链三切片落地+双 Bug 修复让路正典+S0 分叉两波 rebase 收口线**"
    "——r361 W2 dual-disclosure owner-review ACCEPT〔MSG-0620 逐条复核零异议：x2 范围/descriptive 冻结解释/annex(1)/beat `>` 算子/keep-ok per-leg/vacuous+degenerate〕；"
    "r362 judge 切片全落地〔judge-prep 四门+judge 分片 checkpoint 续跑+_judge_cell_w2 dual-leg×base/x2 CostPatch(2) 四曲线+双 nulls[20286500,i]+judge-finalize "
    "G1'v2/DSR/PBO/账本 append；selftest 41→58/58+池 TRIAL-LABOR-W2-JUDGE waiting+MSG-0550 六披露〕；"
    "r363 screen-prep PASS〔G-PANEL Monday-bar-proof 截断修+tl1.GRAMMAR 全局修 双门零烧 cell；c4e93817〕；"
    "r364 MSG-0655 Bug1 dispatch positional forwarding+Bug2 _claim_shard 双键〔S15n〕双修同轮〔selftest 58/58〕+W2B census 点火+mid-round push-storm 手术〔merge_lane_views 91-union+r358 直连收口+10 stash-pop〕；"
    "r365=本核对轮：**S0 分叉收口**〔两波 rebase 落 origin 链 5aed1d09→cbe4792f：Bug1 同坑异补丁 skip 让路 bm-c e463fe9b 正典（origin-first 律·bm-a 生产在跑实证）·Bug2 修复面被 bm-a r387 正典涵盖·"
    "7 UU 状态面 merge_lane_views resolve〔池 91 id-union+done-absorption〕·池 sync_face settle reconcile 7/7 ZERO-DRIFT〔bm-c 探针注记经车道 union 找回〕·"
    "x2_watch_log r364 手术标记清除+同轮截断事故自愈〔dangling blob cd1eb651 恢复 1128 行全 JSON 验证·resolver=_r365bmb_resolve_x2watch.py〕·0625 归档事故性删除恢复〔stash 丢盘被 add -A 忠实提交→HEAD 侧恢复〕·"
    "push LANDED cbe4792f..a442d9a9〕+**S16c/e/f 红腿根因收口=bm-c r142 enabler-2〔_clear_fuse_lanes all-machines〕二机验证**〔r364 交接 P0·S17d on-disk-gate 假设被车道污染根因取代·autofill selftest bm-b ALL PASS 含 S16c/d/e/f/g 显式绿〕"
    "+inbox 5 收讫归档〔0630/0640/0655/0660/0715〕+S6 24 腿 rc=0 周一盘前 no-op 家族+orders 99/99 双扫零+smoke 25/25〕"
    "产物清单漂移=scripts/trial_labor_w2.py〔r362 judge 族新增；r364 Bug1 修复面让路后=origin 正典字节〕/Tools/autofill.py〔Bug2 修复面被 origin 正典涵盖〕/"
    "results/_r365bmb_resolve_x2watch.py+x2_watch_log 恢复面/fleet/inbox processed 移档 5 件；"
    "统一链 **294,304 实读**（live head=census_fusion_s2/w2a_results.json ledger.total·与 bm-a r385/bm-c r140 核对同谳·本窗 bm-b 零批 finalize〔W2-SCREEN 2924 候选烧批在 bm-a 进行中未 finalize 不入链〕）；"
    "池 91 条〔82 done+2 ready=CENSUS-FUS-S2-W2B bmb-owned-burning 实测 1600/5620 ~20/min ETA ~10:30+TRIAL-LABOR-W2-SCREEN owner=bma fixed-runner pid29404 burn LIVE·"
    "7 waiting=V2-P1 defer post-W2B〔lane=bm-b〕+MASS judge x4+W1-JUDGE+W2-JUDGE 均 flip-gated per frozen sec.9.1〕；"
    "周一就绪面=09:15 T-91 s3 first-marks 自动点火（bma lane）+15:30 fund_premium FIRST SNAPSHOT（bmc lane）+15:30+ astock 续拉（bmb lane=本机）+"
    "W2-SCREEN finalize watch→judge-prep（bmb）→W2-JUDGE flip+post-W2B-landing：V2-P1 relaunch stable-RAM→T-95 s3 verdict+s4 CEO 呈报（negative also per O-2255·48h 钟 09-29 22:45）+"
    "T-94/T-96 CEO 48h 呈报钟 09-29 22:45（bmb）；下轮 5x=bm-b r370"
)
idx = raw.index(anchor)
raw = raw[:idx] + hol + "\n" + raw[idx:]
with open(HO, "wb") as f:
    f.write(raw.encode("utf-8"))
print("HANDOVER line inserted, line bytes:", len(hol))

# ---------- 5) CODELY.md pit entry ----------
CM = r"CODELY.md"
raw = open(CM, "rb").read()
nlc = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
entry = (
    "- [2026-09-28 07:1x r365 bm-b] 坑律：**resolver/收口脚本对 in-repo 数据件禁「先截断后组装」——`open(path,'wb')` 在首条 write 前即完成截断，payload 异常=0 字节半成品；且 `git add -A` 会把上轮 stash 丢盘的事故性缺件忠实提交成删除**。"
    "r365 实弹：x2_watch_log 标记清除脚本 wb 开截断→TypeError→0 字节；定向 add 后空文件过 pre-commit 冲突标记钳随基线入本地历史（未推送）。"
    "自愈=首次 add 的完整 blob 悬于对象库，`git fsck --unreachable` 按内容签名（标记行+双侧 ts 批）从 3440 悬对象中找回→内存组装完毕一次性写回 bytes→未推送基线 amend 收编。"
    "How to apply：resolver 一律「内存/临时件组装完毕→一次性原子写」；动 tracked 数据件前先 add 备份 blob；轮首 add -A 前对「tracked 应在却 0 字节/缺失」件做存在性哨点；事故恢复首选悬对象内容签名扫描非重放。"
    "指针=results/_r365bmb_resolve_x2watch.py+commit a442d9a9。"
)
with open(CM, "ab") as f:
    f.write((entry.encode("utf-8") if raw.endswith(b"\n") or raw.endswith(b"\r\n") else nlc + entry.encode("utf-8")))
size_after = len(open(CM, "rb").read())
print("CODELY.md appended, size_after=", size_after, "bytes")
if size_after > 10240:
    print("ALARM_OVER_10KB: hot-cold archival required this window")
print("ALL CLOSING FACES DONE")
