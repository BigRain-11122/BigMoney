# -*- coding: utf-8 -*-
"""r812 bm-c correction face (zero-run correction precedent r251/r280, honest
disclosure, NOT an amend of pushed commits -- r731 law). Fixes two narrative
inaccuracies pushed with the r812 row + updates the delivery sync block:
(1) did item-5 tail claimed a post-close --auto re-run returned
    'declared=worked'; the LIVE re-run returned 'declared=claimed' (engine
    made a fresh pool claim inside the window; claim precedence over work is
    by design);
(2) the work-detection leg was live-DEAD at first attempt (module-level CNW
    undefined -> NameError swallowed by _git's except-Exception -> silent
    short-circuit), found by the re-verification probe, fixed in-round
    (module-level CNW + except-path stderr surface + selftest cnw-consistency
    42nd leg), post-fix live re-proof = 31 work paths hit.
Pit law entry verbatim landed in research/pit-tooling.md (1,251B, direct-write
precedent r666/r747; CODELY.md main-file headroom 176B < pointer line, pointer
deferred to next mini-split window -- disclosed)."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
HM = now.strftime("%H:%M")[:4] + "x"

OLD_DID_TAIL = ("**实弹端到端双验：窗内 --auto=declared claimed（pool_claim="
                "w17-screen-0of8·引擎真 claim 被结构化捕获）+close commit 后复验 declared=worked（work_paths 命中 "
                "Tools 面）**·tech 队列 6→5（T7 队头）；")
NEW_DID_TAIL = ("实弹验证=claim 腿双场命中（17:24 w17-screen-0of8+17:32 w17-screen-1of8）·close 后复验实跑=declared "
                "claimed（引擎新 claim 在窗·优先级律按设计先于 work）——预写「declared=worked」为超前叙事失误·见 r812-correction；"
                "work 检测腿首跑=live 死腿（_git 引用未定义模块级 CNW→NameError 被 except 吞=静默短路·半死态最险）"
                "→当场修（模块级 CNW+except stderr 面+selftest cnw-consistency 第 42 腿）→修复后 live 重证 31 work "
                "paths 命中 Tools/qa/fleet 面→坑律 verbatim 入 research/pit-tooling.md（r666/r747 直写先例）"
                "·tech 队列 6→5（T7 队头）；")

OLD_SELFTEST_DID = "selftest 9→41 腿全绿"
NEW_SELFTEST_DID = "selftest 9→42 腿全绿（41+cnw 回归腿）"

OLD_VERIFY = ("+ live --auto dual verification (pre-commit window: declared=claimed pool_claim=w17-screen-0of8; "
              "post-close-commit re-run: declared=worked work_paths hit) + iteration_loop.ps1 ParseFile 0 errors ")
NEW_VERIFY = ("+ live --auto verification (claim leg dual-hit 17:24/17:32 pool_claim w17-screen-0of8/1of8; "
              "close re-run=claimed per precedence, engine claim in window -- pre-pushed narrative said worked, "
              "CORRECTED per zero-run precedent; work leg first live-fire exposed r812 CNW silent-NameError "
              "dead-leg -> fixed in-round (module-level CNW + except stderr surface + selftest cnw-consistency "
              "42nd leg) -> post-fix live re-proof 31 work paths incl Tools faces + pit verbatim in "
              "pit-tooling.md 1,251B r666/r747 direct-write, CODELY pointer deferred to next mini-split window) "
              "+ iteration_loop.ps1 ParseFile 0 errors ")

OLD_VERIFY_ST = "idle_trigger selftest 41/41 (32 new T6 legs: path classifier 26 + daemon-subj 3 + log-line 3) "
NEW_VERIFY_ST = "idle_trigger selftest 42/42 (33 new T6 legs: path classifier 26 + daemon-subj 3 + log-line 3 + cnw-consistency 1) "

CORRECTION_LINE = (
    "2026-10-09T" + HM + "+08:00 | r812-correction | r812 行两处修正案（零跑修正案先例 r251/r280·如实留痕非结果驱动"
    "·不 amend 已推 commit·r731 律）：①did ⑤项尾「close commit 后复验 declared=worked」与实况不符——复验实跑="
    "declared claimed（引擎 w17-screen-1of8 新 claim 在窗·claim 优先级律按设计先于 work）；②work 检测腿首跑=live "
    "死腿（_git 引用未定义模块级 CNW→NameError 被 except-Exception 吞=静默短路·半死态：claim 腿活+work 腿死+离线 "
    "selftest 全绿=假象完整）→当场修（模块级 CNW+except stderr 面+selftest cnw-consistency 第 42 腿）→修复后 live "
    "重证 31 work paths 命中 Tools/qa/fleet 面→坑律 verbatim 入 research/pit-tooling.md（r812 条 1,251B·r666/r747 "
    "直写先例·主件 176B 余量不够指针行=指针行留下次 mini-split 窗如实披露）| state/hb verify+did 串同窗本 commit 修正"
)

changed = {}
for rel in ("state-bm-c.json", "fleet/machines/bm-c.json"):
    f = ROOT / rel
    d = json.loads(f.read_text(encoding="utf-8"))
    n = 0
    def fix(v):
        global n
        if isinstance(v, str):
            if OLD_DID_TAIL in v:
                v = v.replace(OLD_DID_TAIL, NEW_DID_TAIL); n += 1
            if OLD_SELFTEST_DID in v:
                v = v.replace(OLD_SELFTEST_DID, NEW_SELFTEST_DID); n += 1
            if OLD_VERIFY in v:
                v = v.replace(OLD_VERIFY, NEW_VERIFY); n += 1
            if OLD_VERIFY_ST in v:
                v = v.replace(OLD_VERIFY_ST, NEW_VERIFY_ST); n += 1
        elif isinstance(v, dict):
            for k in list(v):
                v[k] = fix(v[k])
        elif isinstance(v, list):
            v = [fix(x) for x in v]
        return v
    d = fix(d)
    if rel == "state-bm-c.json":
        d["sync"] = {
            "ahead": 0, "behind": 0,
            "last_push_ts": "2026-10-09T17:32:00+08:00",
            "note": ("r812 delivery chain: main commit 3b76145f2 + close 2f8dcd963 pushed OK first try "
                     "(fast-forward over own engine autofill claims 3f8f7923a, zero foreign faces) + fetch + "
                     "rev-list 0/0 self-verified; correction commit follows same channel"),
        }
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    changed[rel] = n

rr = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"
raw = rr.read_bytes()
if not raw.endswith((b"\r\n", b"\n")):
    rr.write_bytes(raw + b"\r\n")
    raw = rr.read_bytes()
rr.write_bytes(raw + CORRECTION_LINE.encode("utf-8") + b"\n")

print("correction applied:", changed, "| ledger line appended:", len(CORRECTION_LINE.encode("utf-8")), "B")
