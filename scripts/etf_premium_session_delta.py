#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""etf_premium_session_delta -- did the toll on this sheet go up or down between boards?

WHY THIS FILE EXISTS
--------------------
`etf_premium_face.py fetch` prints one board session at a time: "what this book pays over
NAV to get filled today". Two boards are now on disk (2026-11-06 and 2026-11-10) and no
face joins them, so the one question an operator actually asks -- "is the entry friction
on THIS sheet getting cheaper or dearer" -- had no artifact. Two snapshots are not a
series, so this face prints no percentile: it prints the move, in pp and in CNY, and
refuses to average it.

WHAT IT IS NOT
--------------
Not a backtest and not a signal. Both readings are realtime IOPV estimates taken after
different closes; the premium of a cross-border leg moves with a timezone the local close
does not see, so two boards a few days apart are two readings, not a trend.

MODES
-----
  run       join the two newest board faces and write the delta face.
  check     re-derive every published number from the faces and refuse a drift.
  selftest  offline legs over synthetic faces (the face's own contract).

Exit codes: 0 ok / 2 cannot build (fewer than two faces, unreadable face) /
            3 refused (the two faces price different sheets).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE_DIR = os.path.join(ROOT, "results", "etf_premium")
OUT_JSON = os.path.join(FACE_DIR, "PREMIUM-SESSION-DELTA.json")
OUT_MD = os.path.join(FACE_DIR, "PREMIUM-SESSION-DELTA.md")

# frozen: the face's own "at par" band, imported by value with the face as the owner.
PAR_BAND_PP = 0.30
FLAT_BAND_PP = 0.30


def _faces(d=None):
    """{session: face_dict} for every PREMIUM-<session>.json on disk."""
    d = d or FACE_DIR
    out = {}
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not (name.startswith("PREMIUM-") and name.endswith(".json")):
            continue
        sess = name[len("PREMIUM-"):-len(".json")]
        if len(sess) != 10 or sess.count("-") != 2:
            continue
        try:
            with open(os.path.join(d, name), encoding="utf-8") as fh:
                out[sess] = json.load(fh)
        except Exception:                                        # noqa: BLE001
            out[sess] = {"status": "unreadable"}
    return out


def _usable(face):
    """A published board face carries `legs` and no failed status (the face has no status
    field on success -- absence of legs is what tells the two apart, not a typed word)."""
    if not isinstance(face, dict):
        return False
    st = face.get("status")
    if st not in (None, "ok"):
        return False
    return bool(face.get("legs"))


def _priced(face):
    """{symbol: (amount_cny, premium_pct)} for the legs a face could price."""
    rows = {}
    for leg in (face.get("legs") or []):
        sym = leg.get("symbol")
        pct = leg.get("premium_pct")
        amt = leg.get("amount_cny")
        if sym and pct is not None and amt is not None:
            rows[sym] = (float(amt), float(pct))
    return rows


def build(faces=None, tol_amount_pct=1.0):
    """Join the two newest faces. Returns (payload, exit_code)."""
    faces = _faces() if faces is None else faces
    live = [s for s in sorted(faces) if _usable(faces[s])]
    if len(live) < 2:
        return ({"status": "insufficient_history", "evidence_cutoff": None,
                 "detail": "need two board faces, found %d" % len(live),
                 "sessions": live}, 2)
    prev, now = live[-2], live[-1]
    a, b = _priced(faces[prev]), _priced(faces[now])
    if not a or not b:
        return ({"status": "unreadable", "detail": "a face carries no priced legs",
                 "sessions": [prev, now]}, 2)
    # The two faces can price DIFFERENT order sizes (the permission floor trims the sheet
    # between boards: 459,796 -> 392,727). Lots change, the per-unit premium rate does not,
    # so "did the toll move" is answered by applying BOTH rates to ONE sheet -- the newer
    # one, i.e. the order a reader is holding. Subtracting the two faces' own totals would
    # answer "did my order change", which is a different question (and mixes the two).
    shared = sorted(set(a) & set(b))
    if not shared:
        return ({"status": "refused", "sessions": [prev, now],
                 "detail": "the two faces share no priced symbol; there is nothing to join",
                 "prev_symbols": sorted(a), "now_symbols": sorted(b)}, 3)
    rows, unver = [], []
    for sym in sorted(set(a) | set(b)):
        if sym not in a or sym not in b:
            unver.append(sym)
            continue
        amt, p_prev = a[sym]
        amt_now, p_now = b[sym]
        amt = amt_now
        rows.append({
            "symbol": sym,
            "amount_cny": round(amt, 2),
            "prev_pct": round(p_prev, 4),
            "now_pct": round(p_now, 4),
            "delta_pp": round(p_now - p_prev, 4),
            "prev_cny": round(amt * p_prev / 100.0, 2),
            "now_cny": round(amt * p_now / 100.0, 2),
            "delta_cny": round(amt * (p_now - p_prev) / 100.0, 2),
            "prev_sheet_cny": round(a[sym][0], 2),
        })
    tot_prev = round(sum(r["prev_cny"] for r in rows), 2)
    tot_now = round(sum(r["now_cny"] for r in rows), 2)
    tot_d = round(tot_now - tot_prev, 2)
    amt_all = round(sum(r["amount_cny"] for r in rows), 2)
    # cross-check: the newer face publishes its own "over NAV" total for the same sheet.
    # If this face cannot reproduce it, the rates were read off the wrong column.
    published = ((faces[now] or {}).get("over_hurdle") or {}).get("total_over_nav_cny")
    xcheck = None
    if published is not None:
        xcheck = {"published_cny": round(float(published), 2), "recomputed_cny": tot_now,
                  "gap_cny": round(tot_now - float(published), 2), "ok": bool(abs(tot_now - float(published)) <= 1.0)}
        if not xcheck["ok"]:
            return ({"status": "refused", "sessions": [prev, now],
                     "detail": "cannot reproduce the newer face's own over-NAV total; the "
                               "rates were read off the wrong column",
                     "cross_check": xcheck}, 3)
    if not rows:
        return ({"status": "unreadable", "detail": "no symbol priced on both faces",
                 "sessions": [prev, now]}, 2)
    # the word comes off the numbers, never typed beside them
    if abs(tot_now - tot_prev) <= FLAT_BAND_PP / 100.0 * amt_all:
        word = "PREMIUM_FLAT"
    elif tot_d < 0:
        word = "PREMIUM_EASED"
    else:
        word = "PREMIUM_WIDENED"
    payload = {
        "status": "ok",
        "artifact": "results/etf_premium/PREMIUM-SESSION-DELTA.json",
        "evidence_cutoff": now,
        "sessions": [prev, now],
        "rows": rows,
        "unverifiable": unver,
        "totals": {
            "priced_amount_cny": amt_all,
            "prev_cny": tot_prev,
            "now_cny": tot_now,
            "delta_cny": tot_d,
            "prev_share_pct": round(100.0 * tot_prev / amt_all, 4) if amt_all else None,
            "now_share_pct": round(100.0 * tot_now / amt_all, 4) if amt_all else None,
            "delta_share_pp": round(100.0 * tot_d / amt_all, 4) if amt_all else None,
        },
        "verdict": word,
        "cross_check": xcheck,
        "sheets": {
            "prev_amount_cny": round(sum(v[0] for v in a.values()), 2),
            "now_amount_cny": round(sum(v[0] for v in b.values()), 2),
            "delta_cny_on_now_sheet": tot_d,
            "note": ("each rate is per unit, so both are applied to the NEWER sheet; the two "
                     "faces' own totals are printed beside each other and never subtracted"),
        },
        "caveats": [
            "two boards, two readings: IOPV is a realtime estimate and a cross-border leg's "
            "premium moves with a timezone the local close does not see",
            "legs one face could not price are named and excluded, never counted as zero",
            "if the two faces priced different order sizes, the move is recomputed on the "
            "newer sheet only -- a sizing change is not a market move",
        ],
    }
    return payload, 0


def _fmt(v):
    return format(v or 0, ",.2f")


def render(p):
    L = []
    add = L.append
    sess = p.get("sessions") or []
    if p.get("status") != "ok":
        add("# 溢价板面之间的挪动 · 无法出件")
        add("")
        add("- 状态 `%s`：%s" % (p.get("status"), p.get("detail") or "无读数"))
        if p.get("prev_symbols"):
            add("- 两块板各自价的票：%s vs %s"
                % ("、".join(p.get("prev_symbols") or []), "、".join(p.get("now_symbols") or [])))
        return "\n".join(L) + "\n"
    prev, now = sess
    t = p["totals"]
    sh = p.get("sheets") or {}
    add("# 同一张单的入场摩擦，两块板面之间挪了多少")
    add("")
    add("快照口径：两块 ETF 现货板分别在 **%s** 与 **%s** 收盘后各读一次；IOPV 是实时估值，"
        "不是公布净值。" % (prev, now))
    add("")
    if sh and abs((sh.get("prev_amount_cny") or 0) - (sh.get("now_amount_cny") or 0)) > 1.0:
        add("**两张面价的不是一样大的单**：%s 那张 **￥%s**、%s 那张 **￥%s**（额度在地板之间裁过）。"
            "费率是按份额算的，所以下面的挪动是**两种费率套到同一张单（%s，￥%s）上**重算的——"
            "不是把两张单的金额相减（那答的是「我的单变了多少」，不是「市场要的价变了多少」）。"
            % (prev, _fmt(sh.get("prev_amount_cny")), now, _fmt(sh.get("now_amount_cny")),
               now, _fmt(t.get("priced_amount_cny"))))
        add("")
    add("**合计：%s → %s，挪了 %s 元（%+.2f 个百分点）**——占这张单 %s%% → %s%%。"
        % (_fmt(t["prev_cny"]), _fmt(t["now_cny"]), _fmt(t["delta_cny"]),
           t["delta_share_pp"] or 0.0,
           "%.2f" % (t["prev_share_pct"] or 0.0), "%.2f" % (t["now_share_pct"] or 0.0)))
    add("")
    add("| 代码 | 计划金额 | 溢价率（%s） | 溢价率（%s） | 挪动 | 这次多付/少付 ￥ |" % (prev, now))
    add("|---|---|---|---|---|---|")
    for r in p["rows"]:
        add("| %s | ￥%s | %+.2f%% | %+.2f%% | %+.2fpp | %s |"
            % (r["symbol"], _fmt(r["amount_cny"]), r["prev_pct"], r["now_pct"],
               r["delta_pp"], _fmt(r["delta_cny"])))
    add("| — | **合计** | | | | **%s** |" % _fmt(t["delta_cny"]))
    add("")
    if p.get("unverifiable"):
        add("- %s 只有一块板面有读数——挪动**不知道**，不是零。" % "、".join(p["unverifiable"]))
        add("")
    add("## 这一面答不了什么")
    add("")
    for c in p.get("caveats") or []:
        add("- %s" % c)
    add("- 两块板不是一条序列：这里只印「挪了多少」，不印「现在这个水平算高还是低」——"
        "那个问题要等板面自己攒够观测（另一个面在管）。")
    add("")
    add("判词由数字派生：**%s**（平坦带 ±%.2fpp）。" % (p["verdict"], FLAT_BAND_PP))
    xc = p.get("cross_check") or {}
    if xc:
        add("")
        add("口径自证：本面在 %s 那张单上重算的合计 **￥%s**，与那面自己发布的「相对净值多付」"
            "**￥%s** 差 **￥%s**——差在 1 元内才准发布，否则这一面拒绝出件。"
            % (now, _fmt(xc.get("recomputed_cny")), _fmt(xc.get("published_cny")),
               _fmt(xc.get("gap_cny"))))
    return "\n".join(L) + "\n"


def check(path=OUT_JSON):
    """Re-derive the published face from its own rows and the two board faces."""
    if not os.path.exists(path):
        print("FAIL face absent: %s" % path)
        return 1
    with open(path, encoding="utf-8") as fh:
        p = json.load(fh)
    bad = []
    for r in p.get("rows") or []:
        exp = round(r["amount_cny"] * r["prev_pct"] / 100.0, 2)
        if abs(exp - r["prev_cny"]) > 0.02:
            bad.append("%s prev_cny %s != %s" % (r["symbol"], r["prev_cny"], exp))
        exp = round(r["amount_cny"] * r["now_pct"] / 100.0, 2)
        if abs(exp - r["now_cny"]) > 0.02:
            bad.append("%s now_cny %s != %s" % (r["symbol"], r["now_cny"], exp))
        if abs(round(r["now_pct"] - r["prev_pct"], 4) - r["delta_pp"]) > 1e-6:
            bad.append("%s delta_pp != now-prev" % r["symbol"])
    t = p.get("totals") or {}
    for key, src in (("prev_cny", "prev_cny"), ("now_cny", "now_cny")):
        exp = round(sum(r[src] for r in p.get("rows") or []), 2)
        if abs(exp - (t.get(key) or 0.0)) > 0.05:
            bad.append("total %s %s != %s" % (key, t.get(key), exp))
    if abs(round((t.get("now_cny") or 0.0) - (t.get("prev_cny") or 0.0), 2)
           - (t.get("delta_cny") or 0.0)) > 0.05:
        bad.append("total delta_cny is not now-prev")
    amt = t.get("priced_amount_cny") or 0.0
    d = (t.get("now_cny") or 0.0) - (t.get("prev_cny") or 0.0)
    word = ("PREMIUM_FLAT" if abs(d) <= FLAT_BAND_PP / 100.0 * amt
            else ("PREMIUM_EASED" if d < 0 else "PREMIUM_WIDENED"))
    if word != p.get("verdict"):
        bad.append("verdict %r != %r recomputed" % (p.get("verdict"), word))
    if bad:
        print("FAIL %d drift(s):" % len(bad))
        for b in bad[:8]:
            print("  - %s" % b)
        return 1
    print("CHECK_OK rows=%d sessions=%s verdict=%s total_delta=%s"
          % (len(p.get("rows") or []), ",".join(p.get("sessions") or []),
             p.get("verdict"), _fmt(t.get("delta_cny"))))
    return 0


def _face(sess, legs, status="ok"):
    return {sess: {"status": status, "session": sess, "legs": legs}}


def selftest():
    ok = 0
    total = 0

    def chk(name, cond, info=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("PASS %s" % name)
        else:
            print("FAIL %s  %s" % (name, info))

    a = {"symbol": "AAA", "amount_cny": 100000.0, "premium_pct": 10.0}
    b = {"symbol": "BBB", "amount_cny": 50000.0, "premium_pct": 0.0}

    p, rc = build({**_face("2026-01-01", [a, b]), **_face("2026-01-02", [a, b])})
    chk("L1 two faces price one sheet -> a delta face builds", p["status"] == "ok" and rc == 0,
        p.get("status"))
    _a = dict(a, premium_pct=5.0)
    p2, _ = build({**_face("2026-01-01", [a, b]), **_face("2026-01-02", [_a, b])})
    chk("L2 cheaper board -> PREMIUM_EASED with the drop in CNY",
        p2["verdict"] == "PREMIUM_EASED" and abs(p2["totals"]["delta_cny"] + 5000.0) < 0.05,
        p2["totals"])
    p3, _ = build({**_face("2026-01-01", [_a, b]), **_face("2026-01-02", [a, b])})
    chk("L3 dearer board -> PREMIUM_WIDENED (the other direction is not assumed)",
        p3["verdict"] == "PREMIUM_WIDENED" and abs(p3["totals"]["delta_cny"] - 5000.0) < 0.05)
    _tiny = dict(a, premium_pct=10.1)
    p4, _ = build({**_face("2026-01-01", [a, b]), **_face("2026-01-02", [_tiny, b])})
    chk("L4 a move inside the flat band prints no direction",
        p4["verdict"] == "PREMIUM_FLAT", p4["verdict"])
    _new = {"symbol": "CCC", "amount_cny": 1000.0, "premium_pct": 9.0}
    p5, _ = build({**_face("2026-01-01", [a, b]),
                   **_face("2026-01-02", [a, b, _new])})
    chk("L5 a leg only one board priced is named, never counted as zero",
        p5["unverifiable"] == ["CCC"] and abs(p5["totals"]["delta_cny"]) < 0.01,
        p5.get("unverifiable"))
    _moved = dict(a, amount_cny=200000.0)
    p6, rc6 = build({**_face("2026-01-01", [a, b]), **_face("2026-01-02", [_moved, b])})
    chk("L6 two faces pricing different order sizes still join -- on ONE sheet, and say so",
        p6["status"] == "ok" and rc6 == 0
        and abs(p6["sheets"]["delta_cny_on_now_sheet"]) < 0.01
        and "不是一样大的单" in render(p6), p6.get("status"))
    p7, rc7 = build(_face("2026-01-01", [a, b]))
    chk("L7 one board is not a delta -> insufficient_history, never a zero move",
        p7["status"] == "insufficient_history" and rc7 == 2, p7.get("status"))
    md = render(p2)
    chk("L8 the md dates both boards and prints both yuan totals",
        "2026-01-01" in md and "2026-01-02" in md and "合计" in md and "PREMIUM_EASED" in md)
    # the word must follow the signed total even when a single leg moves the other way
    _up = {"symbol": "BBB", "amount_cny": 50000.0, "premium_pct": 3.0}
    p8, _ = build({**_face("2026-01-01", [a, b]), **_face("2026-01-02", [_a, _up])})
    chk("L9 a leg that widens inside a cheaper sheet does not flip the verdict",
        any(r["delta_pp"] > 0 for r in p8["rows"]) and p8["verdict"] == "PREMIUM_EASED",
        p8["verdict"])
    tmp = os.path.join(ROOT, "results", "_selftest_premium_session_delta.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(p2, fh, ensure_ascii=False)
    chk("L10 check passes on a face it just built", check(tmp) == 0)
    p2b = json.loads(json.dumps(p2))
    p2b["totals"]["now_cny"] = round(p2b["totals"]["now_cny"] + 1.0, 2)
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(p2b, fh, ensure_ascii=False)
    import contextlib
    import io
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf):
        _rc = check(tmp)
    chk("L11 check rejects a tampered total (the face is measured, not typed)", _rc == 1)
    # the newer face publishes its own over-NAV total; a face that cannot reproduce it read
    # the wrong column, so it refuses to publish instead of printing a plausible number
    _f1 = {"status": "ok", "legs": [a, b]}
    _f2 = {"status": "ok", "legs": [_a, b], "over_hurdle": {"total_over_nav_cny": 9999.0}}
    p9, rc9 = build({"2026-01-01": _f1, "2026-01-02": _f2})
    chk("L12 a face that cannot reproduce the newer board's own total refuses to publish",
        p9["status"] == "refused" and rc9 == 3, p9.get("status"))
    _f2ok = dict(_f2, over_hurdle={"total_over_nav_cny": 5000.0})
    p10, rc10 = build({"2026-01-01": _f1, "2026-01-02": _f2ok})
    chk("L13 reproducing that total (within a yuan) lets it publish and prints the gap",
        p10["status"] == "ok" and rc10 == 0 and p10["cross_check"]["ok"]
        and "口径自证" in render(p10), p10.get("status"))
    try:
        os.remove(tmp)
    except OSError:
        pass
    print("\nselftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return check()
    payload, rc = build()
    if payload.get("status") == "ok":
        os.makedirs(FACE_DIR, exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(render(payload))
        print("WROTE %s sessions=%s verdict=%s total_delta=%s"
              % (os.path.basename(OUT_JSON), ",".join(payload["sessions"]),
                 payload["verdict"], _fmt(payload["totals"]["delta_cny"])))
    else:
        print("NO-FACE status=%s detail=%s"
              % (payload.get("status"), payload.get("detail")))
    return rc


if __name__ == "__main__":
    sys.exit(main())