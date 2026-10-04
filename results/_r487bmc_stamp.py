"""r487 bm-c S7-close stamp: delivery proof into round report, MSG-1810
processed, state/heartbeat next-pointer closure, CODELY dedup check,
satengine daemon faces absorbed. Laws: r446 probe-to-file, r679 marker
count gates, r678 roundtrip-stable faces only (state/hb verified stable
this window), r641 bytes needle count==1 surgery."""
import json
import os
import shutil
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(REPO, "round_reports-bm-c.md")
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
CODELY = os.path.join(REPO, "CODELY.md")
MSG = os.path.join(REPO, "fleet", "inbox",
                   "MSG-2026-10-04-1810-bma-ALL-w3fin-yield-exec.md")
MSG_DONE = os.path.join(REPO, "fleet", "inbox", "processed",
                       "MSG-2026-10-04-1810-bma-ALL-w3fin-yield-exec.md")
OUT = os.path.join(REPO, "results", "_r487bmc_stamp_out.txt")
lines = []

# 1. round report: delivery proof placeholder -> actual (idempotent)
raw = open(RR, "rb").read()
needle = "本地未达 origin commit 数=<PUSH_VERIFY>".encode("utf-8")
repl = ("本地未达 origin commit 数=0 (DELIVERED: round commit fd2843fba + "
        "merge wave 35262eb66, push_verify ahead=0 behind=0 tip==remote)"
        ).encode("utf-8")
if raw.count(needle) == 1:
    open(RR, "wb").write(raw.replace(needle, repl))
    lines.append("rr delivery proof stamped")
elif raw.count(repl) == 1:
    lines.append("rr delivery proof already stamped (idempotent skip)")
else:
    raise AssertionError(f"rr needle/repl state unexpected "
                        f"{raw.count(needle)}/{raw.count(repl)}")
raw2 = open(RR, "rb").read()
assert raw2.count(repl) == 1 and raw2.count(needle) == 0

# 2. MSG-1810 -> processed (idempotent)
if os.path.exists(MSG):
    shutil.move(MSG, MSG_DONE)
    lines.append("MSG-1810 processed (bm-a yield executed, zero-write kill, "
                 "ADOPT posture; receipt watch closed)")
else:
    assert os.path.exists(MSG_DONE)
    lines.append("MSG-1810 already processed (idempotent skip)")
assert not os.path.exists(MSG) and os.path.exists(MSG_DONE)

# 3. CODELY dedup checks (r453/r479 family): r487 entry once, r486
#    yield-merge pit once; marker judgment = LINE-START form only
#    (r657/r453 law: inline literal '<<<<<<<' is legal pit text)
ct = open(CODELY, "rb").read()
n487 = ct.count("r487 bm-c] judge-finalize 工时标定坑".encode("utf-8"))
n486 = ct.count("r687 yield a6fc0132d".encode("utf-8"))
n1810 = ct.count("MSG-2026-10-04-1810".encode("utf-8"))
bad_markers = [ln for ln in ct.split(b"\n")
               if ln.strip().startswith(b"<<<<<<<")
               or ln.strip().startswith(b">>>>>>>")]
lines.append(f"CODELY check: r487-entry x{n487} (exp 1), r486-yield-pit "
             f"x{n486} (exp 1), msg1810-refs x{n1810}, "
             f"line-start-markers {len(bad_markers)} (exp 0)")
assert not bad_markers, bad_markers[:2]
assert n487 == 1, n487
assert n486 == 1, n486

# 4. state: next item-(b) closure + delivery evidence in verify
st = json.load(open(STATE, encoding="utf-8"))
assert st["round_no"] == 487
st["next"] = (
    "(a) CLOSED-SCOPE CONTINUATION: product lands ~22:1x -> run python "
    "results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS receipt (complete "
    "+ 777 cells + prev_total 646799 + total 647576 + single chain block "
    "+ seed 20285600 + ckpt 0 dup + pool 4/4) -> targeted commit+push -> "
    "48h CEO report clock starts (<=10-06 evening) -> treasure-capture "
    "question (TREASURE_REGISTRY + METHODOLOGY_ASSETS) -> prereg sec.7/8 "
    "judge-phase backfill (w2 precedent lines). (b) DONE THIS ROUND: bm-a "
    "yield EXECUTED per MSG-1810 (pid 32480 killed clean zero-write, "
    "quarantine fix verified 70/70 head 646799, ADOPT posture for bm-c "
    "product; MSG processed). (c) fund-trio finalize 10-05 10:30 (bm-b "
    "owner, watch only). (d) O-2115/O-2030 acceptance 10-08. (e) market "
    "reopen 10-09. (f) CODELY hot layer 94.5KB water note (post-r447 "
    "entries; sweep candidate window after W3 judge closure, group "
    "surface per r504).")
st["verify"] += (" | r487 stamp: merge wave 8-UU canon-resolved + "
                 "DELIVERED 35262eb66 (ahead=0 behind=0 push_verify) + "
                 "MSG-1810 processed (yield executed) + CODELY dedup "
                 "check r487x1/r486-yield-pitx1")
st["did"] += (" (8) merge origin/main wave (bm-a r689/691 + bm-b trio "
              "keepalives): 8 UU resolved per canon (receipt "
              "_r487bmc_merge_resolve.json: pool per-face max-merge 3 "
              "newer-theirs + 371 same + zero regressions; token per-key "
              "union side_pick=8; snapshots ts-newer ours) + MSG-1810 "
              "read+processed (bm-a yield executed, sole-finalize "
              "confirmed) + delivery self-proof stamped.")
st["last_round"] = (
    "r487 bm-c: judge-finalize custody (w2-calibrated ETA ~4.5h -> "
    "~22:1x; law in CODELY) + one-command adoption chain live-fired "
    "IN_FLIGHT + merge wave 8-UU canon-resolved + MSG-1810 yield-receipt "
    "processed (bm-c 33768 sole finalize) + DELIVERED 35262eb66")
st["last_round_at"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
st["updated"] = st["last_round_at"]
st["updated_at"] = st["last_round_at"]
json.dump(st, open(STATE, "w", encoding="utf-8", newline=""), indent=1,
          ensure_ascii=False)
chk = json.load(open(STATE, encoding="utf-8"))
assert chk["round_no"] == 487 and isinstance(
    chk["heartbeat_epoch_utc"], int)
lines.append("state next/verify/did updated + self-proof")

# 5. heartbeat: prod_lanes yield-receipt closure
hb = json.load(open(HB, encoding="utf-8"))
hb["prod_lanes"] = (
    "W3-JUDGE lane: 4/4 shards done+flipped; judge-finalize --wave 3 "
    "SOLE in flight on bm-c (pid 33768, correct caliber 646,799, ETA "
    "~22:1x); bm-a yield EXECUTED per MSG-1810 (pid 32480 killed "
    "zero-write, ADOPT posture for bm-c product, quarantine fix "
    "verified 70/70); CONTEST-YTD-P1-RC-0OF1 = bm-b keepalive RAM-gated "
    "(autofill face); FUND trio NULLS bm-b in-flight (watch only); "
    "boards empty; no new orders")
hb["verdict"] = (
    "r487 bm-c: judge-finalize custody (w2-calibrated ETA ~4.5h, lands "
    "~22:1x; law in CODELY) + adoption chain live-fired IN_FLIGHT + "
    "merge wave 8-UU canon-resolved + MSG-1810 yield executed (bm-c sole "
    "finalize) + DELIVERED 35262eb66")
json.dump(hb, open(HB, "w", encoding="utf-8", newline=""), indent=1,
          ensure_ascii=False)
chk2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int)
lines.append("heartbeat prod_lanes/verdict updated + self-proof")

open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("STAMP_OK:", " | ".join(lines))
