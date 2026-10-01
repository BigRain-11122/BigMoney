"""r514 bm-a S7 bookkeeping: state bump + heartbeat + round report line.
Format-mirror writes (probe indent/EOL per file). Heartbeat epoch MUST be
JSON int (R170/R178 law), clock_read ISO-8601 with T (R262 law)."""
import json
import time
import datetime

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())


def load_probe(path):
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    lines = raw.decode("utf-8").splitlines()
    ind = 1
    for l in lines[1:]:
        if l.strip().startswith('"'):
            ind = len(l) - len(l.lstrip(" "))
            break
    trailing = raw.endswith(b"\n")
    return json.loads(raw.decode("utf-8")), crlf, ind, trailing


def dump_probe(obj, path, crlf, ind, trailing):
    out = json.dumps(obj, ensure_ascii=False, indent=ind)
    if crlf:
        out = out.replace("\n", "\r\n")
    if trailing and not out.endswith("\r\n" if crlf else "\n"):
        out += "\r\n" if crlf else "\n"
    open(path, "wb").write(out.encode("utf-8"))
    assert json.load(open(path, encoding="utf-8")) == obj


# ---------------- state-bm-a.json ----------------
P = "state-bm-a.json"
st, crlf, ind, trailing = load_probe(P)
st["round_no"] = 515
st["did"] = (
    "r514: T-140 crash-adoption + tree integration + LOWAMP-P2 IGNITION (round product): "
    "adopted GM-session T-140 products 1-3 after r471 verification (ledger -2008 "
    "compensation + verdict=void-with-face-note + watchlist re-entry + grammar-band "
    "revert + science_gates void face selftest 69/69) + froze LOWAMP-P2 prereg (c3c825c2a, "
    "exit-axis explicit gate FIRST application); integrated 39-commit backlog via r507 "
    "net path (git-2.55 rebase --continue false-refusal x3 -> commit-C/cherry-pick "
    "sequence; pool AA face resolved + indent-format healed; 5/5 empty picks=origin "
    "surgical absorption); built scripts/lowamp_p2.py (hold-through: engine default "
    "exit stack disabled key-by-key in params, engine/ zero-touch; selftest 10/10; "
    "r494 real-run leg=live probe PASS 14/14 13.2s, D6 hold-through fresh face "
    "max|corr|=0.1738 vs 0.7 ADMIT); pool +18 entries registered raw-text surgical "
    "(ids+shard-keys verified vs runner _entry_of 18/18 after catching LA-REP/LAREP "
    "key-drift pre-push); ignition LIVE (daemon burning ~50s/shard, fleet "
    "claim-to-saturation); S6 deferred chain 23/23 rc0 + tail legs (scorecard/report/"
    "live-usage/dashboard/token); merge_lane_views resolve+settle indent-probe fix "
    "(selftest 0 FAIL, real-run dual-case verified); CODELY 50KB waterline -> hot-cold "
    "re-archivation (50415->48643B, 5 flow lines verbatim to 202610.md, 2 new pitfall "
    "laws hot)"
)
st["verify"] = (
    "smoke 47/47 (late-run, zero FAIL); orders 136/136 zero-diff dual sweep; D-19 "
    "MATCH-unchanged 753F99E8 (r481 temp-clone recipe, upper-normalized); attrition "
    "guard 4 ledgers CLEAN; loop pin=8 Running + watchdog re-registered + claw MATCH; "
    "pool_dualrun ZERO-DRIFT streak 2/3 + reconcile all-faces zero-drift (r376 "
    "same-window law); P2 burn live: LAREP legacy base+x2 done, deep-base in flight"
)
st["next"] = (
    "r515: monitor LOWAMP-P2 burn (16 cells + nulls K=2000 + sens N=500) -> finalize "
    "when complete (append_ledger +2008, sec.7/sec.8 backfill, E1 known-answer "
    "reconciliation r492 law BEFORE consuming verdict); T-139 stage-B REV stock prereg "
    "draft (single-family corner per r513 D6 probe); families 2/3 stock-face designs; "
    "W8 finalize blocked on shard-12 origin-absence (bm-c local unpushed -- inbox ping "
    "if still absent)"
)
st["last_round_at"] = NOW_ISO
st["current_task"] = "T-140 action-4/5: LOWAMP-P2 burning in pool (18 entries, daemon fleet); finalize next round"
st["updated"] = NOW_ISO
st["last_round"] = 514
st["last_round_ts"] = NOW_ISO
st["loop_round"] = 514
st["notes"] = (
    "r514: r513 S7 crashed post-surgical-push (state stayed r512-face; r513 record "
    "lives in origin commit 3305af3ca + round report line -- state jump 513->515 "
    "disclosed); r514 adopted the crashed GM session per r471 (silent >45min, "
    "ticket next_steps handoff complete, all products verified before adoption)"
)
dump_probe(st, P, crlf, ind, trailing)
print("state: round_no=515, last_round=514")

# ---------------- heartbeat ----------------
H = "fleet/machines/bm-a.json"
hb, crlf, ind, trailing = load_probe(H)
hb["last_seen"] = NOW_ISO
hb["current_task"] = "T-140 LOWAMP-P2 judged batch burning (pool 18 entries, daemon fleet)"
hb["verdict"] = "loaded_ok_p2_burn"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW_ISO
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170)"
assert "T" in hb["clock_read"], "clock_read must be ISO with T (R262)"
dump_probe(hb, H, crlf, ind, trailing)
back = json.load(open(H, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int)
print("heartbeat: epoch int OK,", NOW_ISO)

# ---------------- round report ----------------
R = "round_reports-bm-a.md"
raw = open(R, "rb").read()
crlf = b"\r\n" in raw
eol = "\r\n" if crlf else "\n"
if raw and not raw.endswith(b"\n"):
    raw += eol.encode()
line = (
    f"{NOW_ISO} | r514——T-140 收养+整合+LOWAMP-P2 点火（本轮产品：runner "
    "lowamp_p2.py 落地+池 18 分片登记+D6 探针 ADMIT 0.1738+daemon 烧录活火）；r471 "
    "收养 GM 会话产物（verdict VOID 面+补偿分录-2008+watchlist 复列+P2 预注册冻结 "
    "c3c825c2a）；39-commit 积压经 r507 净路整合（假拒绝 x3→cherry-pick 序）； "
    "merge_lane_views 缩进探针双坑当场修复（池 21k 翻面治愈+selftest 0 FAIL）；"
    "CODELY 50KB 水位热冷整编（→48.6KB·5 行 verbatim 入 202610.md）| dept:策略+研究+工程 "
    "| WM=py_low_with_work_cands（合法：工作候选=本批 P2 在烧·daemon claim-to-saturation）"
    " | S6 链 23/23 rc0+尾腿绿 | 本地未达 origin commit 数=0（push 6a959cd27 后 fetch+ls-tree 自证）"
    " | 下轮：P2 finalize 守望（E1 对账先行）+T-139 stage-B REV prereg"
)
open(R, "wb").write(raw + line.encode("utf-8") + eol.encode())
print("round report: r514 line appended")
