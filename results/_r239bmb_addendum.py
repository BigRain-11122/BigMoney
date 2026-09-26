# -*- coding: utf-8 -*-
"""r239 addendum (bm-b): push-collision yield record corrections.
- state.json + heartbeat: reflect s4 yield (bm-a canonical owner T-74/T-75)
- T-75 yield_note correction: _-prefix concern inapplicable to canonical
  (their combat face does not read prospect_paper) -- FYI note only
- round report addendum line + CODELY race lesson (claim-time fetch gate)
"""
import io
import json
import subprocess
import time
from datetime import datetime

NOW = datetime.now()
TS = NOW.strftime("%Y-%m-%d %H:%M")
ISO = NOW.isoformat(timespec="seconds")

# ---- state.json correction
sp = "logs/iteration-loop/state.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["did"] = ("r239: T-74/T-75 claim race LOST per fleet/README s4 (bm-a claim 09:58:58 pushed 10:01:27 precedes "
             "bm-b 10:05; bm-b local fetch was 10:00:59 = one push behind) -> bm-b yields: same-window duplicate "
             "deliverables dropped in rebase (daily_report/DECISIONS/MARKET_CLOCK_COMBO/prompt-wiring/report+call "
             "pages), ticket yield_note corrected; bm-b keeps: S6 maintenance chain products, claim-race resolver "
             "provenance _r239bmb_*, scorecard pointer fix, CODELY lesson, bookkeeping; shared-state unions per "
             "classifier recipes zero-loss")
st["verdict"] = "YELLOW->GREEN (claim race lost; round product = maintenance + yield record; no work lost to duplication beyond the race window)"
st["next"] = ("T-74 s2 owner bm-a (bm-b contributions listed in yield_note); T-75 owner bm-a (extension suggestions "
              "FYI only); pre-claim fetch+rescan gate = new CODELY law; 09-28 Monday new-bar full chain; 10-01 "
              "monthly three-suite + v3 date gate; GPU-FACTOR-LANE-PROOF bm-a flip")
st["current_task"] = "r239 closed: T-74/T-75 yielded to bm-a per s4 commit-time order; maintenance chain green"
st["updated_at"] = ISO
st["last_seen"] = TS
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json corrected")

# ---- heartbeat correction
hp = "fleet/machines/bm-b.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = TS
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = ISO
hb["current_task"] = ("r239 closed: T-74/T-75 claim race yielded to bm-a per s4 (their 09:58:58 claim pushed "
                      "10:01:27; my 10:05 claim made on stale fetch 10:00:59); duplicate deliverables dropped in "
                      "rebase, yield_note on tickets, maintenance chain products kept")
hb["verdict"] = ("py_low_board_clear = legal idle (board: T-74/T-75 owned+delivered by bm-a this window; bandit 0; "
                 "pool 0 ready bm-b lanes; GPU-FACTOR-LANE-PROOF waits bm-a flip); round-start red lane "
                 "runnable-work-idle-low-cpu resolved by same-window execution on both machines")
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat corrected, epoch int OK")

# ---- T-75 yield_note correction (inapplicable _-prefix claim)
p = "fleet/tasks/T-2026-09-26-75-P1.json"
d = json.load(io.open(p, encoding="utf-8"))
d["yield_note"] = (
    "claim race r239 adjudicated per fleet/README s4: bm-a claim 09:58:58 precedes bm-b 10:05 -> bm-a canonical owner; "
    "bm-b same-window delivery (daily_report.py + DECISIONS + first report + S6 wiring) dropped from canonical in "
    "rebase (preserved in bm-b local history); correction r239 addendum: bm-b _-prefix concern is INAPPLICABLE to "
    "canonical (its combat face does not read prospect_paper, no _summary.json exposure) -- FYI only if owner later "
    "extends coverage to prospect dir: skip _-prefixed schema-foreign files per r157 law; dropped bm-b draft also "
    "carried PROSPECT observation rows + fill_guard action log + heat clock reading faces")
raw = io.open(p, "r", encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw else "\n"
out = json.dumps(d, ensure_ascii=False, indent=1) + "\n"
json.loads(out)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(out)
print("T-75 yield_note corrected")

# ---- round report addendum
RR = ("2026-09-26 {ts} | r239 addendum (bm-b): S7 push rejected (bm-a pushed 10:01:27 mid-my-round: claims 513168db "
      "09:58:58 + full triple-delivery 11ed3193 + their own rebase fdb3efd3) -> pull --rebase 2-commit replay, step1 "
      "1-UU x2 (tickets), step2 21-conflict batch (10 UU + 2 AA + 9 UU) -> s4 adjudication: bm-a claim 09:58:58 "
      "precedes bm-b 10:05 (my claim made on fetch stale by ONE push -- lesson below) -> bm-b YIELDS T-74/T-75: "
      "duplicate deliverables dropped (daily_report.py/DECISIONS.md/MARKET_CLOCK_COMBO.md/prompt wiring/report+call "
      "orphan pages), tickets keep bm-a claim + corrected yield_note (correction: _-prefix concern inapplicable, "
      "canonical combat face does not read prospect_paper); r221 rename _r239_claim/_r239_wire_prompt -> "
      "_r239bmb_* (both preserved); shared-state per classifier: post_review.jsonl union 567+567->583 zero-loss, "
      "autofill launches union cap50 + last_tick whole-dict (CRLF mirror), compute_audit history union "
      "200+201->202, regime history/transitions union, dashboard pair by twin generated_at 10:08>09:55 take-side3 "
      "wrapper-preserved, snapshots take-new; CODELY memory-union +1 line; poison scan 2 commits CLEAN (r231/r235b "
      "line-start) | lesson: 认领前 fetch+重扫门（claim-commit 必须紧贴 fetch 之后，board 读数跨他机 push 即陈旧）| 下轮: "
      "T-74 s2 owner bm-a; 09-28 周一 T-75 首自动 fire 观测（canonical 守卫语义由 bm-a 版本定）；10-01 月度三件套\n")
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(RR.format(ts=NOW.strftime("%H:%M")))
print("round report addendum appended")

# ---- CODELY race lesson
cp = "CODELY.md"
line = ("- [2026-09-26 10:4x] 坑律（bm-b r239·CEO 即时票双机同窗认领撞车·P0/E1 双向盲区实证）：**认领 commit 必须紧贴 "
        "git fetch 之后——board 读数一旦跨过他机 push 即陈旧（实弹：bm-b 10:00:59 fetch 后扫描见 T-74/T-75 open，10:05 认领；"
        "实况 bm-a 09:58:58 已认领并于 10:01:27 推上 origin，bm-b 本地不 fetch 即不知）**；裁决=fleet/README §4 commit 时间序后到让路"
        "（bm-a 09:58:58 < bm-b 10:05 → bm-b yield，同窗重复交付物 rebase 中让位丢弃、ticket 留 yield_note）；连带=心跳停滞>20min "
        "接管触发器与他机在飞轮次并存时，接管前必查 origin 末 push 时间戳非仅心跳；同窗竞速双交付=反重复铁律最痛形态，认领前 fetch 门为正解。"
        "指针=results/_r239bmb_resolve1.py+_r239bmb_resolve2.py+commit 8522b06e/4b98aa5c+round_reports r239 addendum\n")
with io.open(cp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("CODELY race lesson appended")
