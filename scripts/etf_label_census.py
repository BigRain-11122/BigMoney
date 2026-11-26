"""The board's own labels, adjudicated by the board's own prices, over the WHOLE board.

r1803 taught the label test to the five legs of the book: a leg the hand map could not name is
retried on the label its own ticker writes, and the price history decides (median day-over-day
change of the gap <= 0.30 pp = one basket). Five legs cannot answer the two questions the desk
actually has:

    * is that line calibrated for the board, or only for those five? and
    * which of the other 1,600 tickers may a reader legitimately treat as the same thing?

So this face runs the same ruler over every label on the board, and publishes what it finds in
the order a reader needs it:

  1. how many of the board's labels are written on two or more live tickers;
  2. of the pairs under one label, how many does the price history agree are one basket;
  3. therefore which tickers form a GROUP of true substitutes -- and inside a group, what the
     dearest member costs its holder against the cheapest (CNY on a stated notional);
  4. which labels LIE (one name, prices say different baskets), so nobody swaps on the name.

Verdicts per label (frozen thresholds echoed into the payload; --check refuses a face that
disagrees with its own numbers):

  ONE_BASKET     every priced pair under the label is one basket
  MIXED          some pairs are one basket, some are not (the label spans a family)
  NOT_A_BASKET   no priced pair is one basket
  UNPRICED       not one pair could be priced (never read as "no alternative")

A pair that cannot be priced is UNKNOWN, never a basket, so a label can carry
n_priced < n_pairs; the reader sees which.

Group construction warns about its own weakest assumption. "A is B" and "B is C" do NOT imply
"A is C" (transitivity is an assumption, and 512040's label is exactly the case where a name
covers two different baskets). Components are therefore built by union-find and then TESTED for
being a clique: a component that is not a clique is published as CHAIN_NOT_CLIQUE with its
pairs, and no money is computed inside it.

Usage:
    python scripts/etf_label_census.py run
    python scripts/etf_label_census.py --check
    python scripts/etf_label_census.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_gap as gap  # noqa: E402  (the ruler and the board reader, one copy)
import etf_book_sibling_entry as sib  # noqa: E402  (the liquidity floor and the premium parser)

OUT_JSON = os.path.join(ROOT, "results", "etf_label_census.json")
OUT_MD = os.path.join(ROOT, "results", "etf_label_census.md")
SIB_GAP_JSON = os.path.join(ROOT, "results", "etf_book_sibling_gap.json")

LINE_PP = gap.LABEL_GAP_MEDIAN_PP    # the r1803 ruler, not a second line
MIN_DAYS = gap.MIN_DAYS
NOTIONAL_CNY = 100_000.0             # what one swap is sized on, so the money line is readable
MATERIAL_PP = sib.MATERIAL_PP        # a premium spread under half a point is not worth a trade
MERGE_TOL_PP = 5e-5                  # retained for callers that still import the old name
STORE_DP = 4                         # both faces publish medians at this many decimals


def same_reading(a, b):
    """Do two readings print the same number? Compared at the precision the faces STORE.

    r1935: the tolerance has to be the storage precision, never 1e-9 -- one more panel bar
    shifts these medians by ~1e-4 pp, which is the same size as the rounding of a stored
    4dp value. Comparing raw floats would call a correct face stale; comparing at 4dp says
    exactly what a reader can see.
    """
    if a is None or b is None:
        return False
    return round(a, STORE_DP) == round(b, STORE_DP)

CRITERIA = {
    "gap_median_pp": LINE_PP,
    "min_days": MIN_DAYS,
    "liq_floor_cny": sib.LIQ_FLOOR_CNY,
    "material_gap_pp": MATERIAL_PP,
    "notional_cny": NOTIONAL_CNY,
    "min_live_members": 2,
}


# ---------------------------------------------------------------- pair ruler (reused, not rewritten)

def pair_reading(code_a, code_b, cache):
    """One pair, one reading: the median day change of 100*ln(P_a/P_b).

    The level of the ratio carries the two NAV bases and is never read; only day changes are.
    A constant offset (the reconstruction r1803 pins with one session's premiums) cancels in
    every difference, so this median is the same number the sibling face publishes for the pair
    -- --check asserts that on the pairs the two faces share.
    """
    a = _closes(code_a, cache)
    b = _closes(code_b, cache)
    if a is None or b is None:
        return {"state": "NO_PANEL", "median_pp": None, "days": 0,
                "why": "no daily panel for %s" % (code_a if a is None else code_b)}
    dates, ca, cb = gap.common_series(a, b)
    if len(dates) < MIN_DAYS:
        return {"state": "SHORT_HISTORY", "median_pp": None, "days": len(dates),
                "why": "%d common days < %d" % (len(dates), MIN_DAYS)}
    med = gap.median_abs_change(gap.gap_series(ca, cb))
    if med is None:
        return {"state": "NO_HISTORY", "median_pp": None, "days": len(dates),
                "why": "the common series carries no change"}
    return {"state": pair_verdict(med), "median_pp": round(med, 4), "days": len(dates),
            "why": ""}


def _closes(code, cache):
    if code in cache:
        return cache[code]
    path = gap.find_daily(code)
    cache[code] = gap.load_close(path) if path else None
    return cache[code]


def pair_verdict(median_pp):
    """The boundary is inclusive on the basket side: a reading AT the line is not a refusal."""
    return "BASKET" if median_pp <= LINE_PP else "NOT_BASKET"


def label_class(readings):
    """ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED from the priced pairs only."""
    states = [r["state"] for r in readings]
    priced = [s for s in states if s in ("BASKET", "NOT_BASKET")]
    if not priced:
        return "UNPRICED"
    if all(s == "BASKET" for s in priced):
        return "ONE_BASKET"
    if all(s == "NOT_BASKET" for s in priced):
        return "NOT_A_BASKET"
    return "MIXED"


# ---------------------------------------------------------------- groups of true substitutes

def components(nodes, edges):
    """Union-find, but the result is a candidate, not a verdict (see clique check)."""
    parent = {n: n for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    out = {}
    for n in nodes:
        out.setdefault(find(n), []).append(n)
    return [sorted(v) for v in out.values()]


def is_clique(members, basket_pairs):
    want = {frozenset((members[i], members[j]))
            for i in range(len(members)) for j in range(i + 1, len(members))}
    return want <= basket_pairs


def group_money(members, premiums):
    """What the dearest member of a group costs its holder against the cheapest.

    Only members whose premium is observable take part -- a group where one premium is missing
    gets no money line rather than a guess.
    """
    seen = {c: premiums[c] for c in members if premiums.get(c) is not None}
    if len(seen) < 2:
        return None, "premium unobservable for at least two members"
    cheat = min(seen, key=lambda c: seen[c])
    dear = max(seen, key=lambda c: seen[c])
    spread_pp = round(seen[dear] - seen[cheat], 4)
    return {"cheapest": cheat, "cheapest_premium_pp": round(seen[cheat], 4),
            "dearest": dear, "dearest_premium_pp": round(seen[dear], 4),
            "spread_pp": spread_pp,
            "cost_cny": round(NOTIONAL_CNY * spread_pp / 100.0, 1),
            "material": spread_pp > MATERIAL_PP}, ""


# ---------------------------------------------------------------- face

def build():
    board, session = gap.board_labels()
    premiums = {c: sib.premium_dec(r.get("premium_pct")) for c, r in board.items()}
    premiums = {c: (None if p is None else p * 100.0) for c, p in premiums.items()}
    labels = {}
    for code, row in board.items():
        labels.setdefault(row.get("label"), []).append((code, row))

    cache, families, lying = {}, [], []
    n_labels_multi = n_pairs = n_priced = 0
    for label, members in sorted(labels.items(), key=lambda kv: -len(kv[1])):
        live = [c for c, r in members if (r.get("amount") or 0.0) >= sib.LIQ_FLOOR_CNY]
        if len(live) < 2:
            continue
        n_labels_multi += 1
        pairs = []
        for i in range(len(live)):
            for j in range(i + 1, len(live)):
                reading = pair_reading(live[i], live[j], cache)
                reading.update({"a": live[i], "b": live[j]})
                pairs.append(reading)
        n_pairs += len(pairs)
        n_priced += sum(1 for p in pairs if p["state"] in ("BASKET", "NOT_BASKET"))
        klass = label_class(pairs)
        n_priced_fam = sum(1 for p in pairs if p["state"] in ("BASKET", "NOT_BASKET"))
        fam = {"label": label, "n_tickers": len(members), "n_live": len(live),
               "live": sorted(live), "n_pairs": len(pairs),
               "n_priced": n_priced_fam,
               "class": klass,
               # a class read off a subset must not read like a class read off every pair
               "partial": n_priced_fam < len(pairs),
               "basket_pairs": sum(1 for p in pairs if p["state"] == "BASKET"),
               "not_basket_pairs": sum(1 for p in pairs if p["state"] == "NOT_BASKET"),
               "unpriced": [p for p in pairs if p["state"] not in ("BASKET", "NOT_BASKET")],
               "pairs": pairs}
        families.append(fam)
        if klass in ("NOT_A_BASKET", "MIXED"):
            lying.append({"label": label, "class": klass, "n_live": len(live),
                          "n_priced": fam["n_priced"],
                          "worst_pair": max((p["median_pp"] for p in pairs
                                             if p["median_pp"] is not None), default=None)})

    # groups: only pairs the price history accepted, and only cliques get money
    nodes = sorted({p["a"] for f in families for p in f["pairs"]} |
                   {p["b"] for f in families for p in f["pairs"]})
    basket_pairs = {frozenset((p["a"], p["b"])) for f in families for p in f["pairs"]
                    if p["state"] == "BASKET"}
    groups, chains = [], []
    for comp in components(nodes, basket_pairs):
        if len(comp) < 2:
            continue
        labels_of = sorted({next(f["label"] for f in families if c in f["live"]) for c in comp})
        row = {"members": comp, "n": len(comp), "labels": labels_of}
        if not is_clique(comp, basket_pairs):
            missing = [sorted(p) for p in
                       ({frozenset((comp[i], comp[j]))
                         for i in range(len(comp)) for j in range(i + 1, len(comp))}
                        - basket_pairs)]
            row.update({"state": "CHAIN_NOT_CLIQUE",
                        "why": "A~B and B~C is not A~C; not every pair inside was accepted",
                        "pairs_not_accepted": sorted(missing)})
            chains.append(row)
            continue
        money, why = group_money(comp, premiums)
        row.update({"state": "GROUP", "money": money, "why": why})
        groups.append(row)

    over = [g for g in groups if (g.get("money") or {}).get("material")]
    total = round(sum(g["money"]["cost_cny"] for g in over), 1)
    biggest = max(over, key=lambda g: g["money"]["cost_cny"], default=None)
    counts = {}
    for f in families:
        counts[f["class"]] = counts.get(f["class"], 0) + 1
    face = {
        "artifact": "etf_label_census",
        "session": session,
        "source_faces": {"board": "results/etf_book_sibling_entry.json (latest snapshot)",
                         "ruler": "scripts/etf_book_sibling_gap.py"},
        "criteria": CRITERIA,
        "board": {"n_rows": len(board), "n_labels": len(labels),
                  "n_labels_multi": n_labels_multi,
                  "n_pairs": n_pairs, "n_pairs_priced": n_priced},
        "label_class_counts": counts,
        "families": families,
        "lying_labels": sorted(lying, key=lambda r: -(r["worst_pair"] or 0.0)),
        "groups": groups,
        "chains": chains,
        "money": {"notional_cny": NOTIONAL_CNY, "groups_over_line": len(over),
                  "total_cost_cny": total,
                  "worst_group": (None if biggest is None else
                                  {"labels": biggest["labels"],
                                   "members": biggest["members"],
                                   "money": biggest["money"]})},
        "sentence": sentence(face_counts=(len(labels), n_labels_multi, len(groups)),
                             counts=counts, over=len(over), total=total),
        "caveats": [
            "one session of premiums and one price history per pair: the group says these "
            "tickers hold the same basket, it does not say the basket is worth its price",
            "the money line is the dearest-vs-cheapest premium INSIDE an accepted group on a "
            "%.0f CNY swap; it is the cost of an avoidable choice, not a return" % NOTIONAL_CNY,
            "a label with unpriced pairs carries n_priced < n_pairs; those pairs are unknown, "
            "never baskets",
            "the 0.30 pp line is the r1803 ruler; --check echoes it, so a refit is a new face "
            "and not a silent edit",
            "labels are the board's own residual names after the house prefix is stripped; two "
            "different words for one basket (alias families) are NOT merged here",
        ],
    }
    return face


def sentence(face_counts, counts, over, total):
    n_labels, n_multi, n_groups = face_counts
    if not n_multi:
        return "no label on this board is written on two live tickers"
    return ("%d of %d labels are written on two or more live tickers; the price history calls "
            "%d of those one basket, %d a family and %d none at all. %d groups of true "
            "substitutes survive the clique test and %d carry a premium spread over %.2f pp "
            "(%.0f CNY on a %.0f CNY swap)"
            % (n_multi, n_labels, counts.get("ONE_BASKET", 0), counts.get("MIXED", 0),
               counts.get("NOT_A_BASKET", 0), n_groups, over, MATERIAL_PP, total, NOTIONAL_CNY))


def render_md(face):
    L = ["# The board's own labels, adjudicated by its own prices", "",
         "Session: %s  |  ruler: median |day change| of the gap <= %.2f pp on >= %d common days"
         % (face.get("session") or "-", LINE_PP, MIN_DAYS), "",
         face["sentence"], "",
         "| reading | value |", "|---|---|",
         "| board rows / labels | %d / %d |" % (face["board"]["n_rows"],
                                                face["board"]["n_labels"]),
         "| labels on >= 2 live tickers | %d |" % face["board"]["n_labels_multi"],
         "| pairs / priced pairs | %d / %d |" % (face["board"]["n_pairs"],
                                                 face["board"]["n_pairs_priced"]),
         "| ONE_BASKET / MIXED / NOT_A_BASKET / UNPRICED | %d / %d / %d / %d |"
         % (face["label_class_counts"].get("ONE_BASKET", 0),
            face["label_class_counts"].get("MIXED", 0),
            face["label_class_counts"].get("NOT_A_BASKET", 0),
            face["label_class_counts"].get("UNPRICED", 0)),
         "| groups of true substitutes (clique) | %d |" % len(face["groups"]),
         "| groups over the %.2f pp line | %d |" % (MATERIAL_PP,
                                                    face["money"]["groups_over_line"]),
         "| their cost on a %.0f CNY swap | %.0f CNY |" % (NOTIONAL_CNY,
                                                            face["money"]["total_cost_cny"]),
         "| labels whose class rests on a subset of their pairs | %d |"
         % len([f for f in face["families"] if f.get("partial")]),
         ""]
    partial = [f for f in face["families"] if f.get("partial")]
    if partial:
        L.append("A class read off a subset is marked `*` below; the unpriced pairs are listed "
                 "in the JSON under each family's `unpriced` key (short history or no panel), "
                 "and a pair that could not be priced is never counted as a basket.")
        L.append("")
        L.append("Partial: %s" % ", ".join("%s (%d/%d priced)" % (f["label"], f["n_priced"],
                                                                  f["n_pairs"]) for f in partial))
        L.append("")
    L.append("## where the name and the price disagree")
    L.append("")
    if not face["lying_labels"]:
        L.append("No label on this board spans two different baskets.")
    else:
        L += ["| label | class | live | priced pairs | worst median pp |", "|---|---|---|---|---|"]
        for r in face["lying_labels"]:
            L.append("| %s | %s | %d | %d | %s |"
                     % (r["label"], r["class"], r["n_live"], r["n_priced"],
                        "-" if r["worst_pair"] is None else "%.3f" % r["worst_pair"]))
    L.append("")
    L.append("## the groups a reader may switch inside")
    L.append("")
    mat = [g for g in face["groups"] if (g.get("money") or {}).get("material")]
    thin = [g for g in face["groups"] if not (g.get("money") or {}).get("material")]
    if mat:
        L += ["| label(s) | members | cheapest | dearest | spread pp | cost CNY |",
              "|---|---|---|---|---|---|"]
        for g in sorted(mat, key=lambda g: -g["money"]["cost_cny"]):
            m = g["money"]
            L.append("| %s | %s | %s (%.2f%%) | %s (%.2f%%) | %.2f | %.0f |"
                     % (", ".join(g["labels"]), ", ".join(g["members"]), m["cheapest"],
                        m["cheapest_premium_pp"], m["dearest"], m["dearest_premium_pp"],
                        m["spread_pp"], m["cost_cny"]))
    else:
        L.append("No accepted group carries a premium spread over %.2f pp today." % MATERIAL_PP)
    if thin:
        L.append("")
        L.append("%d further groups are one basket but their premium spread is under the %.2f pp "
                 "materiality line (%s)." % (len(thin), MATERIAL_PP,
                                             ", ".join(g["labels"][0] for g in thin)))
    L.append("")
    if face["chains"]:
        L.append("## chains that are not cliques (no money priced inside them)")
        L.append("")
        for c in face["chains"]:
            L.append("- %s: %s -- %s" % (", ".join(c["labels"]), ", ".join(c["members"]),
                                          c["why"]))
        L.append("")
    L.append("## what this face does not say")
    L.append("")
    for c in face["caveats"]:
        L.append("- %s" % c)
    L.append("")
    return "\n".join(L)


def write_out(face):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))


def run():
    face = build()
    write_out(face)
    print(json.dumps({"artifact": face["artifact"], "session": face["session"],
                      "labels_multi": face["board"]["n_labels_multi"],
                      "pairs": face["board"]["n_pairs"],
                      "priced": face["board"]["n_pairs_priced"],
                      "classes": face["label_class_counts"],
                      "groups": len(face["groups"]), "chains": len(face["chains"]),
                      "groups_over_line": face["money"]["groups_over_line"],
                      "total_cost_cny": face["money"]["total_cost_cny"],
                      "lying": len(face["lying_labels"])}, ensure_ascii=False))
    return 0


def check():
    """Re-derive the published face from its own pair table and from the panels."""
    problems = []
    if not os.path.exists(OUT_JSON):
        print("check FAIL: no published face at %s" % OUT_JSON)
        return 2
    with open(OUT_JSON, encoding="utf-8") as fh:
        face = json.load(fh)
    crit = face.get("criteria") or {}
    if crit.get("gap_median_pp") != LINE_PP or crit.get("min_days") != MIN_DAYS:
        problems.append("the published criteria are not the frozen ruler (refit must be a new face)")
    if crit.get("notional_cny") != NOTIONAL_CNY:
        problems.append("the published notional moved; the money line is no longer comparable")

    cache, premiums = {}, {}
    for fam in face.get("families") or []:
        states = [p["state"] for p in fam["pairs"]]
        priced = [s for s in states if s in ("BASKET", "NOT_BASKET")]
        if label_class(fam["pairs"]) != fam["class"]:
            problems.append("%s: class %s does not re-derive" % (fam["label"], fam["class"]))
        if len(priced) != fam["n_priced"]:
            problems.append("%s: n_priced %d does not re-derive" % (fam["label"], fam["n_priced"]))
        if bool(fam.get("partial")) != (len(priced) < len(fam["pairs"])):
            problems.append("%s: the partial flag does not re-derive" % fam["label"])
        if len(fam["pairs"]) != fam["n_pairs"]:
            problems.append("%s: n_pairs %d does not re-derive" % (fam["label"], fam["n_pairs"]))
        for p in fam["pairs"]:
            if p["median_pp"] is None:
                continue
            if pair_verdict(p["median_pp"]) != p["state"]:
                problems.append("%s: pair %s/%s reads %s at %.4f pp"
                                % (fam["label"], p["a"], p["b"], p["state"], p["median_pp"]))
    # the arithmetic of the groups has to come back out of the published table
    nodes = sorted({p["a"] for f in face["families"] for p in f["pairs"]} |
                   {p["b"] for f in face["families"] for p in f["pairs"]})
    basket_pairs = {frozenset((p["a"], p["b"])) for f in face["families"] for p in f["pairs"]
                    if p["state"] == "BASKET"}
    published = {tuple(g["members"]): g for g in face.get("groups") or []}
    for comp in components(nodes, basket_pairs):
        if len(comp) < 2 or not is_clique(comp, basket_pairs):
            continue
        if tuple(comp) not in published:
            problems.append("group %s is missing from the published face" % (comp,))
    for key, g in published.items():
        if not is_clique(list(key), basket_pairs):
            problems.append("group %s is published as a clique but a pair inside it is not"
                            % (key,))
    over = sum((g.get("money") or {}).get("cost_cny") or 0.0
               for g in published.values() if (g.get("money") or {}).get("material"))
    if abs(round(over, 1) - (face["money"]["total_cost_cny"])) > 0.11:
        problems.append("total cost %.1f does not re-derive from the group rows (%.1f)"
                        % (face["money"]["total_cost_cny"], over))
    # the readings themselves, re-derived from the panels on disk -- not from the face
    # (r1935: a check that only re-reads its own published numbers can never say "I am old").
    # One ruler, one panel: when the two faces disagree, exactly one of them has not been
    # reburned since the panel moved. That is STALE -- the word that pays a writer -- and it
    # must not be published as a defect. Two different rulers would be a defect, and the
    # arithmetic below keeps the two cases apart instead of reporting whichever comes first.
    published_med = {}
    for fam in face["families"]:
        for p in fam["pairs"]:
            if p["median_pp"] is not None:
                published_med[frozenset((p["a"], p["b"]))] = p["median_pp"]
    cache_all, now_med = {}, {}
    for key in published_med:
        a, b = sorted(key)
        now_med[key] = pair_reading(a, b, cache_all)["median_pp"]
    stale_here, sibling_stale, shared, bad = [], [], 0, []
    for key, pub in published_med.items():
        now = now_med.get(key)
        if now is None or same_reading(now, pub):
            continue
        a, b = sorted(key)
        stale_here.append("%s/%s published %.4f, panel now %.4f" % (a, b, pub, now))
    # the ruler must agree with the face that taught it, on the pairs both priced
    if os.path.exists(SIB_GAP_JSON):
        with open(SIB_GAP_JSON, encoding="utf-8") as fh:
            sib_face = json.load(fh)
        for n in sib_face.get("label_family") or []:
            med = n.get("gap_median_pp")
            key = frozenset((str(n.get("leg_symbol")), str(n.get("sibling_symbol"))))
            if med is None or key not in published_med:
                continue
            shared += 1
            mine_pub, now = published_med[key], now_med.get(key)
            a, b = sorted(key)
            if now is not None and not same_reading(now, mine_pub):
                continue  # my own face is the stale side; already named in the STALE line
            if now is not None and not same_reading(now, med):
                sibling_stale.append("%s/%s sibling face %.4f, panel now %.4f"
                                     % (a, b, med, now))
            elif now is None and not same_reading(mine_pub, med):
                bad.append("%s/%s: census %.4f vs sibling face %.4f (panel now %s)"
                           % (a, b, mine_pub, med,
                              "unreadable" if now is None else "%.4f" % now))
    else:
        shared = 0
    if stale_here:
        problems.append("STALE the panel moved under %d priced pair(s) and this face was not "
                        "reburned since: %s" % (len(stale_here), "; ".join(stale_here[:4])))
    if sibling_stale:
        problems.append("STALE the sibling face %s is behind the same panel on %d shared "
                        "pair(s): %s" % (os.path.basename(SIB_GAP_JSON), len(sibling_stale),
                                         "; ".join(sibling_stale[:4])))
    if bad:
        problems.append("the two faces price the same pair differently: %s" % "; ".join(bad))
    print(json.dumps({"ok": not problems, "problems": problems,
                      "labels_multi": face["board"]["n_labels_multi"],
                      "groups": len(published), "shared_pairs_crosschecked": shared,
                      "pairs_rederived": len(now_med), "stale_pairs": len(stale_here),
                      "sibling_stale_pairs": len(sibling_stale)},
                     ensure_ascii=False))
    return 0 if not problems else 1


def selftest():
    fails, ran = [], []

    def eq(got, want, what):
        ran.append(what)
        if got != want:
            fails.append("%s: got %r want %r" % (what, got, want))

    # L1 the boundary is inclusive on the basket side
    eq(pair_verdict(LINE_PP), "BASKET", "L1 at the line")
    eq(pair_verdict(LINE_PP + 1e-9), "NOT_BASKET", "L1 above the line by a hair")
    eq(pair_verdict(0.145), "BASKET", "L1 the same-basket reading r1803 measured")

    # L2 label classes
    def rd(state):
        return {"state": state}

    eq(label_class([rd("BASKET"), rd("BASKET")]), "ONE_BASKET", "L2 all baskets")
    eq(label_class([rd("BASKET"), rd("NOT_BASKET")]), "MIXED", "L2 some baskets")
    eq(label_class([rd("NOT_BASKET"), rd("NOT_BASKET")]), "NOT_A_BASKET", "L2 none")
    eq(label_class([rd("NO_PANEL"), rd("BASKET")]), "ONE_BASKET",
       "L2 an unpriced pair does not decide the class")
    eq(label_class([rd("SHORT_HISTORY")]), "UNPRICED",
       "L2 nothing priced is not 'no basket'")

    # L3 union-find groups a chain but the clique test refuses to price it
    comps = components(["A", "B", "C"], [("A", "B"), ("B", "C")])
    eq(len(comps), 1, "L3 one component")
    eq(is_clique(comps[0], {frozenset(("A", "B")), frozenset(("B", "C"))}), False,
       "L3 A~B~C is not a clique (transitivity is an assumption)")
    eq(is_clique(["A", "B", "C"], {frozenset(("A", "B")), frozenset(("B", "C")),
                                   frozenset(("A", "C"))}), True, "L3 a full triangle is")
    eq(len(components(["A", "B", "C"], [("A", "B")])), 2, "L3 the loner stays out")

    # L4 the money line is dearest-vs-cheapest premium, on the stated notional
    money, why = group_money(["X", "Y", "Z"], {"X": 3.0, "Y": 1.0, "Z": 2.0})
    eq(money["cheapest"], "Y", "L4 cheapest by premium")
    eq(money["dearest"], "X", "L4 dearest by premium")
    eq(money["spread_pp"], 2.0, "L4 spread")
    eq(money["cost_cny"], 2000.0, "L4 %.0f CNY on a %.0f swap = 2%%" % (NOTIONAL_CNY, NOTIONAL_CNY))
    eq(money["material"], True, "L4 over the %.2f pp line" % MATERIAL_PP)
    money, why = group_money(["X", "Y"], {"X": 1.2, "Y": 1.0})
    eq(money["material"], False, "L4 under the materiality line is not money")
    money, why = group_money(["X", "Y", "Z"], {"X": 3.0, "Y": 1.0, "Z": None})
    eq((money["cheapest"], money["dearest"]), ("Y", "X"),
       "L4 an unobservable premium drops out instead of becoming zero")
    eq(group_money(["X"], {"X": 3.0})[0], None, "L4 one premium is not a spread")

    # L5 a face whose sentence and total disagree cannot pass (the published face's own tripwire)
    face = {"label_class_counts": {"ONE_BASKET": 1}, "groups": [], "chains": [],
            "money": {"groups_over_line": 0, "total_cost_cny": 0.0},
            "board": {"n_labels": 1, "n_labels_multi": 1, "n_pairs": 1,
                      "n_pairs_priced": 1, "n_rows": 2}, "families": [], "criteria": CRITERIA,
            "lying_labels": [], "session": "s", "caveats": [], "sentence": ""}
    face["sentence"] = sentence((1, 1, 0), {"ONE_BASKET": 1}, 0, 0.0)
    if "1 of 1 labels" not in face["sentence"]:
        fails.append("L5 the sentence must quote the counts it was given")

    # L18-L20 (r1911/r1934 lineage): the two faces must publish one number, and the two ways
    # they can differ have to be told apart -- a face the panel outran is STALE (the word that
    # pays a writer), two rulers that disagree is a defect no rebuild may erase.
    import contextlib
    import copy
    import io as _io
    import tempfile

    def _check_with(mine_doc, sib_doc):
        d = tempfile.mkdtemp(prefix="census_st")
        mp = os.path.join(d, "mine.json")
        sp = os.path.join(d, "sib.json")
        with open(mp, "w", encoding="utf-8") as fh:
            json.dump(mine_doc, fh)
        with open(sp, "w", encoding="utf-8") as fh:
            json.dump(sib_doc, fh)
        g = globals()
        old = (g["OUT_JSON"], g["SIB_GAP_JSON"])
        g["OUT_JSON"], g["SIB_GAP_JSON"] = mp, sp
        buf = _io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = check()
        finally:
            g["OUT_JSON"], g["SIB_GAP_JSON"] = old
        return rc, buf.getvalue()

    if not (os.path.exists(OUT_JSON) and os.path.exists(SIB_GAP_JSON)):
        fails.append("L18 both published faces must exist for the divergence legs")
        ran.extend(["L18", "L19", "L20"])
    else:
        with open(OUT_JSON, encoding="utf-8") as fh:
            mine_doc = json.load(fh)
        with open(SIB_GAP_JSON, encoding="utf-8") as fh:
            sib_doc = json.load(fh)

        rc0, out0 = _check_with(mine_doc, sib_doc)
        ran.append("L18 the untouched copies still read green (the guard does not redden the "
                   "ordinary case)")
        if rc0 != 0 or "STALE" in out0:
            fails.append("L18 control rc=%s out=%s" % (rc0, out0[:300]))

        mine_bad = copy.deepcopy(mine_doc)
        poisoned = None
        for fam in mine_bad["families"]:
            for p in fam["pairs"]:
                if p["median_pp"] is not None:
                    p["median_pp"] = round(p["median_pp"] + 1.0, 4)
                    poisoned = "%s/%s" % (p["a"], p["b"])
                    break
            if poisoned:
                break
        rc1, out1 = _check_with(mine_bad, sib_doc)
        ran.append("L19 a pair the panel no longer reproduces is reported STALE, never as a "
                   "defect between the faces")
        if poisoned is None:
            fails.append("L19 no priced pair to poison")
        elif rc1 == 0 or "STALE" not in out1 or "price the same pair differently" in out1:
            fails.append("L19 rc=%s out=%s" % (rc1, out1[:400]))

        published = {}
        for fam in mine_doc["families"]:
            for p in fam["pairs"]:
                if p["median_pp"] is not None:
                    published[frozenset((p["a"], p["b"]))] = p["median_pp"]
        sib_bad = copy.deepcopy(sib_doc)
        hit = None
        for n in sib_bad.get("label_family") or []:
            k = frozenset((str(n.get("leg_symbol")), str(n.get("sibling_symbol"))))
            if n.get("gap_median_pp") is not None and k in published:
                n["gap_median_pp"] = round(float(n["gap_median_pp"]) + 1.0, 4)
                hit = "%s/%s" % tuple(sorted(k))
                break
        rc2, out2 = _check_with(mine_doc, sib_bad)
        ran.append("L20 a sibling face behind the same panel is named STALE by name, not charged "
                   "to this face")
        if hit is None:
            fails.append("L20 the two faces share no priced pair, so this leg cannot run")
        elif rc2 == 0 or "STALE" not in out2 or "sibling face" not in out2:
            fails.append("L20 rc=%s out=%s" % (rc2, out2[:400]))

    for f in fails:
        print("FAIL " + f)
    print("selftest %d/%d %s" % (len(ran) - len(fails), len(ran),
                                 "PASS" if not fails else "FAIL"))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true", help="alias for the check subcommand")
    ap.add_argument("--selftest", action="store_true", help="alias for the selftest subcommand")
    a = ap.parse_args(argv)
    if a.check:
        return check()
    if a.selftest:
        return selftest()
    return {"run": run, "check": check, "selftest": selftest}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
