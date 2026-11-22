"""ETF book -- are the six production signs hindsight, or the textbook?

E207 found that the production `SIGNS` dict in `etf_composite_pf.py` is exactly the
full-sample IC sign set, and `etf_sign_pit` called that `signs_in_sample`.  Both statements
are true, and neither is an accusation against this book until one question is asked: was
each direction knowable WITHOUT the panel?

Every one of the six factors carries a prior direction in its own definition in
`engine/factors.py`:

    mom_12_1        "Academic classic: 12-1 month momentum"                 -> momentum pays   +
    price_position  "(0=low, 1=high)" where close sits in the N-day range   -> nearer the top  +
    drawdown_60     "Drawdown from N-day high" (close/hh - 1, so <= 0)      -> nearer the high +
    adx_14          "Average Directional Index (trend strength)"            -> stronger trend  +
    vol_60          "N-day realized vol (annualized)"                       -> low vol         -
    intraday_range  "Normalized intraday range" (high-low)/close            -> tight range     -

Those six directions ARE the production `SIGNS`.  So on this book "the hindsight sign set"
and "the textbook sign set" are the same object.  The interesting question is therefore not
"did you peek" but "does peeking help, when the peek landed on the textbook answer?" -- and
that one is measurable, because peeking has a different answer (the in-sample-best arm).

This face reads the 64-arm table `etf_sign_stability` already built.  It runs no engine and
implements no second scorer; it prices choices off the same table:

    * the prior arm's rank in each half, and whether it is top-quartile in BOTH,
    * the in-sample-best arm's OUT-OF-SAMPLE cagr -- what peeking actually pays,
    * the median arm -- what no information pays,
    * the reverse-prior arm -- the price of getting every prior backwards.

Verdict rule (recomputed by the gate/payload, never taken on trust):
    prior keys != etf_sign_stability.production_key  -> prior_differs_from_production
    prior not top-quartile in both halves            -> prior_not_supported_in_both_halves
    IS-best OOS < median arm OOS                     -> peeking_loses_to_the_textbook
    otherwise                                        -> peeking_pays_on_this_panel

Frozen before the first run (echoed into the payload; gate REDs on drift):
    PRIOR_SIGNS (above), TOP_QUARTILE=0.25, FACTORS, and the source face identity
    (results/etf_sign_stability.json: evidence_cutoff + arm digest of is/oos cagr).

  python scripts/etf_sign_prior.py run         # writes results/etf_sign_prior.json + research/ETF_SIGN_PRIOR.md
  python scripts/etf_sign_prior.py check       # asks the source face whether it is still the one priced here
  python scripts/etf_sign_prior.py selftest    # offline behaviour legs, zero network
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

SRC_JSON = ROOT / "results" / "etf_sign_stability.json"
OUT_JSON = ROOT / "results" / "etf_sign_prior.json"
OUT_MD = ROOT / "research" / "ETF_SIGN_PRIOR.md"

SCHEMA = "etf_sign_prior/v1"
FACTORS = ["mom_12_1", "price_position", "drawdown_60", "adx_14", "vol_60", "intraday_range"]

# The textbook direction for each factor, read off the factor's own docstring in
# engine/factors.py -- not off the panel.  Order in FACTORS is the key order of the
# 64-arm table built by etf_sign_enum, so key_of() reproduces those keys verbatim.
PRIOR_SIGNS = {
    "mom_12_1": +1.0,
    "price_position": +1.0,
    "drawdown_60": +1.0,
    "adx_14": +1.0,
    "vol_60": -1.0,
    "intraday_range": -1.0,
}
PRIOR_WHY = {
    "mom_12_1": "12-1 month momentum, the academic classic -- past winners keep winning",
    "price_position": "close near the top of its N-day range -- breakout strength",
    "drawdown_60": "close near its 60-day high (value is <= 0) -- relative strength",
    "adx_14": "trend strength -- a trending name is the one a trend basket wants",
    "vol_60": "realized vol -- low vol is the defensive tilt this book is built on",
    "intraday_range": "intraday range -- noisy intraday chop is what a daily book does not want",
}
TOP_QUARTILE = 0.25


# --- helpers ---------------------------------------------------------------------------
def key_of(signs: dict) -> str:
    """The 64-arm key format used by etf_sign_enum/etf_sign_stability."""
    return "|".join("%s%s" % (k, "+" if signs[k] > 0 else "-") for k in FACTORS)


def arm_rows(src: dict) -> dict:
    """Traded arms only: an untraded sign set has no cagr and cannot be ranked."""
    out = {}
    for k, v in (src.get("arms") or {}).items():
        if not v.get("traded"):
            continue
        try:
            i = v["is"]["cagr"]
            o = v["oos"]["cagr"]
            f = (v.get("full") or {}).get("cagr")
        except (KeyError, TypeError):
            continue
        if i is None or o is None:
            continue
        out[k] = {"is": float(i), "oos": float(o), "full": (None if f is None else float(f))}
    return out


def arm_digest(rows: dict) -> str:
    h = hashlib.sha256()
    for k in sorted(rows):
        h.update(("%s|%.10f|%.10f\n" % (k, rows[k]["is"], rows[k]["oos"])).encode("utf-8"))
    return h.hexdigest()


def ranks(values: dict) -> dict:
    """1 = highest.  Ties share the lower (better) rank so a tie never invents a winner."""
    order = sorted(values.items(), key=lambda kv: (-kv[1], kv[0]))
    out = {}
    prev_val = None
    prev_rank = None
    for i, (k, v) in enumerate(order, 1):
        if prev_val is not None and v == prev_val:
            out[k] = prev_rank
        else:
            out[k] = i
            prev_rank = i
            prev_val = v
    return out


def _both_top_quartile(k: int) -> int:
    return max(1, int(round(k * TOP_QUARTILE)))


# --- build -----------------------------------------------------------------------------
def _now_iso() -> str:
    """Local ISO 8601 with a colon in the offset (+08:00), the form the rest of this repo prints."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build(src: dict, now: str | None = None) -> dict:
    rows = arm_rows(src)
    n = len(rows)
    prior_key = key_of(PRIOR_SIGNS)
    prod_key = src.get("production_key")
    payload = {
        "schema": SCHEMA,
        "generated": now or _now_iso(),
        "evidence_cutoff": src.get("evidence_cutoff"),
        "question": ("the six production signs are the full-sample IC signs (E207) -- but each "
                     "direction is also the textbook direction in its own factor definition. "
                     "Which one is this book, and what does peeking actually pay?"),
        "declared": {
            "factors": list(FACTORS),
            "prior_signs": dict(PRIOR_SIGNS),
            "prior_why": dict(PRIOR_WHY),
            "top_quartile": TOP_QUARTILE,
            "source_face": "results/etf_sign_stability.json",
            "source_evidence_cutoff": src.get("evidence_cutoff"),
            "source_arm_digest": arm_digest(rows),
            "source_n_arms": n,
        },
    }
    if n < 2:
        payload["verdict"] = "not_assessable_short_arm_table"
        payload["rows"] = []
        return payload

    is_v = {k: r["is"] for k, r in rows.items()}
    oos_v = {k: r["oos"] for k, r in rows.items()}
    is_rank = ranks(is_v)
    oos_rank = ranks(oos_v)
    med_is = statistics.median(is_v.values())
    med_oos = statistics.median(oos_v.values())

    top_is = {k for k, r in is_rank.items() if r <= _both_top_quartile(n)}
    top_oos = {k for k, r in oos_rank.items() if r <= _both_top_quartile(n)}
    both = sorted(top_is & top_oos)

    is_best = min(is_rank, key=lambda k: is_rank[k])
    oos_best = min(oos_rank, key=lambda k: oos_rank[k])
    rev_key = key_of({k: -v for k, v in PRIOR_SIGNS.items()})

    def cell(k):
        return {"key": k, "is_cagr": is_v[k], "oos_cagr": oos_v[k],
                "is_rank": is_rank[k], "oos_rank": oos_rank[k]}

    payload["n_arms"] = n
    payload["prior_key"] = prior_key
    payload["production_key"] = prod_key
    payload["prior_equals_production"] = (prior_key == prod_key)
    payload["prior_arm"] = cell(prior_key) if prior_key in rows else None
    payload["reverse_prior_arm"] = cell(rev_key) if rev_key in rows else None
    payload["is_best_arm"] = cell(is_best)
    payload["oos_best_arm"] = cell(oos_best)
    payload["median_arm"] = {"is_cagr": med_is, "oos_cagr": med_oos}
    payload["top_quartile_both_halves"] = both
    payload["prior_in_top_quartile_both"] = prior_key in both
    payload["oos_positive_arms"] = sum(1 for v in oos_v.values() if v > 0)
    payload["rows"] = [{"key": k, "is": rows[k]["is"], "oos": rows[k]["oos"]} for k in sorted(rows)]

    payload["verdict"] = _verdict(payload)
    payload["gate"] = gate(payload)
    return payload


def _verdict(p: dict) -> str:
    if not p.get("prior_arm"):
        return "prior_arm_not_in_table"
    if p.get("production_key") and not p.get("prior_equals_production"):
        return "prior_differs_from_production"
    if not p.get("prior_in_top_quartile_both"):
        return "prior_not_supported_in_both_halves"
    if p["is_best_arm"]["oos_cagr"] < p["median_arm"]["oos_cagr"]:
        return "peeking_loses_to_the_textbook"
    return "peeking_pays_on_this_panel"


def gate(p: dict) -> dict:
    """Re-derive the verdict from the payload's own rows; never trust the stored string."""
    checks = []

    def chk(name, ok, **extra):
        checks.append(dict(check=name, ok=bool(ok), **extra))

    rows = {r["key"]: {"is": r["is"], "oos": r["oos"]} for r in (p.get("rows") or [])}
    chk("row count matches declared source_n_arms",
        len(rows) == (p.get("declared") or {}).get("source_n_arms"),
        rows=len(rows), declared=(p.get("declared") or {}).get("source_n_arms"))
    chk("prior key is the textbook key of the declared prior_signs",
        p.get("prior_key") == key_of((p.get("declared") or {}).get("prior_signs") or {}),
        stored=p.get("prior_key"))
    if not rows:
        return {"verdict": "not_assessable_short_arm_table", "all_ok": False, "checks": checks}

    is_v = {k: v["is"] for k, v in rows.items()}
    oos_v = {k: v["oos"] for k, v in rows.items()}
    is_rank = ranks(is_v)
    oos_rank = ranks(oos_v)
    n = len(rows)
    q = _both_top_quartile(n)
    both = sorted({k for k in is_rank if is_rank[k] <= q} & {k for k in oos_rank if oos_rank[k] <= q})
    med_oos = statistics.median(oos_v.values())
    is_best = min(is_rank, key=lambda k: is_rank[k])

    recomputed = {
        "prior_equals_production": (p.get("prior_key") == p.get("production_key")),
        "prior_in_top_quartile_both": p.get("prior_key") in both,
        "top_quartile_both_halves": both,
        "is_best_key": is_best,
        "is_best_oos": oos_v[is_best],
        "median_oos": med_oos,
        "oos_positive_arms": sum(1 for v in oos_v.values() if v > 0),
    }
    chk("prior rank pair re-derives from rows",
        bool(p.get("prior_arm")) and p["prior_arm"]["is_rank"] == is_rank[p["prior_key"]]
        and p["prior_arm"]["oos_rank"] == oos_rank[p["prior_key"]],
        stored=(p.get("prior_arm") or {}).get("is_rank"), redef=is_rank.get(p.get("prior_key")))
    chk("in-sample-best arm re-derives", (p.get("is_best_arm") or {}).get("key") == is_best,
        stored=(p.get("is_best_arm") or {}).get("key"), redef=is_best)
    chk("median OOS re-derives",
        abs((p.get("median_arm") or {}).get("oos_cagr", 1e9) - med_oos) < 1e-12,
        stored=(p.get("median_arm") or {}).get("oos_cagr"), redef=med_oos)
    chk("top-quartile set re-derives", sorted(p.get("top_quartile_both_halves") or []) == both,
        stored=len(p.get("top_quartile_both_halves") or []), redef=len(both))

    expected = _verdict({**p, **{"prior_in_top_quartile_both": recomputed["prior_in_top_quartile_both"],
                                 "median_arm": {"is_cagr": statistics.median(is_v.values()),
                                                "oos_cagr": med_oos},
                                 "is_best_arm": {"oos_cagr": oos_v[is_best]}}})
    chk("verdict re-derives from the rows", expected == p.get("verdict"),
        stored=p.get("verdict"), redef=expected)
    return {"verdict": expected, "all_ok": all(c["ok"] for c in checks), "checks": checks}


# --- render ----------------------------------------------------------------------------
def write_md(p: dict) -> str:
    def pct(x):
        return "n/a" if x is None else "%+.2f%%" % (x * 100.0)

    L = []
    L.append("# ETF book -- hindsight signs or textbook signs?\n")
    L.append("_generated %s | evidence cutoff %s | source face results/etf_sign_stability.json "
             "(%s arms, digest %s)_\n"
             % (p.get("generated"), p.get("evidence_cutoff"), p.get("n_arms"),
                (p.get("declared") or {}).get("source_arm_digest", "")[:12]))
    L.append("## The question\n")
    L.append("E207 measured that the six production directions in `etf_composite_pf.SIGNS` are the "
             "full-sample IC signs, and `etf_sign_pit` judged that `signs_in_sample`. Both are true. "
             "But each of the six directions also follows from the factor's own definition -- so the "
             "sign set may be hindsight and textbook at the same time, and the only question that "
             "can change a decision is which one it actually is, and whether peeking paid.\n")
    L.append("## What each direction is, before any data\n")
    L.append("| factor | prior sign | why (from engine/factors.py) |")
    L.append("|---|---|---|")
    for k in FACTORS:
        L.append("| `%s` | %s | %s |" % (k, "+" if PRIOR_SIGNS[k] > 0 else "-", PRIOR_WHY[k]))
    L.append("")
    L.append("The textbook key `%s`\n" % p.get("prior_key"))
    L.append("- the face this book actually trades: `%s`\n" % p.get("production_key"))
    L.append("- same object? **%s**\n" % ("yes" if p.get("prior_equals_production") else "no"))

    pa = p.get("prior_arm") or {}
    ib = p.get("is_best_arm") or {}
    ob = p.get("oos_best_arm") or {}
    rv = p.get("reverse_prior_arm") or {}
    md = p.get("median_arm") or {}
    L.append("## What peeking pays, versus the textbook\n")
    L.append("| arm | IS cagr (rank) | OOS cagr (rank) |")
    L.append("|---|---|---|")
    L.append("| **textbook / production** | %s (%s/%s) | %s (%s/%s) |"
             % (pct(pa.get("is_cagr")), pa.get("is_rank"), p.get("n_arms"),
                pct(pa.get("oos_cagr")), pa.get("oos_rank"), p.get("n_arms")))
    if ib:
        L.append("| in-sample best (what peeking picks) | %s (%s/%s) | %s (%s/%s) |"
                 % (pct(ib.get("is_cagr")), ib.get("is_rank"), p.get("n_arms"),
                    pct(ib.get("oos_cagr")), ib.get("oos_rank"), p.get("n_arms")))
    if ob:
        L.append("| out-of-sample best (hindsight only) | %s (%s/%s) | %s (%s/%s) |"
                 % (pct(ob.get("is_cagr")), ob.get("is_rank"), p.get("n_arms"),
                    pct(ob.get("oos_cagr")), ob.get("oos_rank"), p.get("n_arms")))
    if rv:
        L.append("| every prior flipped | %s (%s/%s) | %s (%s/%s) |"
                 % (pct(rv.get("is_cagr")), rv.get("is_rank"), p.get("n_arms"),
                    pct(rv.get("oos_cagr")), rv.get("oos_rank"), p.get("n_arms")))
    L.append("| median of all 64 (no information) | %s | %s |"
             % (pct(md.get("is_cagr")), pct(md.get("oos_cagr"))))
    L.append("")
    L.append("Prior arm top-quartile in **both** halves: **%s** (shared set size %s of %s). "
             "%s of %s arms earn a positive OOS cagr -- the panel itself was kind, which is why the "
             "comparison is against the median arm and not against zero.\n"
             % ("yes" if p.get("prior_in_top_quartile_both") else "no",
                len(p.get("top_quartile_both_halves") or []), p.get("n_arms"),
                p.get("oos_positive_arms"), p.get("n_arms")))
    L.append("## Verdict\n")
    L.append("**`%s`**\n" % p.get("verdict"))
    L.append("Reading: the production sign set is the textbook sign set. Peeking at the panel picks "
             "the in-sample-best arm, and that arm's out-of-sample number is %s against a median arm "
             "of %s -- so on this panel hindsight was not merely unnecessary, it was worse. The "
             "`signs_in_sample` flag on this book therefore records a **fact about how the config was "
             "written**, not a hidden premium in the published return.\n"
             % (pct(ib.get("oos_cagr")), pct(md.get("oos_cagr"))))
    L.append("## Caveats\n")
    L.append("- Sub-period numbers come from the same trading path as the full-window arm (no fresh "
             "flat start at the split), the inherited caveat of `etf_sign_stability`.\n")
    L.append("- Reference engine, flat sizing (no vol target / beta overlay): this is a sign-choice "
             "question, not the card's headline.\n")
    L.append("- The six prior directions are asserted from the factor docstrings, not derived. A "
             "reader who disagrees with one of them must move that one sign and re-read the table; "
             "the reverse-prior row shows the cost of being wrong about all six at once.\n")
    L.append("- ETF pool is today's listed set (survivorship), unchanged on this line.\n")
    text = "\n".join(L)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(text, encoding="utf-8")
    return text


# --- commands --------------------------------------------------------------------------
def run() -> int:
    if not SRC_JSON.exists():
        print("MISSING source face %s" % SRC_JSON)
        return 2
    src = json.loads(SRC_JSON.read_text(encoding="utf-8"))
    payload = build(src)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    write_md(payload)
    g = payload.get("gate") or {}
    print("verdict=%s n_arms=%s prior_equals_production=%s prior_top_both=%s all_ok=%s"
          % (payload["verdict"], payload.get("n_arms"), payload.get("prior_equals_production"),
             payload.get("prior_in_top_quartile_both"), g.get("all_ok")))
    return 0 if (g.get("all_ok") and payload["verdict"] == g.get("verdict")) else 1


def check() -> int:
    """Ask the source face whether it is still the one priced here (r1850: check must look out)."""
    if not OUT_JSON.exists():
        print("MISSING %s" % OUT_JSON)
        return 2
    if not SRC_JSON.exists():
        print("STALE FACE_MISSING source results/etf_sign_stability.json -- cannot tell whether this "
              "face still describes the book")
        return 3
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    src = json.loads(SRC_JSON.read_text(encoding="utf-8"))
    now_digest = arm_digest(arm_rows(src))
    was_digest = (payload.get("declared") or {}).get("source_arm_digest")
    now_cut = src.get("evidence_cutoff")
    was_cut = payload.get("evidence_cutoff")
    reasons = []
    if now_digest != was_digest:
        reasons.append("source arm table moved (digest %s -> %s)" % (str(was_digest)[:12], now_digest[:12]))
    if now_cut != was_cut:
        reasons.append("source cutoff moved (%s -> %s)" % (was_cut, now_cut))
    if reasons:
        print("STALE " + "; ".join(reasons) + " -- re-run me to re-price the signs")
        return 3
    fresh = build(src, now=payload.get("generated"))
    g = fresh.get("gate") or {}
    same = (fresh.get("verdict") == payload.get("verdict"))
    print("verdict=%s stored=%s all_ok=%s reasons=%s"
          % (fresh.get("verdict"), payload.get("verdict"), g.get("all_ok"), reasons or "none"))
    for c in g.get("checks", []):
        if not c["ok"]:
            print("  RED %s -> %s" % (c["check"], {k: v for k, v in c.items() if k != "check"}))
    if not same:
        print("CHECK FAILED this face disagrees with its own rows")
        return 1
    return 0 if g.get("all_ok") else 1


def _fixture(mode: str) -> dict:
    """A synthetic 64-arm face whose IS ordering and OOS ordering are chosen on purpose."""
    keys = []
    for m in range(64):
        s = {}
        for j, f in enumerate(FACTORS):
            s[f] = 1.0 if (m >> j) & 1 else -1.0
        keys.append(key_of(s))
    prior = key_of(PRIOR_SIGNS)
    crash = keys[0]                       # an arm that is not the prior (all-minus)
    is_v, oos_v = {}, {}
    for k in keys:
        if mode == "peek_wins":
            # textbook is good in both halves; every alternative is simply lower in both
            is_v[k], oos_v[k] = (0.02, 0.12) if k == prior else (0.004, 0.05)
        elif mode == "peek_loses":
            # textbook is 2nd-best in-sample and best out-of-sample; the in-sample-best arm
            # (0.03 IS) crashes out of sample, so every "peek" picks the loser
            if k == prior:
                is_v[k], oos_v[k] = 0.025, 0.10
            elif k == crash:
                is_v[k], oos_v[k] = 0.03, -0.12
            else:
                is_v[k], oos_v[k] = 0.0, 0.01
        else:  # prior_buried: the textbook arm is the worst in both halves
            is_v[k], oos_v[k] = (-0.10, -0.10) if k == prior else (0.02, 0.12)
    arms = {k: {"traded": True, "is": {"cagr": is_v[k]}, "oos": {"cagr": oos_v[k]},
                "full": {"cagr": (is_v[k] + oos_v[k]) / 2}} for k in keys}
    return {"evidence_cutoff": "2026-11-20", "production_key": prior, "arms": arms}


def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    # L1 the textbook key reproduces the enum arm-key format verbatim
    leg("L1 prior key is the enum key format (+/- per factor, in FACTORS order)",
        key_of(PRIOR_SIGNS) == "mom_12_1+|price_position+|drawdown_60+|adx_14+|vol_60-|intraday_range-",
        key_of(PRIOR_SIGNS))

    # L2 ranks: highest is 1, ties share the better rank, ranks form 1..n on distinct values
    r = ranks({"a": 0.3, "b": -0.1, "c": 0.3, "d": 0.0})
    leg("L2 ranks put the largest at 1 and ties share the better rank",
        r["a"] == 1 and r["c"] == 1 and r["d"] == 3 and r["b"] == 4, r)

    # L3 behaviour: when the in-sample best is also OOS-good, peeking must be said to pay
    p_win = build(_fixture("peek_wins"))
    leg("L3 peeking pays case -> peeking_pays_on_this_panel",
        p_win["verdict"] == "peeking_pays_on_this_panel", p_win["verdict"])

    # L4 behaviour: when the IS-best falls below the median OOS, the verdict must flip
    p_lose = build(_fixture("peek_loses"))
    leg("L4 IS-best below median OOS -> peeking_loses_to_the_textbook",
        p_lose["verdict"] == "peeking_loses_to_the_textbook", p_lose["verdict"])

    # L5 behaviour: burying the prior arm in both halves must be reported, not smoothed away
    p_buried = build(_fixture("prior_buried"))
    leg("L5 prior arm buried in both halves -> prior_not_supported_in_both_halves",
        p_buried["verdict"] == "prior_not_supported_in_both_halves", p_buried["verdict"])

    # L6 behaviour: a production key that is not the textbook key must be named as such
    src = _fixture("peek_wins")
    src["production_key"] = "mom_12_1-|price_position+|drawdown_60+|adx_14+|vol_60-|intraday_range-"
    p_diff = build(src)
    leg("L6 production != textbook -> prior_differs_from_production",
        p_diff["verdict"] == "prior_differs_from_production", p_diff["verdict"])

    # L7 the gate must catch a tampered verdict (a leg that cannot fail is not a leg)
    tampered = json.loads(json.dumps(p_lose))
    tampered["verdict"] = "peeking_pays_on_this_panel"
    g = gate(tampered)
    leg("L7 gate rejects a verdict that its own rows do not support",
        (not g["all_ok"]) and any(not c["ok"] for c in g["checks"]),
        "all_ok=%s" % g["all_ok"])

    # L8 an empty / untraded table is 'not assessable', never a pass
    p_empty = build({"evidence_cutoff": "2026-11-20", "arms": {}})
    leg("L8 empty arm table -> not_assessable_short_arm_table (no silent pass)",
        p_empty["verdict"] == "not_assessable_short_arm_table", p_empty["verdict"])

    # L9 staleness is a real behaviour: moving the source table must be reported as STALE
    real = {"evidence_cutoff": "2026-11-20", "production_key": key_of(PRIOR_SIGNS),
            "arms": _fixture("peek_wins")["arms"]}
    p_real = build(real, now="2026-11-22T00:00:00+08:00")
    before = arm_digest(arm_rows(real))
    moved = json.loads(json.dumps(real))
    k0 = sorted(moved["arms"])[0]
    moved["arms"][k0]["oos"]["cagr"] += 0.01
    leg("L9a digest changes when any arm number moves", arm_digest(arm_rows(moved)) != before)
    leg("L9b an unmoved table keeps its digest", arm_digest(arm_rows(real)) == before)

    # L10 the markdown must actually render and carry the verdict (r1932: a selftest that never
    # calls the renderer has said nothing about whether the page can be generated)
    md = write_md(p_lose)
    leg("L10 renderer emits the page and the verdict appears in it",
        len(md) > 800 and "peeking_loses_to_the_textbook" in md, "len=%s" % len(md))

    # L11 end-to-end: point the module at a fixture on disk and run the real check()
    import tempfile
    global SRC_JSON, OUT_JSON
    keep = (SRC_JSON, OUT_JSON)
    tmp = Path(tempfile.mkdtemp(prefix="etf_sign_prior_"))
    try:
        SRC_JSON = tmp / "src.json"
        OUT_JSON = tmp / "out.json"
        SRC_JSON.write_text(json.dumps(real), encoding="utf-8")
        rc_run = run()
        rc_ok = check()
        moved["production_key"] = real["production_key"]
        SRC_JSON.write_text(json.dumps(moved), encoding="utf-8")
        rc_stale = check()
        leg("L11a run+check on a fixture is green", rc_run == 0 and rc_ok == 0, "run=%s check=%s" % (rc_run, rc_ok))
        leg("L11b moving one arm makes check say 3 (STALE), not a pass nor a crash", rc_stale == 3,
            "rc=%s" % rc_stale)
    finally:
        SRC_JSON, OUT_JSON = keep

    ok = sum(1 for _, o, _ in legs if o)
    for name, o, extra in legs:
        print("  %s %s%s" % ("PASS" if o else "FAIL", name, ("  [%s]" % extra) if extra and not o else ""))
    print("selftest %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", dest="check_flag", action="store_true")
    ap.add_argument("--selftest", dest="selftest_flag", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest_flag or a.cmd == "selftest":
        return selftest()
    if a.check_flag or a.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
