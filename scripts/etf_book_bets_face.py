"""Five tickers, five equal weights -- but how many independent bets is that?

The executable ticket (results/etf_book_order/ORDER-*.md) prints five holdings at
9.4% each and calls the sleeve a basket. Four of the five are crossborder, one is
domestic equity. Nothing in the repo says whether those five names move as five
things or as one and a half, so a reader who checks the diversification by counting
tickers is reading a number that was never measured.

This face measures it three ways on the same covariance and puts all three on one
line:

  * nominal_bets   = 1 / sum(w_i^2)          -- the counting-the-tickers answer
  * effective_bets = (sum lambda)^2 / sum lambda^2 on the correlation matrix
                                              -- how many uncorrelated directions
                                                 the sleeve really spans
  * risk_split     = 1 / sum(rc_i^2)         -- how evenly the VARIANCE is shared,
                                                 from the risk contributions

The last two are deliberately kept apart, because they answer different questions and
a single number would hide that: five copies of one series span ONE direction while
their variance is shared FIVE ways, perfectly evenly. `effective_bets` is the
independence count (it does not move when the weights move); `risk_split` is the
weight-dependent evenness of the risk. The headline verdict is driven by the
independence count only.

One counterfactual rides beside it: inverse-volatility weights on the SAME covariance,
which moves `risk_split` and cannot move `effective_bets` -- that is the arithmetic
proof that the two numbers measure different things.

Rules:
  * the holdings and their weights are READ from the published ticket, never re-typed
    (a second copy of the book is a second book -- E262);
  * an absent panel or a name with no bars on the window reads as None / no_data,
    never as 0 bets;
  * a ticket whose weights do not add up to its own book weight raises, it is not
    normalised silently into a plausible-looking basket;
  * price-only: cash and the cash leg are outside the sleeve and are disclosed but
    not counted as a bet, because a repo leg contributes carry, not covariance.

  python scripts/etf_book_bets_face.py run
  python scripts/etf_book_bets_face.py --selftest

Outputs results/etf_book_bets_face.json.
Exploratory: reads published faces and the daily panel, books nothing, changes no rule.
"""
import argparse
import csv
import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS                                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PATHS.results_dir, "etf_book_bets_face.json")
TICKET_GLOB = os.path.join(PATHS.results_dir, "etf_book_order", "TICKET-*.json")
TICKET_PTR = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")

WIN_LONG = 250        # one trading year: the window the headline is read on
WIN_SHORT = 60        # one quarter: disclosed beside it, never averaged into it
MIN_BARS = 60         # below this a correlation is not a measurement
CORR_FLAG = 0.85      # "these two are the same bet" line
WEIGHT_TOL = 0.005    # published weights are 6dp; 50bp of slack is rounding, not a book


# ---------------------------------------------------------------- pure helpers
def _finite(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def nominal_bets(w):
    """1 / sum(w^2): the count a reader gets by counting tickers."""
    ws = [_finite(x) for x in w]
    if not ws or any(v is None for v in ws):
        return None
    s = sum(v * v for v in ws)
    return 1.0 / s if s > 0 else None


def effective_bets(corr):
    """(sum lambda)^2 / sum lambda^2 -- participation ratio of a correlation matrix.

    Equal to 1 when every name is the same name, and to N when the names are
    mutually uncorrelated. Square of the Frobenius norm, so it never needs a
    sign convention on the eigenvectors.
    """
    n = len(corr)
    if n == 0:
        return None
    s1 = sum(corr[i][i] for i in range(n))          # trace == N
    s2 = 0.0
    for i in range(n):
        for j in range(n):
            s2 += corr[i][j] * corr[i][j]
    if s2 <= 0:
        return None
    return (s1 * s1) / s2


def risk_contrib(weights, cov):
    """Each name's share of the sleeve variance. Sums to 1 when the inputs are sane."""
    n = len(weights)
    if n == 0 or len(cov) != n:
        return None
    w = [_finite(x) for x in weights]
    if any(v is None for v in w):
        return None
    sw = [0.0] * n
    for i in range(n):
        acc = 0.0
        for j in range(n):
            acc += cov[i][j] * w[j]
        sw[i] = acc
    var = sum(w[i] * sw[i] for i in range(n))
    if var <= 0:
        return None
    return [(w[i] * sw[i]) / var for i in range(n)]


def risk_split_bets(rc):
    """1 / sum(rc^2) on the risk split: how many equivalent names share the variance.

    This is NOT an independence count. Five copies of one series share their variance
    five ways (reading 5 here) while spanning a single direction (reading 1 on
    effective_bets). Keeping both is the point.
    """
    if not rc:
        return None
    s = sum(v * v for v in rc)
    return 1.0 / s if s > 0 else None


def inverse_vol_weights(vols):
    """1/sigma weights. Deliberately the simple proxy, not a full ERC solve."""
    vs = [_finite(v) for v in vols]
    if not vs or any(v is None or v <= 0 for v in vs):
        return None
    inv = [1.0 / v for v in vs]
    s = sum(inv)
    return [x / s for x in inv] if s > 0 else None


def diversification_ratio(weights, vols, sleeve_vol):
    """(sum w_i sigma_i) / sigma_p. 1.0 means the sleeve is one name wearing five."""
    ws = [_finite(x) for x in weights]
    vs = [_finite(x) for x in vols]
    pv = _finite(sleeve_vol)
    if pv is None or pv <= 0 or not ws or len(ws) != len(vs):
        return None
    if any(v is None for v in vs):
        return None
    return sum(ws[i] * vs[i] for i in range(len(ws))) / pv


def corr_matrix(rets):
    """Pearson correlation on aligned return rows. Empty or degenerate -> None."""
    n = len(rets)
    if n == 0:
        return None
    T = len(rets[0])
    if T < 2 or any(len(r) != T for r in rets):
        return None
    mu = [sum(r) / T for r in rets]
    sd = []
    for i in range(n):
        var = sum((rets[i][t] - mu[i]) ** 2 for t in range(T)) / (T - 1)
        sd.append(math.sqrt(var) if var > 0 else 0.0)
    if any(s == 0 for s in sd):
        return None                    # a constant series has no correlation
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        out[i][i] = 1.0
        for j in range(i + 1, n):
            acc = 0.0
            for t in range(T):
                acc += (rets[i][t] - mu[i]) * (rets[j][t] - mu[j])
            c = acc / ((T - 1) * sd[i] * sd[j])
            c = max(-1.0, min(1.0, c))
            out[i][j] = c
            out[j][i] = c
    return out


def cov_matrix(rets):
    n = len(rets)
    if n == 0:
        return None
    T = len(rets[0])
    if T < 2:
        return None
    mu = [sum(r) / T for r in rets]
    cov = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            acc = 0.0
            for t in range(T):
                acc += (rets[i][t] - mu[i]) * (rets[j][t] - mu[j])
            cov[i][j] = acc / (T - 1)
            cov[j][i] = cov[i][j]
    return cov


def returns_from_closes(closes):
    out = []
    for k in range(1, len(closes)):
        a, b = closes[k - 1], closes[k]
        if a is None or b is None or a <= 0:
            out.append(None)
        else:
            out.append(b / a - 1.0)
    return out


def pair_stats(corr):
    """Max and median off-diagonal correlation, plus how many pairs sit above the flag."""
    n = len(corr)
    pairs = [corr[i][j] for i in range(n) for j in range(i + 1, n)]
    if not pairs:
        return {"max": None, "median": None, "n_pairs": 0, "n_above_flag": 0,
                "flag": CORR_FLAG}
    s = sorted(pairs)
    mid = len(s) // 2
    med = s[mid] if len(s) % 2 else 0.5 * (s[mid - 1] + s[mid])
    return {"max": max(s), "median": med, "n_pairs": len(s),
            "n_above_flag": sum(1 for p in pairs if abs(p) >= CORR_FLAG),
            "flag": CORR_FLAG}


def verdict_for(effective_bets_):
    """Driven by the independence count, never by the weight-dependent risk split."""
    if effective_bets_ is None:
        return "NOT_ASSESSED"
    if effective_bets_ < 1.5:
        return "ONE_BET_IN_FIVE_TICKERS"
    if effective_bets_ < 2.5:
        return "TWOISH_BETS"
    return "SPREAD"


def sentence_for(n_nominal, widest_w, eff, risk_split, widest_name, widest_share,
                 rp_split, med_corr):
    if eff is None or risk_split is None:
        return "the sleeve's covariance could not be measured, so how many bets it holds is unknown"
    head = ("%d tickers (widest %.1f%%) span %.1f independent directions, not %d"
            % (n_nominal, 100.0 * (widest_w or 0.0), eff, n_nominal))
    if med_corr is not None:
        head += " (median pairwise correlation %.2f)" % med_corr
    tail = ("; the variance is still split fairly evenly across %.1f equivalent names"
            % risk_split)
    if rp_split is not None:
        tail += " (%.1f under inverse-volatility weights)" % rp_split
    if widest_name:
        tail += ", and the widest single name %s carries %.0f%% of it" % (
            widest_name, 100.0 * widest_share)
    return head + tail


# ---------------------------------------------------------------- data access
def _daily_path(code):
    for pre in ("sh", "sz", "bj"):
        p = os.path.join(PATHS.daily_dir, pre + code + ".csv")
        if os.path.exists(p):
            return p
    return None


def load_closes(code, cutoff=None):
    """date -> close, oldest first. Missing file -> None (not an empty series)."""
    p = _daily_path(code)
    if not p:
        return None
    rows = []
    with open(p, "r", encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh):
            if len(row) < 5:
                continue
            d = row[0].strip()
            if not d or not d[0].isdigit():
                continue
            if cutoff and d > cutoff:
                continue
            c = _finite(row[4])
            if c is None or c <= 0:
                continue
            rows.append((d, c))
    rows.sort()
    return rows or None


def load_ticket(path=None):
    """Read the newest published executable ticket. Returns dict or None."""
    p = path
    if p is None:
        cands = sorted(glob.glob(TICKET_GLOB))
        cands = [c for c in cands if not c.endswith("-card.json")]
        p = cands[-1] if cands else (TICKET_PTR if os.path.exists(TICKET_PTR) else None)
    if not p or not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def holding_weights(ticket):
    """[(symbol, weight)] from the ticket's own order rows, or None.

    Weights must add up to the ticket's own book weight, otherwise the basket the
    reader is being shown is not the basket the ticket priced.
    """
    if not isinstance(ticket, dict):
        return None
    order = ticket.get("ticket", {}).get("order")
    if not order:
        return None
    pairs = []
    for row in order:
        sym = str(row.get("symbol", "")).strip()
        w = _finite(row.get("weight"))
        if not sym or w is None:
            return None
        pairs.append((sym, w))
    book_w = _finite(ticket.get("ticket", {}).get("book_weight"))
    if book_w is not None:
        if abs(sum(w for _s, w in pairs) - book_w) > WEIGHT_TOL:
            raise ValueError("ticket weights %.6f do not add up to its own book weight %.6f"
                             % (sum(w for _s, w in pairs), book_w))
    return pairs


def align_returns(symbols, cutoff, window):
    """Build return rows for every symbol on the SAME dates.

    Returns (rets, dates, missing) where missing lists symbols that had no usable
    series at all. Common-date intersection only: a name with a shorter history
    shortens the window for everyone, it never gets silently forward-filled.
    """
    series = {}
    missing = []
    for s in symbols:
        rows = load_closes(s, cutoff=cutoff)
        if not rows or len(rows) < 3:
            missing.append(s)
            continue
        series[s] = dict(rows)
    usable = [s for s in symbols if s in series]
    if len(usable) < 2:
        return None, None, missing
    common = None
    for s in usable:
        ds = set(series[s])
        common = ds if common is None else (common & ds)
    dates = sorted(common or [])
    if window and len(dates) > window + 1:
        dates = dates[-(window + 1):]       # N returns need N+1 closes
    if len(dates) < MIN_BARS + 1:
        return None, dates, missing
    rets = []
    for s in usable:
        closes = [series[s][d] for d in dates]
        r = returns_from_closes(closes)
        rr = [0.0 if x is None else x for x in r]     # hole only inside the window
        rets.append(rr)
    return rets, usable, missing


def analyse(pairs, cutoff, window):
    symbols = [s for s, _w in pairs]
    rets, usable, missing = align_returns(symbols, cutoff, window)
    if rets is None:
        return {"status": "no_data", "window_bars": 0, "symbols_missing": missing,
                "verdict": "NOT_ASSESSED",
                "sentence": "no common return window for %s, so the bet count is unknown"
                            % ", ".join(symbols)}
    idx = [symbols.index(s) for s in usable]
    w_all = [pairs[i][1] for i in idx]
    tot = sum(w_all)
    if tot <= 0:
        return {"status": "no_data", "window_bars": 0, "symbols_missing": missing,
                "verdict": "NOT_ASSESSED", "sentence": "the ticket weights sum to zero"}
    w = [x / tot for x in w_all]
    corr = corr_matrix(rets)
    cov = cov_matrix(rets)
    if corr is None or cov is None:
        return {"status": "no_data", "window_bars": len(rets[0]) if rets else 0,
                "symbols_missing": missing, "verdict": "NOT_ASSESSED",
                "sentence": "a held name has a constant price on this window, so its "
                            "correlation is undefined and the bet count is not measured"}
    T = len(rets[0])
    vols = [math.sqrt(cov[i][i] * 252.0) for i in range(len(usable))]
    sw = [0.0] * len(usable)
    for i in range(len(usable)):
        sw[i] = sum(cov[i][j] * w[j] for j in range(len(usable)))
    var = sum(w[i] * sw[i] for i in range(len(usable)))
    sleeve_vol = math.sqrt(var * 252.0) if var > 0 else None
    rc = risk_contrib(w, cov)
    eff = effective_bets(corr)
    nom = nominal_bets(w)
    split = risk_split_bets(rc)
    pairs_face = pair_stats(corr)
    rpw = inverse_vol_weights(vols)
    rp_split = None
    if rpw is not None:
        rp_score = risk_contrib(rpw, cov)
        rp_split = risk_split_bets(rp_score)
    widest = None
    widest_share = None
    if rc:
        k = max(range(len(rc)), key=lambda i: rc[i])
        widest, widest_share = usable[k], rc[k]
    return {
        "status": "ok",
        "window_bars": T,
        "window_mode": "long" if window == WIN_LONG else ("short" if window == WIN_SHORT else str(window)),
        "symbols": usable,
        "symbols_missing": missing,
        "weights_sleeve": w,
        "vol_ann": vols,
        "sleeve_vol_ann": sleeve_vol,
        "nominal_bets": nom,
        "effective_bets": eff,
        "risk_split": split,
        "risk_contrib": rc,
        "widest_name": widest,
        "widest_share": widest_share,
        "diversification_ratio": diversification_ratio(w, vols, sleeve_vol),
        "pairs": pairs_face,
        "inverse_vol_weights": rpw,
        "inverse_vol_risk_split": rp_split,
        "verdict": verdict_for(eff),
        "sentence": sentence_for(len(usable), max(w), eff, split, widest, widest_share or 0.0,
                                 rp_split, pairs_face.get("median")),
    }


# ---------------------------------------------------------------- reader face
def read_published(path=None):
    """The reader other faces may quote: never invents a verdict it cannot read."""
    p = path or OUT
    if not os.path.exists(p):
        return {"status": "absent", "verdict": None, "sentence": None,
                "note": "the bets face has not been published yet"}
    try:
        with open(p, "r", encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"status": "unreadable", "verdict": None, "sentence": None,
                "note": "could not parse %s: %s" % (p, exc)}
    long_face = d.get("long") or {}
    return {"status": d.get("status"),
            "verdict": long_face.get("verdict"),
            "sentence": long_face.get("sentence"),
            "effective_bets": long_face.get("effective_bets"),
            "risk_split": long_face.get("risk_split"),
            "nominal_bets": long_face.get("nominal_bets"),
            "evidence_cutoff": d.get("evidence_cutoff")}


# ---------------------------------------------------------------- run
def run():
    ticket = load_ticket()
    if ticket is None:
        payload = {"status": "no_ticket", "evidence_cutoff": None,
                   "sentence": "no executable ticket on disk, so there is no book to count"}
        _write(payload)
        print("no_ticket: %s" % payload["sentence"])
        return 0
    cutoff = ticket.get("evidence_cutoff")
    pairs = holding_weights(ticket)
    if not pairs:
        payload = {"status": "no_book", "evidence_cutoff": cutoff,
                   "sentence": "the ticket carries no priced holdings, so there is no basket"}
        _write(payload)
        print("no_book: %s" % payload["sentence"])
        return 0
    long_face = analyse(pairs, cutoff, WIN_LONG)
    short_face = analyse(pairs, cutoff, WIN_SHORT) if long_face.get("status") == "ok" else None
    payload = {
        "status": long_face.get("status"),
        "evidence_cutoff": cutoff,
        "ticket_decided_at": ticket.get("book_decided_at"),
        "sources": {"ticket": os.path.relpath(_ticket_path(), ROOT).replace("\\", "/"),
                    "panel": "data/daily/<sh|sz><code>.csv"},
        "book_weight": ticket.get("ticket", {}).get("book_weight"),
        "cash_weight": ticket.get("ticket", {}).get("cash_weight"),
        "cash_note": "the cash leg carries repo interest, not covariance, so it is not counted as a bet",
        "windows": {"long": WIN_LONG, "short": WIN_SHORT},
        "long": long_face,
        "short": short_face,
        "sentence": long_face.get("sentence"),
    }
    _write(payload)
    print(json.dumps({"status": payload["status"], "verdict": long_face.get("verdict"),
                      "effective_bets": long_face.get("effective_bets"),
                      "risk_split": long_face.get("risk_split"),
                      "nominal_bets": long_face.get("nominal_bets"),
                      "sentence": long_face.get("sentence")}, ensure_ascii=False, indent=1))
    return 0


def _ticket_path():
    cands = sorted(c for c in glob.glob(TICKET_GLOB) if not c.endswith("-card.json"))
    if cands:
        return cands[-1]
    return TICKET_PTR


def _write(payload):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, OUT)


# ---------------------------------------------------------------- selftest
def _selftest():
    import random
    ok = 0

    def chk(name, cond):
        nonlocal ok
        assert cond, "FAILED: %s" % name
        ok += 1

    # L1 identical names are one bet, by every reading
    same = [[0.01, -0.02, 0.03, 0.005, -0.011] * 4 for _ in range(5)]
    c = corr_matrix(same)
    chk("five copies of one series correlate at 1 and span 1 direction",
        c is not None and abs(c[0][1] - 1.0) < 1e-12 and abs(effective_bets(c) - 1.0) < 1e-9)
    cov = cov_matrix(same)
    w = [0.2] * 5
    rc = risk_contrib(w, cov)
    chk("five copies of one series share their variance five ways while spanning one direction",
        rc is not None and abs(sum(rc) - 1.0) < 1e-12
        and abs(risk_split_bets(rc) - 5.0) < 1e-9
        and abs(effective_bets(c) - 1.0) < 1e-9)
    chk("the two readings really are different questions (split != independence here)",
        abs(risk_split_bets(rc) - effective_bets(c)) > 1.0)

    # L2 mutually orthogonal series span N directions
    rnd = random.Random(20261030)
    T = 400
    rows = [[rnd.gauss(0, 1) for _ in range(T)] for _ in range(5)]
    rets_orth = []
    for i in range(5):
        r = rows[i][:]
        for j in range(i):                      # Gram-Schmidt: same column space, no overlap
            dot = sum(r[t] * rets_orth[j][t] for t in range(T))
            nrm = sum(rets_orth[j][t] ** 2 for t in range(T))
            r = [r[t] - (dot / nrm) * rets_orth[j][t] for t in range(T)]
        rets_orth.append(r)
    c2 = corr_matrix(rets_orth)
    e2 = effective_bets(c2)
    chk("five orthogonal series reach the nominal five bets",
        e2 is not None and e2 > 4.95)

    # L3/L4 equal volatility and equal correlation gives equal risk, whatever the sign
    n = 4
    corr_eq = [[1.0 if i == j else 0.4 for j in range(n)] for i in range(n)]
    cov_eq = [[corr_eq[i][j] * 0.02 * 0.02 for j in range(n)] for i in range(n)]
    rc_eq = risk_contrib([0.25] * 4, cov_eq)
    chk("equal weights on equal vol/corr split the risk into four equal quarters",
        rc_eq is not None and max(abs(x - 0.25) for x in rc_eq) < 1e-12)

    # L5 bounds: 1 <= effective bets <= N for any correlation matrix
    cov_r = cov_matrix(rets_orth)
    some_w = [0.5, 0.2, 0.15, 0.1, 0.05]
    rc_r = risk_contrib(some_w, cov_r)
    eb = effective_bets(c2)
    chk("effective bets stays between one and N", eb is not None and 1.0 - 1e-9 <= eb <= 5.0 + 1e-9)
    chk("risk contributions always sum to one for a positive-definite covariance",
        rc_r is not None and abs(sum(rc_r) - 1.0) < 1e-9)

    # L6 counting tickers is the nominal answer and nothing else
    chk("nominal bets on five equal weights is five", abs(nominal_bets([0.2] * 5) - 5.0) < 1e-12)
    chk("nominal bets on one name is one", abs(nominal_bets([1.0]) - 1.0) < 1e-12)

    # L7 absent inputs read as None, never as zero bets
    chk("an empty weight vector has no nominal count", nominal_bets([]) is None)
    chk("an empty correlation matrix has no effective count", effective_bets([]) is None)
    chk("an empty risk split has no bet count", risk_split_bets([]) is None)
    chk("a constant series has no correlation to measure", corr_matrix([[0.0] * 10, [0.0] * 10]) is None)

    # L8 inverse-vol weights on equal vols are equal weights
    iv = inverse_vol_weights([0.2, 0.2, 0.2, 0.2])
    chk("inverse-vol weights on equal volatilities are equal weights",
        iv is not None and max(abs(x - 0.25) for x in iv) < 1e-12)
    chk("inverse-vol weights refuse a zero volatility instead of inventing a weight",
        inverse_vol_weights([0.2, 0.0, 0.1]) is None)

    # L9 diversification ratio: identical names give 1, orthogonal names give more
    dr_same = diversification_ratio([0.25] * 4, [0.2] * 4, 0.2)
    chk("identical names diversify nothing (ratio 1.0)", dr_same is not None and abs(dr_same - 1.0) < 1e-12)
    dr_orth = diversification_ratio([0.25] * 4, [0.2] * 4, 0.1)
    chk("a sleeve quieter than its names has a ratio above one",
        dr_orth is not None and dr_orth > 1.5)

    # L10 a ticket that does not add up raises instead of being normalised
    bad = {"ticket": {"book_weight": 0.5,
                      "order": [{"symbol": "A", "weight": 0.4}, {"symbol": "B", "weight": 0.4}]}}
    raised = False
    try:
        holding_weights(bad)
    except ValueError:
        raised = True
    chk("a ticket whose weights do not add up to its book weight is refused", raised)
    good = {"ticket": {"book_weight": 0.47,
                       "order": [{"symbol": "A", "weight": 0.235}, {"symbol": "B", "weight": 0.235}]}}
    chk("a ticket that adds up is read as written",
        holding_weights(good) == [("A", 0.235), ("B", 0.235)])
    chk("a ticket with no order rows has no basket", holding_weights({"ticket": {}}) is None)

    # L11 verdict vocabulary, including the honest refusal
    chk("a single-risk book is named as one bet", verdict_for(1.2) == "ONE_BET_IN_FIVE_TICKERS")
    chk("two-ish is its own reading", verdict_for(2.0) == "TWOISH_BETS")
    chk("a spread book is a spread", verdict_for(3.4) == "SPREAD")
    chk("an unmeasured book is NOT_ASSESSED, never a passing grade", verdict_for(None) == "NOT_ASSESSED")

    # L12 the reader never invents a verdict from a missing artifact
    missing_reader = read_published(os.path.join(ROOT, "results", "_no_such_bets_face.json"))
    chk("an absent artifact reads absent with no verdict",
        missing_reader["status"] == "absent" and missing_reader["verdict"] is None)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "face.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"status": "ok", "evidence_cutoff": "2026-10-30",
                       "long": {"verdict": "TWOISH_BETS", "sentence": "quoted verbatim",
                                "effective_bets": 1.8, "risk_split": 2.1, "nominal_bets": 5.0}}, fh)
        rp = read_published(p)
        chk("the reader quotes the verdict and sentence verbatim from the artifact",
            rp["status"] == "ok" and rp["verdict"] == "TWOISH_BETS"
            and rp["sentence"] == "quoted verbatim" and rp["risk_split"] == 2.1
            and rp["effective_bets"] == 1.8)

    print("selftest %d/%d PASS" % (ok, ok))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest or a.cmd == "selftest":
        return _selftest()
    if a.cmd in ("run", ""):
        return run()
    ap.error("unknown command: %s" % a.cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv))