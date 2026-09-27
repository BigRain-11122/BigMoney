# -*- coding: utf-8 -*-
"""R345 bm-a S7 wrap-up: state round_no, round report line, heartbeat
(fresh epoch+clock at write, r96 law), CODELY.md pit entry (4-question gate),
HANDOVER 5x anchor insert (round 345 = 5x69)."""
import io
import json
import time
import datetime

# ---- fresh time at write (r96 law: epoch & clock same read, no reuse) ----
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
stamp = clock  # e.g. 2026-09-27T19:2x:xx+08:00

# ---------------- state ----------------
s = json.load(io.open("state-bm-a.json", encoding="utf-8"))
s["round_no"] = 345
s["did"] = ("R345: W2-B RUNNER BUILD LANDED (build slice f5822d92 post-rebase): "
            "scripts/census_fusion_s2_w2b.py (cross-wave D>=1 fusion census "
            "N=5,620 = 5,204 cand + 16 D-controls + 400 nulls rejection-"
            "forced >=1D; W1+W2A machinery imported not rewritten; A-sidecar "
            "read-only reuse validated vs w2_roster + W2A.prep_state "
            "fallback; D8 in-runner sha256 fail-closed gate; grid anchors "
            "in D-window ~47 weekly signals; selftest 7/7 hermetic) + "
            "scripts/census_w2b_d8_export.py bm-a lane (judged-construct row "
            "laws mirrored: dtype=str coerce/collapse 1e-3/unverifiable/dup "
            "keep-last/turnover>0 guard; selftest 9/9) + real-panel export "
            "60.4MB (250x5,228x8, sha 9febb7b4b5fab260..., collapse_reject "
            "116,259 = %.10g latent defect disclosed) + TRANSFER plan-A "
            "branch transfer/w2b-d8 pushed + worktree restored r90 law + "
            "pool entry CENSUS-FUS-S2-W2B status=waiting lane=bm-b deps= "
            "D8-receipt + W2-A-finalize + MSG-20260927-1912 SOP to bm-b")
s["verify"] = ("W2-B selftest 7/7 (enum 284/4920/16/400=5620 + sha gate "
               "fail-closed + two-dir worker glue) + D8 export selftest 9/9 "
               "+ artifact sha=manifest + transfer branch on origin + "
               "rebase 28-UU zero-left (ls-files -u empty) + smoke 25/25 + "
               "S6 33/33 rc=0 + orders 96/96 double-scan")
s["next"] = ("bm-b: receive D8 per MSG SOP (checkout transfer/w2b-d8 -- "
             "data/census_w2b/w2b_d8_faces.npz + restore --staged) -> W2-A "
             "finalize -> probe once -> W2-B run (ledger N 5,620 at "
             "finalize only); AH panel spawn throttle 23min<30min -> next "
             "round re-spawn window; UNC face after W2-A per sec.9.3")
s["last_round_at"] = stamp
s["current_task"] = ("r345: W2-B runner build landed + D8 artifact "
                     "transferred (bm-b lane queued after W2-A finalize)")
io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(s, ensure_ascii=False, indent=2) + "\n")
print("state round_no -> 345")

# ---------------- round report ----------------
rep_line = (
    f"{stamp} | R345 bm-a (dept:工程+研究) | WM first-line verdict: green "
    "(py_low_board_clear legal-idle @19:11 probe: board 0 open/96 claimed "
    "+ bandit parked MF-panel + pool W2-A ready lane=bm-b R31 no-touch + "
    "W2-B waiting双dep; audit v2.3 CLEAN flags=[]) | did: (A) S3 closed "
    "loop W2-B RUNNER BUILD + EXPORT + TRANSFER: census_fusion_s2_w2b.py "
    "built (mirror W2-A; N=5,620 cross-wave D>=1; W1/W2A import-only; "
    "A-sidecar read-only reuse + prep fallback; D8 sha256 in-runner "
    "fail-closed; selftest 7/7) + census_w2b_d8_export.py built+ran on "
    "bm-a sina panel (5,228 csv; laws mirrored from judged construct incl. "
    "dtype=str coerce/collapse 1e-3=116,259 rejected %.10g latent defect "
    "disclosed/unverifiable=0/dup=0; selftest 9/9; npz 60.4MB sha "
    "9febb7b4b5fab260... + manifest git-tracked) + TRANSFER plan-A branch "
    "transfer/w2b-d8 pushed + worktree restore r90 law + pool entry "
    "CENSUS-FUS-S2-W2B status=waiting lane_owner=bm-b (deps: D8 receipt + "
    "W2-A finalize) + MSG-20260927-1912 SOP (probe-once-then-run) | (B) "
    "S0.5 orders 96/96 zero-unacked double-scan + decision review: "
    "D-20260927-09 (BigMoney conflict-res two-fix) already executed/closed "
    "via F-20260927-03, D-08/D-10 non-BigMoney-execution-face zero action | "
    "(C) S1 smoke 25/25 | (D) S6 33/33 rc=0 Sunday no-op family (regime "
    "ORANGE shadow breadth 0.77 / clock ORANGE_COOL sleeves=4 activated=0 "
    "/ live.paper OK / t35v PASS zero-pending / t24 22-22 / collectors "
    "no-op-throttled honest / export+report+build+token refreshed) | (E) "
    "mid-round rebase storm vs bm-c r98: 28-UU same-window S6 family "
    "resolved per skill (classifier 12 + 16 hand-classified snapshots; "
    "compute_audit history 201|201->202 union / x2log 906|906->912 line "
    "union / autofill launches 48|48->48 identical-key union + last_tick "
    "same-second tie->HEAD / twin REPORT md same-side coupled / snapshot "
    "M-fresher take-new byte-verbatim; 8 files ts-probe-miss (updated/"
    "last_attempt not in probe key family) re-resolved explicit + side-diff "
    "re-verify zero-loss; resolvers archived _r345bma_resolve{,2}.py) | "
    "verify: selftests 7/7+9/9 + sha gate manifest match + transfer branch "
    "on origin + rebase zero-UU + S6 33/33 | next: bm-b receives D8 -> "
    "W2-A finalize -> probe once -> W2-B run; AH spawn throttle window "
    "next round; UNC face after W2-A per sec.9.3\n")
with io.open("logs/iteration-loop/round_reports-bm-a.md", "a",
             encoding="utf-8", newline="") as fh:
    fh.write(rep_line)
print("round report appended")

# ---------------- heartbeat ----------------
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["machine_id"] = "bm-a"
hb["last_seen"] = stamp
hb["current_task"] = s["current_task"]
hb["cpu_cores"] = 32
hb["verdict"] = ("healthy (r345: W2-B runner build landed + D8 artifact "
                 "transferred; smoke 25/25 + S6 33/33; W2-A burn=bm-b lane "
                 "watch alive; W2-B pool waiting双dep)")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 345
io.open("fleet/machines/bm-a.json", "w", encoding="utf-8",
        newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=2)
                            + "\n")
check = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in check["clock_read"], "clock_read must be T-separated"
print("heartbeat: epoch", epoch, "clock", clock, "round 345 OK")

# ---------------- CODELY.md pit entry ----------------
pit = (
    f"- [{stamp[:16]} r345 bm-a] 坑律：deep-ts 探针键族完备性——resolver 取新探针键表漏 "
    "`updated`/`last_attempt` 生产者拼写→探针空判 tie→误取旧侧（8 件实弹：heat snapshots 3→0 "
    "+ paper regime_guard enforce 披露面全丢）；正典=逐件显式写时键探（updated/last_attempt/"
    "generated_at）+解后同键异值 side-diff 复验（键集同+值分歧=探针 miss 疑点必深查）+hermetic "
    "selftest 路径换元必须覆盖全部路径全局（半换元静默读真面板 79s 副作用）——指针=results/"
    "_r345bma_resolve2.py+8 件重解内联。\n")
src = io.open("CODELY.md", encoding="utf-8").read()
anchor = "- [2026-09-27 19:11 r98 bm-c]"
i = src.find(anchor)
assert i > 0, "r98 anchor not found"
src = src[:i] + pit + src[i:]
io.open("CODELY.md", "w", encoding="utf-8", newline="\n").write(src)
import os
print("CODELY.md appended, bytes:", os.path.getsize("CODELY.md"))

# ---------------- HANDOVER 5x anchor ----------------
h = io.open("research/HANDOVER.md", encoding="utf-8").read()
anchor_line = "> 本文件由循环每 5 轮核对更新一次（mandate 已写明）。最近核对=bm-a round 335"
i = h.find(anchor_line)
assert i > 0, "HANDOVER anchor not found"
new_anchor = (
    f"> 最近核对=bm-a round 345（{stamp[:16]}·对账增量=本窗 bm-a R336-345 行"
    "【bm-a R336-345 窗：**W2-A/W2-B 双普查线点火+同窗撞车解常态化**——R336-343 "
    "t54 网格 LA-LD/DA-DD+DECISION-CHAIN-E2E+PROSPECT-REGIME-SEGMENTS 池批烧收"
    "+sina construct P1 判定（R338·D 族 standalone REJECT=判据锚）+S6 常驻撞车解多波"
    "（r339/r341/r343）；R344 W2-B sec.9.4 冻结（D8-only N=5,620·E-heat 诚实降格"
    "·seed 20282500 R250 同 commit）；R345 W2-B runner build 落地（跨波 D≥1 "
    "census_fusion_s2_w2b.py·W1/W2A 机器面 import 不重写·A 侧车只读复用+prep 回退"
    "·selftest 7/7）+D8 导出件 60.4MB sha 门禁 fail-closed+TRANSFER A 方案分支 "
    "transfer/w2b-d8 已推+池条目 waiting（bm-b 车道·双 dep=D8 传输回执+W2-A "
    "finalize）+bm-c r98 同窗 28-UU 风暴解（快照族 M-fresher 取新+8 件 ts 探针漏键"
    "重解零丢失）】产物清单实况=runnable_pool 80 条（W2-A ready bm-b 燃烧中 ETA "
    "~21:10+W2-B waiting 双 dep+其余 done 收割面齐）+纸盘/采集/维护链全绿+smoke "
    "25/25）\n")
h = h[:i] + new_anchor + h[i:]
io.open("research/HANDOVER.md", "w", encoding="utf-8", newline="\n").write(h)
print("HANDOVER 5x anchor inserted (round 345)")
print("ALL WRAP DONE at", stamp)
