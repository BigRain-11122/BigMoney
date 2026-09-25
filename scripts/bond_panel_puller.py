"""T-68 WAVE-3A bond panel puller -- prereg research/BOND_CARRY_WAVE3A_PREREG.md sec.6 panel face.

Pulls the frozen candidate manifest's sina klc full-history (bond_zh_hs_daily
face, r206 capacity probe verified live) into per-member CSV corpus
data/bond_w3a/ (gitignored, regenerable: puller in-repo = reproducible).
Pool-carried batch per prereg sec.0-1 (O-1137 carrier): ~2.5s/member
network-serial, checkpoint = CSV presence + member registry (resume skips
resolved members), conn-fuse = 3 consecutive non-404 member failures ->
30min honest no-op cooldown (r175 family; autofill re-fire hits the cooldown
gate, no request pressure), date monotonic/duplicate guard (sec.6),
no-face registry (klc 404 = structurally zero-capacity member: excluded
from candidates, kept in capacity denominators per R179 extension).

Subcommands:
  manifest                      spot face -> freeze results/bond_w3a/candidates.json
                                (1 network request, control-plane leg)
  run --shard I --of M [--limit K]   pull shard slice; --limit = smoke face
                                (stdout summary only, no shard summary file)
  status                        read-only inventory (manifest vs corpus vs registry)
  selftest                      hermetic fixtures, zero network (404 no-face /
                                zero-volume bar / date-duplicate shapes + fuse +
                                resume + cooldown, r157/r180 production-pairing law)

Evidence window is enforced at the RUNNER face (prereg sec.2 evidence_cutoff
2026-09-24, forward lockbox); this corpus face stores raw full history.
Exit codes: 0 = shard resolved / no-op / smoke; 2 = unresolved fails or
conn-fuse trip (honest, checkpoint preserved).
"""
import json
import math
import os
import sys
import time
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bond_capacity_probe import classify, is_no_face  # noqa: E402  (reuse, zero re-impl)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "bond_w3a")
RES_DIR = os.path.join(ROOT, "results", "bond_w3a")
MANIFEST = os.path.join(RES_DIR, "candidates.json")
REGISTRY = os.path.join(RES_DIR, "member_registry.json")
FUSE = os.path.join(RES_DIR, "conn_fuse.json")

SLEEP_S = 2.5            # house rate-limit convention (sina faces)
RETRY = 2                # fetch attempts per member
FUSE_N = 3               # consecutive non-404 member failures -> fuse trip
FUSE_COOLDOWN_S = 1800   # 30min honest no-op cooldown after trip
CSV_MIN_BYTES = 40       # header + >=1 data row

EXCLUDE_NAME = ("特别国债", "特国")   # prereg sec.2: semantics-unverified special faces


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _atomic_write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def fetch_spot():
    import akshare as ak
    return ak.bond_zh_hs_spot()


def fetch_daily(sym):
    import akshare as ak
    return ak.bond_zh_hs_daily(symbol=sym)


def is_candidate(code, name):
    """Frozen filter rule (prereg sec.2 universe): name-contains-国债 government
    face, special treasuries excluded (semantics probe covered plain 国债 only),
    convertibles excluded via probe classifier (T-60 domain)."""
    n = str(name)
    if "国债" not in n:
        return False
    if any(k in n for k in EXCLUDE_NAME):
        return False
    return classify(code, name) == "treasury"


def cmd_manifest():
    spot = fetch_spot()
    missing = [c for c in ("代码", "名称") if c not in spot.columns]
    if missing:
        print("manifest FAIL: spot missing cols", missing)
        return 2
    rows = [{"code": str(r["代码"]), "name": str(r["名称"])}
            for _, r in spot.iterrows()]
    buckets = {}
    for r in rows:
        b = classify(r["code"], r["name"])
        buckets[b] = buckets.get(b, 0) + 1
    special = [r for r in rows if "国债" in r["name"]
               and any(k in r["name"] for k in EXCLUDE_NAME)
               and classify(r["code"], r["name"]) == "treasury"]
    cands = [r for r in rows if is_candidate(r["code"], r["name"])]
    seen, dedup = set(), []
    for r in cands:
        if r["code"] not in seen:
            seen.add(r["code"])
            dedup.append(r)
    dedup.sort(key=lambda r: r["code"])
    out = {"probe": "T-68 WAVE-3A panel candidate manifest (frozen universe face)",
           "frozen_at": now_iso(),
           "source": "akshare.bond_zh_hs_spot (sina spot 800 face, r206 verified)",
           "spot_rows": len(rows),
           "bucket_dist": buckets,
           "filter_rule": "name contains 国债 AND NOT (特别国债|特国) AND "
                          "classify==treasury (convertibles excluded per T-60)",
           "excluded_special_treasury_n": len(special),
           "excluded_special_treasury": special,
           "dup_codes_dropped": len(cands) - len(dedup),
           "spot_head_repr": [str(r) for r in rows[:3]],
           "n_candidates": len(dedup),
           "candidates": dedup}
    _atomic_write_json(MANIFEST, out)
    chk = json.load(open(MANIFEST, encoding="utf-8"))
    assert chk["n_candidates"] == len(dedup) > 0
    print("MANIFEST OK ->", MANIFEST, "| spot rows:", len(rows),
          "| buckets:", buckets, "| special excluded:", len(special),
          "| candidates:", len(dedup))
    return 0


def shard_slice(cands, i, m):
    """Contiguous position ranges: shard i of m covers
    [i*ceil(n/m), min((i+1)*ceil(n/m), n))."""
    n = len(cands)
    chunk = max(1, math.ceil(n / m))
    lo, hi = i * chunk, min((i + 1) * chunk, n)
    return cands[lo:hi], lo, hi


def normalize_member(df):
    """Sec.6 guards: date strict-monotonic + no duplicates (重行守卫) + no NaN
    in OHLCV; zero-volume bars are legitimate no-trade bars (kept, disclosed).
    Returns normalized frame (date str YYYY-MM-DD, numerics)."""
    if df is None or len(df) == 0:
        raise ValueError("empty member frame")
    d = pd.DataFrame({
        "date": pd.to_datetime(df["date"], errors="coerce"),
        "open": pd.to_numeric(df["open"], errors="coerce"),
        "high": pd.to_numeric(df["high"], errors="coerce"),
        "low": pd.to_numeric(df["low"], errors="coerce"),
        "close": pd.to_numeric(df["close"], errors="coerce"),
        "volume": pd.to_numeric(df["volume"], errors="coerce"),
    })
    if d["date"].isna().any():
        raise ValueError("NaN dates")
    if not d["date"].is_unique:
        raise ValueError("duplicate dates (重行守卫)")
    if not d["date"].is_monotonic_increasing:
        raise ValueError("non-monotonic dates")
    if d[["open", "high", "low", "close", "volume"]].isna().any().any():
        raise ValueError("NaN in OHLCV")
    d["date"] = d["date"].dt.strftime("%Y-%m-%d")
    return d


def csv_ok(path):
    return os.path.exists(path) and os.path.getsize(path) > CSV_MIN_BYTES


def load_registry(path=REGISTRY):
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    return {"no_face": [], "guard_rejects": []}


def pull_members(members, fetch=fetch_daily, probe_face=is_no_face,
                 data_dir=DATA_DIR, registry_path=REGISTRY, fuse_path=FUSE,
                 summary_path=None, limit=None, sleep=time.sleep,
                 sleep_s=SLEEP_S):
    """Core pull loop, dependency-injected for hermetic selftest. Returns
    (stats, exit_code). Fuse semantics (single code path for production and
    fixtures, r157 pairing law): active fuse (age < cooldown) -> honest no-op
    zero fetch exit 0; 3 consecutive non-404 member failures -> fuse file +
    exit 2."""
    os.makedirs(data_dir, exist_ok=True)
    if os.path.exists(fuse_path):
        try:
            age = time.time() - float(json.load(
                open(fuse_path, encoding="utf-8")).get("ts", 0))
        except Exception:                                   # noqa: BLE001
            age = FUSE_COOLDOWN_S + 1      # unreadable fuse = treat stale
        if age < FUSE_COOLDOWN_S:
            return {"members": len(members), "fused_noop": True,
                    "fuse_age_s": round(age), "ts": now_iso()}, 0
    reg = load_registry(registry_path)
    skip_nf = {x["code"] for x in reg["no_face"]}
    skip_rj = {x["code"] for x in reg["guard_rejects"]}
    st = {"members": len(members), "existing": 0, "pulled": 0,
          "no_face_new": 0, "reject_new": 0, "fails": [], "limited": False,
          "ts": now_iso()}
    fuse_counter = 0
    for r in members:
        code, name = r["code"], r["name"]
        csv_path = os.path.join(data_dir, code + ".csv")
        if csv_ok(csv_path):
            st["existing"] += 1
            continue
        if code in skip_nf or code in skip_rj:
            continue
        if limit is not None and st["pulled"] + st["no_face_new"] >= limit:
            st["limited"] = True
            break
        ok = noface = False
        last_err = verr = None
        for _attempt in range(RETRY):
            try:
                raw = fetch(code)
            except Exception as ex:                       # noqa: BLE001
                if probe_face(code):
                    noface = True
                    break
                last_err = "fetch: %s" % str(ex)[:120]
                sleep(sleep_s)
                continue
            try:
                d = normalize_member(raw)
            except Exception as ex:                       # noqa: BLE001
                verr = str(ex)[:120]   # deterministic source shape: no retry
                break
            tmp = csv_path + ".tmp"
            d.to_csv(tmp, index=False)
            os.replace(tmp, csv_path)
            ok = True
            break
        if ok:
            st["pulled"] += 1
            fuse_counter = 0
        elif noface:
            reg["no_face"].append({"code": code, "name": name, "ts": now_iso()})
            st["no_face_new"] += 1
            fuse_counter = 0
        elif verr:
            reg["guard_rejects"].append(
                {"code": code, "name": name, "reason": verr, "ts": now_iso()})
            st["reject_new"] += 1
            fuse_counter = 0
        else:
            st["fails"].append({"code": code, "name": name, "err": last_err})
            fuse_counter += 1
            if fuse_counter >= FUSE_N:
                _atomic_write_json(registry_path, reg)
                _atomic_write_json(fuse_path, {"ts": time.time(),
                                               "iso": now_iso(),
                                               "consecutive_fails": fuse_counter})
                st["fused"] = True
                return st, 2
        sleep(sleep_s)
    _atomic_write_json(registry_path, reg)
    st["no_face_total"] = len(reg["no_face"])
    st["reject_total"] = len(reg["guard_rejects"])
    if st["limited"]:
        return st, 0
    if summary_path is not None:
        st["resolved"] = not st["fails"]
        _atomic_write_json(summary_path, st)
    if st["fails"]:
        return st, 2
    if st["pulled"] and os.path.exists(fuse_path):
        try:
            os.remove(fuse_path)     # healed: successful pulls after stale fuse
        except OSError:
            pass
    return st, 0


def cmd_run(shard, of, limit=None):
    if not os.path.exists(MANIFEST):
        print("run FAIL: manifest absent -- build with `manifest` subcommand first")
        return 2
    man = json.load(open(MANIFEST, encoding="utf-8"))
    cands = man["candidates"]
    if of < 1 or not (0 <= shard < of):
        print("run FAIL: shard out of range", shard, of)
        return 2
    members, lo, hi = shard_slice(cands, shard, of)
    if not members:
        print("shard %d of %d empty (n=%d) -> honest no-op" % (shard, of, len(cands)))
        return 0
    summary_path = None if limit is not None else os.path.join(
        RES_DIR, "shard_%dof%d.json" % (shard, of))
    st, code = pull_members(members, summary_path=summary_path, limit=limit)
    st["shard"], st["of"], st["pos_lo"], st["pos_hi"] = shard, of, lo, hi
    if st.get("fused_noop"):
        print("conn-fuse active (age %ss < %ds cooldown) -> honest no-op, "
              "no request pressure" % (st.get("fuse_age_s"), FUSE_COOLDOWN_S))
    print(json.dumps(st, ensure_ascii=False))
    return code


def cmd_status():
    if not os.path.exists(MANIFEST):
        print("status: manifest absent")
        return 0
    man = json.load(open(MANIFEST, encoding="utf-8"))
    cands = man["candidates"]
    reg = load_registry()
    nf = {x["code"] for x in reg["no_face"]}
    rj = {x["code"] for x in reg["guard_rejects"]}
    have = sum(1 for r in cands if csv_ok(os.path.join(DATA_DIR, r["code"] + ".csv")))
    fused = ""
    if os.path.exists(FUSE):
        f = json.load(open(FUSE, encoding="utf-8"))
        fused = " | FUSED age=%.0fs" % (time.time() - float(f.get("ts", 0)))
    print("status: candidates=%d csv=%d no_face=%d guard_rejects=%d "
          "pending=%d%s" % (len(cands), have, len(nf), len(rj),
                            len(cands) - have - len(nf) - len(rj), fused))
    return 0


# ---- hermetic selftest (zero network) ----------------------------------------
def selftest():
    import tempfile
    ok = []

    def eq(name, a, b):
        ok.append((name, a == b, a, b))

    # S1 frozen filter rule (fixture spot incl. every exclusion face)
    eq("filter plain treasury", is_candidate("sh010107", "21国债07"), True)
    eq("filter special treasury excluded", is_candidate("sh0100801", "20特别国债01"), False)
    eq("filter 特国 excluded", is_candidate("sh0100770", "07特国01"), False)
    eq("filter convertible excluded", is_candidate("sh113001", "XX转债"), False)
    eq("filter local gov excluded", is_candidate("sh010101", "20北京债"), False)
    eq("filter other bond excluded", is_candidate("sh018001", "21国开10"), False)

    # S2 shard slice math: contiguous, union=all, disjoint
    cands = [{"code": "c%03d" % i, "name": "x"} for i in range(7)]
    slices = [shard_slice(cands, i, 3)[0] for i in range(3)]
    eq("slice sizes 3/3/1", [len(s) for s in slices], [3, 3, 1])
    eq("slice union=all", sorted(c["code"] for s in slices for c in s),
       sorted(c["code"] for c in cands))
    eq("slice bounds", (shard_slice(cands, 1, 3)[1], shard_slice(cands, 1, 3)[2]),
       (3, 6))

    def mkframe(dates, close=None, volume=None):
        n = len(dates)
        return pd.DataFrame({
            "date": dates,
            "open": [100.0] * n, "high": [101.0] * n, "low": [99.0] * n,
            "close": close if close is not None else [100.5] * n,
            "volume": volume if volume is not None else [10.0] * n})

    # S3 zero-volume bar shape: legitimate no-trade bars pass and are kept
    d = normalize_member(mkframe(["2024-01-02", "2024-01-03", "2024-01-04"],
                                 volume=[10.0, 0.0, 0.0]))
    eq("zero-volume shape passes", len(d), 3)
    eq("zero-volume rows kept", float(d["volume"].iloc[1]), 0.0)

    # S4 duplicate-date shape (重行守卫)
    try:
        normalize_member(mkframe(["2024-01-02", "2024-01-02"]))
        eq("dup-date rejected", False, True)
    except ValueError as ex:
        eq("dup-date rejected", "duplicate" in str(ex), True)

    # S5 non-monotonic dates
    try:
        normalize_member(mkframe(["2024-01-03", "2024-01-02"]))
        eq("non-monotonic rejected", False, True)
    except ValueError as ex:
        eq("non-monotonic rejected", "monotonic" in str(ex), True)

    # S6 NaN in OHLCV
    try:
        normalize_member(mkframe(["2024-01-02", "2024-01-03"], close=[100.0, None]))
        eq("NaN OHLCV rejected", False, True)
    except ValueError as ex:
        eq("NaN OHLCV rejected", "NaN" in str(ex), True)

    # S7 empty frame
    try:
        normalize_member(pd.DataFrame(columns=["date", "open", "high", "low",
                                               "close", "volume"]))
        eq("empty frame rejected", False, True)
    except ValueError:
        eq("empty frame rejected", True, True)

    tmp = tempfile.mkdtemp(prefix="bpanel_selftest_")

    def fresh_dir(tag):
        p = os.path.join(tmp, tag)
        os.makedirs(p, exist_ok=True)
        return {"data": p, "reg": os.path.join(p, "member_registry.json"),
                "fuse": os.path.join(p, "conn_fuse.json")}

    mem = lambda c: {"code": c, "name": "fixture"}

    # S8 happy path: 2 members pulled -> CSVs on disk, exit 0, summary written
    p = fresh_dir("s8")
    summ = os.path.join(p["data"], "shard_0of1.json")
    st, code = pull_members([mem("sh010107"), mem("sh010218")],
                            fetch=lambda c: mkframe(["2024-01-02", "2024-01-03"]),
                            probe_face=lambda c: False, data_dir=p["data"],
                            registry_path=p["reg"], fuse_path=p["fuse"],
                            summary_path=summ, sleep=lambda s: None)
    eq("happy exit 0", code, 0)
    eq("happy pulled=2", st["pulled"], 2)
    eq("happy csvs on disk",
       (csv_ok(os.path.join(p["data"], "sh010107.csv")),
        csv_ok(os.path.join(p["data"], "sh010218.csv"))), (True, True))
    eq("summary written", os.path.exists(summ), True)

    # S9 404 no-face shape: fetch raises, probe True -> registry, no CSV, no fail
    p = fresh_dir("s9")
    def raise404(c):
        raise KeyError("date")
    st, code = pull_members([mem("sh019999")], fetch=raise404,
                            probe_face=lambda c: True, data_dir=p["data"],
                            registry_path=p["reg"], fuse_path=p["fuse"],
                            summary_path=None, sleep=lambda s: None)
    eq("no-face exit 0 (resolved)", code, 0)
    eq("no-face registered", st["no_face_new"], 1)
    eq("no-face no csv", csv_ok(os.path.join(p["data"], "sh019999.csv")), False)
    eq("no-face no fail", st["fails"], [])

    # S10 404 resets consecutive-fail counter: F,F,NF,F,F -> no fuse, exit 2
    p = fresh_dir("s10")
    calls = []
    def flaky(c):
        calls.append(c)
        if c == "sh0003":
            raise KeyError("date")
        raise ConnectionError("transient")
    st, code = pull_members([mem("sh0001"), mem("sh0002"), mem("sh0003"),
                             mem("sh0004"), mem("sh0005")],
                            fetch=flaky, probe_face=lambda c: c == "sh0003",
                            data_dir=p["data"], registry_path=p["reg"],
                            fuse_path=p["fuse"], summary_path=None,
                            sleep=lambda s: None)
    eq("flaky no fuse", os.path.exists(p["fuse"]), False)
    eq("flaky exit 2 (4 fails: 2+reset+2)", (code, len(st["fails"])), (2, 4))
    eq("flaky fetch attempts = 4 fails x2 + 1 noface probe x1", len(calls), 9)

    # S11 fuse trip: 3 consecutive non-404 failures -> fuse file + exit 2
    p = fresh_dir("s11")
    st, code = pull_members([mem("sh0001"), mem("sh0002"), mem("sh0003"),
                             mem("sh0004")],
                            fetch=lambda c: (_ for _ in ()).throw(ConnectionError("blocked")),
                            probe_face=lambda c: False, data_dir=p["data"],
                            registry_path=p["reg"], fuse_path=p["fuse"],
                            summary_path=None, sleep=lambda s: None)
    eq("fuse exit 2", code, 2)
    eq("fuse file written", os.path.exists(p["fuse"]), True)
    eq("fuse stops before member 4 (registry only 3 fails)",
       len(st["fails"]), 3)

    # S12 cooldown no-op: fresh fuse -> zero fetch calls, exit 0
    p = fresh_dir("s12")
    _atomic_write_json(p["fuse"], {"ts": time.time(), "iso": now_iso()})
    called = []
    st, code = pull_members([mem("sh0001")], fetch=lambda c: called.append(c),
                            probe_face=lambda c: False, data_dir=p["data"],
                            registry_path=p["reg"], fuse_path=p["fuse"],
                            summary_path=None, sleep=lambda s: None)
    eq("cooldown no-op exit 0", code, 0)
    eq("cooldown no fetch pressure", called, [])
    eq("cooldown no summary noise", st["members"], 1)

    # S13 resume: existing CSV skipped without fetch; registry skips too
    p = fresh_dir("s13")
    d0 = normalize_member(mkframe(["2024-01-02"]))
    d0.to_csv(os.path.join(p["data"], "sh010107.csv"), index=False)
    _atomic_write_json(p["reg"], {"no_face": [{"code": "sh019999", "name": "x",
                                               "ts": now_iso()}],
                                  "guard_rejects": [{"code": "sh018888",
                                                     "name": "x",
                                                     "reason": "duplicate dates",
                                                     "ts": now_iso()}]})
    called = []
    pull_members([mem("sh010107"), mem("sh019999"), mem("sh018888")],
                  fetch=lambda c: called.append(c) or mkframe(["2024-01-01"]),
                  probe_face=lambda c: False, data_dir=p["data"],
                  registry_path=p["reg"], fuse_path=p["fuse"],
                  summary_path=None, sleep=lambda s: None)
    eq("resume existing+registry skip = zero fetch", called, [])

    # S14 limit smoke: pulls 1, marks limited, exit 0, no summary file
    p = fresh_dir("s14")
    summ = os.path.join(p["data"], "shard_0of1.json")
    st, code = pull_members([mem("sh0001"), mem("sh0002"), mem("sh0003")],
                            fetch=lambda c: mkframe(["2024-01-02"]),
                            probe_face=lambda c: False, data_dir=p["data"],
                            registry_path=p["reg"], fuse_path=p["fuse"],
                            summary_path=summ, limit=1, sleep=lambda s: None)
    eq("limit pulled=1", st["pulled"], 1)
    eq("limit marked", st["limited"], True)
    eq("limit exit 0", code, 0)
    eq("limit no summary file", os.path.exists(summ), False)

    # S15 CSV roundtrip: str volume coerced numeric, rows byte-faithful
    p = fresh_dir("s15")
    raw = pd.DataFrame({"date": ["2024-01-02", "2024-01-03"],
                        "open": ["100.0", "100.0"], "high": ["101.0", "101.0"],
                        "low": ["99.0", "99.0"], "close": ["100.5", "100.5"],
                        "volume": ["1000", "0"]})
    pull_members([mem("sh010303")], fetch=lambda c: raw, probe_face=lambda c: False,
                 data_dir=p["data"], registry_path=p["reg"], fuse_path=p["fuse"],
                 summary_path=None, sleep=lambda s: None)
    back = pd.read_csv(os.path.join(p["data"], "sh010303.csv"))
    eq("csv roundtrip rows", len(back), 2)
    eq("csv volume numeric", float(back["volume"].iloc[1]), 0.0)

    # S16 stale fuse heals on successful pull (fuse file removed)
    p = fresh_dir("s16")
    _atomic_write_json(p["fuse"], {"ts": time.time() - FUSE_COOLDOWN_S - 10,
                                   "iso": now_iso()})
    st, code = pull_members([mem("sh0001")], fetch=lambda c: mkframe(["2024-01-02"]),
                            probe_face=lambda c: False, data_dir=p["data"],
                            registry_path=p["reg"], fuse_path=p["fuse"],
                            summary_path=None, sleep=lambda s: None)
    eq("stale-fuse heal exit 0", code, 0)
    eq("stale-fuse healed (file removed)", os.path.exists(p["fuse"]), False)

    bad = [r for r in ok if not r[1]]
    for name, passed, a, b in ok:
        print(("PASS" if passed else "FAIL"), "|", name, "|", a, "vs", b)
    print("selftest: %d/%d PASS" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 2


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "manifest":
        sys.exit(cmd_manifest())
    if cmd == "run":
        args = sys.argv[2:]
        shard = of = None
        limit = None
        i = 0
        while i < len(args):
            if args[i] == "--shard":
                shard = int(args[i + 1]); i += 2
            elif args[i] == "--of":
                of = int(args[i + 1]); i += 2
            elif args[i] == "--limit":
                limit = int(args[i + 1]); i += 2
            else:
                i += 1
        if shard is None or of is None:
            print("run FAIL: --shard I --of M required")
            sys.exit(2)
        sys.exit(cmd_run(shard, of, limit))
    if cmd == "status":
        sys.exit(cmd_status())
    print("usage: bond_panel_puller.py manifest | run --shard I --of M [--limit K] "
          "| status | selftest")
    sys.exit(2)
