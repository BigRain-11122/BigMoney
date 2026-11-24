"""One unreadable rail out of five blanks the whole permission -- is that necessary?

Background
----------
`scripts/etf_book_rebalance_permission.py` computes the permission as

    permitted_k = min(paths.values())          # min over PATH readings only

and then, on the very next statement, does

    if unreadable:  ->  verdict=UNREADABLE, permitted_k=None, keep_allowed=None

So a single rail that cannot be *classified* blanks the number, even though the
unreadable rail was never going to enter `paths` (line 147 `continue`s past it).  On
2026-11-24 the rail that broke was `baseline_published` (k=0.460253, the circularity
identity against the ticket's k_rule=0.458463), and the three path rails --
window 0.747086 / universe 0.435003 / window_x_universe 0.667665 -- were all readable
and all agree the floor is 0.435003.  The book then lost its permission row, the gap
face wrote a stub without `gap_k`, and three smoke legs died with KeyError/TypeError
instead of saying "upstream is unreadable".

That blank is *conservative but not always necessary*.  An unreadable rail can only
lower the floor if its own number sits below the current floor line
(`k_now - size_tol`); if it sits at or above, the minimum over the readable paths is
already the answer and blanking hides a decision that is safe to print.  This face
turns that observation into a rule with two verdicts:

    FLOOR_IS_COMPUTABLE   every unreadable rail is at or above the floor line ->
                           publish min(readable paths), carry the unreadable rail as a
                           declared caveat
    FLOOR_MUST_WAIT        an unreadable rail is missing its number or sits below the
                           floor line -> it could be the binding floor; blank is right

It is **descriptive only**: it never edits the permission face, never edits the gap
face, never relaxes the producer's rule.  It prices what the blanket blank costs so a
future round can decide, with numbers, whether to change the producer.

Usage
-----
    python scripts/etf_book_unreadable_rail_floor.py run        # derive + write page block
    python scripts/etf_book_unreadable_rail_floor.py --check    # re-derive and compare
    python scripts/etf_book_unreadable_rail_floor.py --selftest
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

PERM = os.path.join("results", "etf_book_rebalance_permission.json")
GAP = os.path.join("results", "etf_book_cut_order_gap.json")
LEGS = os.path.join("logs", "smoke_legs.json")
OUT = os.path.join("results", "etf_book_unreadable_rail_floor.json")
PAGE = os.path.join("research", "ETF_BOOK_UNREADABLE_RAIL_FLOOR.md")
BEGIN = "<!-- BEGIN unreadable_rail_floor -->"
END = "<!-- END unreadable_rail_floor -->"

SCHEMA = "etf-book-unreadable-rail-floor/v1"
DEFAULT_TOL = 0.005

# the crash shapes the blank produces downstream; the leg names are *read* from the
# last smoke reading, never written down here
CRASH_TOKENS = ("KeyError: 'gap_k'", "KeyError: 'cash_cny'", "not 'NoneType'")


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _machine_id() -> str:
    try:
        return _read_json(os.path.join("fleet", "machine.json")).get("machine_id") or "unknown"
    except Exception:
        return "unknown"


def floor_from_readings(readings: dict, k_now: float, size_tol: float) -> dict:
    """Pure function: a readings table -> the floor the blanket blank is hiding.

    No disk, no clock.  `k_now` is the size the book currently holds; `size_tol` is the
    producer's own keep/trim tolerance, so the floor line is `k_now - size_tol`.
    """
    paths = {}
    statics = {}
    unreadable = {}
    for name, cell in (readings or {}).items():
        kind = (cell or {}).get("kind")
        k = (cell or {}).get("k")
        if kind == "path" and k is not None:
            paths[name] = float(k)
        elif kind == "static" and k is not None:
            statics[name] = float(k)
        elif kind == "unreadable":
            unreadable[name] = None if k is None else float(k)

    floor_line = float(k_now) - float(size_tol)

    # an unreadable rail can only bind the floor if it could sit *below* every readable
    # path; that requires a number, and requires it to be under the floor line
    would_bind = sorted(
        name for name, k in unreadable.items()
        if k is None or k < floor_line - 1e-12
    )

    out = {
        "k_now": round(float(k_now), 6),
        "size_tol": float(size_tol),
        "floor_line_k": round(floor_line, 6),
        "readable_paths": {n: round(k, 6) for n, k in sorted(paths.items())},
        "static_rails": {n: round(k, 6) for n, k in sorted(statics.items())},
        "unreadable_rails": {n: (None if k is None else round(k, 6))
                             for n, k in sorted(unreadable.items())},
        "unreadable_rails_that_could_bind": would_bind,
    }

    if not paths:
        out["verdict"] = "FLOOR_MUST_WAIT"
        out["why"] = ("no reading was measured on a decision path -- there is no floor to "
                      "publish, blank or not")
        out["permitted_k"] = None
        out["keep_allowed"] = None
        out["cut_k"] = None
        out["cut_pp"] = None
        return out

    if would_bind:
        out["verdict"] = "FLOOR_MUST_WAIT"
        out["why"] = ("%s could sit below the floor line %.6f, so min(readable paths) is "
                      "not the permission -- the blank is the honest answer"
                      % (", ".join(would_bind), floor_line))
        out["permitted_k"] = None
        out["keep_allowed"] = None
        out["cut_k"] = None
        out["cut_pp"] = None
        return out

    permitted = min(paths.values())
    keep = any(k >= floor_line - 1e-12 for k in paths.values())
    out["verdict"] = "FLOOR_IS_COMPUTABLE"
    out["why"] = ("every unreadable rail sits at or above the floor line %.6f, so the "
                  "minimum over the %d readable path(s) is already the permission"
                  % (floor_line, len(paths)))
    out["permitted_k"] = round(permitted, 6)
    out["keep_allowed"] = bool(keep)
    out["cut_k"] = round(float(k_now) - permitted, 6)
    out["cut_pp"] = round(100.0 * (float(k_now) - permitted), 2)
    out["binding_rail"] = sorted(n for n, k in paths.items() if k == permitted)[0]
    return out


def _digest(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def derive(now_epoch: float | None = None) -> dict:
    perm = _read_json(PERM)
    gap = _read_json(GAP)
    k_now = perm.get("k_now")
    nav = perm.get("nav_cny")
    size_tol = float(perm.get("size_tol") or DEFAULT_TOL)

    if k_now is None or nav is None:
        reading = {
            "schema": SCHEMA,
            "verdict": "FLOOR_MUST_WAIT",
            "why": "the permission face does not even carry k_now/nav -- nothing to price",
            "permitted_k": None,
            "keep_allowed": None,
            "published_verdict": perm.get("verdict"),
            "cascade_legs": [],
        }
    else:
        floor = floor_from_readings(perm.get("readings") or {}, float(k_now), size_tol)
        published_k = perm.get("permitted_k")
        gross = None if floor.get("permitted_k") is None else floor["permitted_k"] * float(nav)
        book = perm.get("book_amount_cny")
        reading = dict(floor)
        reading.update({
            "schema": SCHEMA,
            "nav_cny": float(nav),
            "published_verdict": perm.get("verdict"),
            "published_sentence": perm.get("sentence"),
            "published_permitted_k": published_k,
            "blank_is_in_force": published_k is None,
            "permitted_book_cny_gross": None if gross is None else round(gross, 2),
            "book_amount_cny": book,
            "headroom_vs_book_cny": (None if gross is None or book is None
                                     else round(gross - float(book), 2)),
            "permission_face_generated": perm.get("generated"),
        })

    # the cascade: the gap face's stub, and every smoke leg that dies on it
    reading["gap_face_has_gap_k"] = "gap_k" in gap
    reading["gap_face_verdict"] = gap.get("verdict")
    reading["gap_face_generated"] = gap.get("generated")
    legs = {}
    try:
        legs = _read_json(LEGS)
    except Exception:
        pass
    cascade = []
    for leg in legs.get("failed") or []:
        detail = leg.get("detail") or ""
        hit = [t for t in CRASH_TOKENS if t in detail]
        if hit:
            cascade.append({"leg": leg.get("name"), "crash": hit[0], "detail": detail[:200]})
    reading["cascade_legs"] = cascade
    reading["cascade_reading_ts"] = legs.get("ts")
    reading["cascade_reading_counts"] = (None if not legs else
                                         {"legs": legs.get("legs"), "fail": legs.get("fail")})
    reading["machine_id"] = _machine_id()
    reading["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S",
                                         time.localtime(now_epoch if now_epoch is not None
                                                        else time.time()))
    reading["inputs_digest"] = _digest({
        "perm_generated": perm.get("generated"),
        "perm_verdict": perm.get("verdict"),
        "perm_permitted_k": perm.get("permitted_k"),
        "readings": perm.get("readings"),
        "k_now": perm.get("k_now"),
        "nav": perm.get("nav_cny"),
        "size_tol": perm.get("size_tol"),
        "gap_generated": gap.get("generated"),
        "gap_has_gap_k": "gap_k" in gap,
        "legs_ts": legs.get("ts"),
        "legs_fail": legs.get("fail"),
    })
    return reading


def _advice(verdict: str) -> str:
    return {
        "FLOOR_IS_COMPUTABLE": "权限可以印；未分类轨必须作为声明并列，禁默默丢掉。",
        "FLOOR_MUST_WAIT": "权限不能印；先修那条读不出的轨，别拿可读数当上限。",
    }.get(verdict, "—")


def render(reading: dict) -> str:
    v = reading["verdict"]
    paths = reading.get("readable_paths") or {}
    unread = reading.get("unreadable_rails") or {}
    lines = [
        BEGIN,
        "generated %s | verdict **%s** | machine %s | inputs %s" % (
            reading.get("generated") or "?", v, reading.get("machine_id", "?"),
            str(reading.get("inputs_digest"))[:12]),
        "",
        "| 项 | 读数 |",
        "|---|---|",
        "| 在册尺寸 k_now | %s |" % _pct(reading.get("k_now")),
        "| 地板线 k_now-size_tol | %s |" % _pct(reading.get("floor_line_k")),
        "| 可读路径轨 | %s |" % (", ".join("%s %s" % (n, _pct(k)) for n, k in paths.items())
                                 or "无"),
        "| 读不出的轨 | %s |" % (", ".join("%s %s" % (n, _pct(k)) for n, k in unread.items())
                                  or "无"),
        "| 会压低地板的那条 | %s |" % (", ".join(reading.get("unreadable_rails_that_could_bind"))
                                        or "无（都在地板线上或之上）"),
        "| 权限（按规则） | %s |" % _pct(reading.get("permitted_k")),
        "| 绑定轨 | %s |" % (reading.get("binding_rail") or "—"),
        "| 可保留 | %s |" % _keep(reading.get("keep_allowed")),
        "| 应变现（pp） | %s |" % _num(reading.get("cut_pp")),
        "| 已发布面判词 | %s |" % (reading.get("published_verdict") or "—"),
        "| 已发布 permitted_k | %s |" % _pct(reading.get("published_permitted_k")),
        "| 按规则可持（毛额） | %s |" % _cny(reading.get("permitted_book_cny_gross")),
        "| 票面在册市值 | %s |" % _cny(reading.get("book_amount_cny")),
        "| 距权限余量 | %s |" % _cny(reading.get("headroom_vs_book_cny")),
        "| 对下面摊 gap 面 | %s（generated %s） |" % (
            "有 gap_k" if reading.get("gap_face_has_gap_k") else "**没有 gap_k（存根）**",
            reading.get("gap_face_generated") or "—"),
        "| 冒烟红腿读数 | %s |" % _legs(reading),
        "",
        "**判词**：%s" % v,
        "",
        "> %s" % reading.get("why", ""),
        "",
        "**本轮可做什么**：%s" % _advice(v),
        END,
    ]
    return "\n".join(lines)


def _pct(x):
    return "—" if x is None else "%.6f%%" % (100.0 * float(x))


def _num(x):
    return "—" if x is None else "%.2f" % float(x)


def _cny(x):
    return "—" if x is None else "{:,.2f} 元".format(float(x))


def _keep(x):
    return "—" if x is None else ("可保留" if x else "不可保留")


def _legs(reading):
    counts = reading.get("cascade_reading_counts") or {}
    cascade = reading.get("cascade_legs") or []
    if not counts:
        return "（读不到 logs/smoke_legs.json）"
    return "%s 条腿 / %s 红 @ %s；其中 %d 条死在这张存根上" % (
        counts.get("legs"), counts.get("fail"), reading.get("cascade_reading_ts") or "?",
        len(cascade))


def write_page(block: str) -> None:
    header = (
        "# 一条读不出的轨，凭什么让整本书闭嘴\n\n"
        "一张面，回答每轮都要问的那句话：权限面把整本书按成 UNREADABLE 的时候，\n"
        "到底是「算不出来」还是「算得出来却不肯印」？\n"
        "由 `scripts/etf_book_unreadable_rail_floor.py` 渲染；只描述不修面、不放宽规则。\n\n"
    )
    footer = (
        "\n## 它不声称什么\n\n"
        "- 不改 `scripts/etf_book_rebalance_permission.py` 的判据（共享面，竞争窗内禁改）\n"
        "- 不替代 producer 的 `UNREADABLE`：它只说「这条轨无法分类」，本面说的是「无法分类"
        "能不能证明印不出来」——两句话不是一句\n"
        "- 未分类轨永远要作为声明并列：本面给的是下限，不是把那条轨当成「没问题」\n"
    )
    if os.path.exists(PAGE):
        with open(PAGE, encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = header + BEGIN + "\n" + END + "\n" + footer
    if BEGIN in text and END in text:
        head = text.split(BEGIN)[0]
        tail = text.split(END, 1)[1]
        text = head + block + tail
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def cmd_run() -> int:
    reading = derive()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(reading, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    write_page(render(reading))
    print("UNREADABLE-RAIL-FLOOR %s permitted_k=%s keep_allowed=%s cut_pp=%s cascade_legs=%d" % (
        reading["verdict"], reading.get("permitted_k"), reading.get("keep_allowed"),
        reading.get("cut_pp"), len(reading.get("cascade_legs") or [])))
    return 0


def cmd_check() -> int:
    """Re-derive and compare.  Inputs moved -> STALE (pay for the rebuild); same inputs
    different numbers -> a disagreement (no STALE word, so the chain does not rebuild)."""
    fresh = derive()
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    old = _read_json(OUT)
    if old.get("inputs_digest") != fresh.get("inputs_digest"):
        print("STALE inputs moved: %s -> %s" % (
            str(old.get("inputs_digest"))[:12], str(fresh.get("inputs_digest"))[:12]))
        return 3
    diffs = []
    for key in ("verdict", "permitted_k", "keep_allowed", "cut_pp", "binding_rail",
                "gap_face_has_gap_k", "floor_line_k"):
        if old.get(key) != fresh.get(key):
            diffs.append("%s: face=%r rederive=%r" % (key, old.get(key), fresh.get(key)))
    if diffs:
        print("CHECK FAILED (same inputs, different numbers -- a disagreement, not drift): %s"
              % "; ".join(diffs)[:300])
        return 3
    if not os.path.exists(PAGE):
        print("STALE page missing: %s" % PAGE)
        return 3
    with open(PAGE, encoding="utf-8") as fh:
        text = fh.read()
    if BEGIN not in text or END not in text:
        print("STALE page has no marker block")
        return 3
    block = text.split(BEGIN, 1)[1].split(END, 1)[0]
    want = render(old).split(BEGIN, 1)[1].split(END, 1)[0]
    if block.strip() != want.strip():
        print("CHECK FAILED page block does not match re-derivation")
        return 3
    print("UNREADABLE-RAIL-FLOOR CHECK OK verdict=%s permitted_k=%s" % (
        fresh["verdict"], fresh.get("permitted_k")))
    return 0


def selftest() -> int:
    ok = 0
    bad = []

    def chk(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s %s" % (name, detail))

    K_NOW = 0.435003
    TOL = 0.005
    FLOOR_LINE = K_NOW - TOL

    # the live table, reproduced with fixed numbers (no disk, no clock)
    live = {
        "baseline_published": {"kind": "unreadable", "k": 0.460253},
        "window": {"kind": "path", "k": 0.747086},
        "universe": {"kind": "path", "k": 0.435003},
        "window_x_universe": {"kind": "path", "k": 0.667665},
        "denominator": {"kind": "static", "k": 0.343508},
    }
    r = floor_from_readings(live, K_NOW, TOL)

    # 1-3. today's table is computable and lands exactly on the size in force
    chk("live table reads FLOOR_IS_COMPUTABLE", r["verdict"] == "FLOOR_IS_COMPUTABLE",
        r["verdict"])
    chk("permission is min(readable paths) = 0.435003",
        r["permitted_k"] == 0.435003, r["permitted_k"])
    chk("cut is zero pp", r["cut_pp"] == 0.0, r["cut_pp"])
    chk("keeping is allowed", r["keep_allowed"] is True, r["keep_allowed"])
    chk("binding rail is named", r["binding_rail"] == "universe", r["binding_rail"])

    # 4. the static rail never enters the floor (0.343508 < 0.435003)
    chk("static rail does not set the floor", r["permitted_k"] != 0.343508, r["permitted_k"])

    # 5. an unreadable rail BELOW the floor line could bind -> must wait
    low = dict(live)
    low["baseline_published"] = {"kind": "unreadable", "k": 0.30}
    r2 = floor_from_readings(low, K_NOW, TOL)
    chk("unreadable rail below the floor reads MUST_WAIT",
        r2["verdict"] == "FLOOR_MUST_WAIT", r2["verdict"])
    chk("must-wait prints no permission", r2["permitted_k"] is None, r2["permitted_k"])
    chk("must-wait names the rail", r2["unreadable_rails_that_could_bind"] == ["baseline_published"],
        r2["unreadable_rails_that_could_bind"])

    # 6. an unreadable rail with no number at all also blocks
    nonum = dict(live)
    nonum["baseline_published"] = {"kind": "unreadable", "k": None}
    r3 = floor_from_readings(nonum, K_NOW, TOL)
    chk("unreadable rail with no k reads MUST_WAIT", r3["verdict"] == "FLOOR_MUST_WAIT",
        r3["verdict"])

    # 7. boundary: exactly on the floor line is NOT stricter than the floor
    edge = dict(live)
    edge["baseline_published"] = {"kind": "unreadable", "k": FLOOR_LINE}
    r4 = floor_from_readings(edge, K_NOW, TOL)
    chk("unreadable rail exactly on the floor line is computable",
        r4["verdict"] == "FLOOR_IS_COMPUTABLE", r4["verdict"])

    # 8. one epsilon below the line flips it
    below = dict(live)
    below["baseline_published"] = {"kind": "unreadable", "k": FLOOR_LINE - 1e-9}
    r5 = floor_from_readings(below, K_NOW, TOL)
    chk("one epsilon below the line flips to MUST_WAIT",
        r5["verdict"] == "FLOOR_MUST_WAIT", r5["verdict"])

    # 9. no readable path at all -> must wait, and it is not the unreadable rule speaking
    nopath = {"baseline_published": {"kind": "unreadable", "k": 0.46},
              "denominator": {"kind": "static", "k": 0.34}}
    r6 = floor_from_readings(nopath, K_NOW, TOL)
    chk("no path reads MUST_WAIT", r6["verdict"] == "FLOOR_MUST_WAIT", r6["verdict"])
    chk("no-path reason mentions the path, not the unreadable rail",
        "decision path" in r6["why"], r6["why"][:60])

    # 10. verdict is a function, not a constant
    chk("verdict differs by input", r["verdict"] != r2["verdict"])

    # 11. the crash really reproduces from the stub on disk (this is the cascade claim)
    try:
        stub = _read_json(GAP)
        _ = stub["gap_k"]
        crashed = False
    except KeyError as exc:
        crashed = str(exc) == "'gap_k'"
    except Exception:
        crashed = False
    chk("the gap face stub really raises KeyError('gap_k')", crashed)

    # 12. and the permission face really publishes a null permission today
    perm = _read_json(PERM)
    chk("published permission is blank", perm.get("permitted_k") is None,
        perm.get("permitted_k"))
    chk("published verdict is UNREADABLE", perm.get("verdict") == "UNREADABLE",
        perm.get("verdict"))

    # 13. the money arithmetic uses the face's own nav
    live_reading = derive(now_epoch=1795551234.0)
    if live_reading.get("permitted_k") is not None:
        want = round(live_reading["permitted_k"] * live_reading["nav_cny"], 2)
        chk("gross permission = k * nav", live_reading["permitted_book_cny_gross"] == want,
            (live_reading.get("permitted_book_cny_gross"), want))
    else:
        chk("gross permission = k * nav", live_reading.get("permitted_book_cny_gross") is None)

    # 14. the page block prints the verdict and the unreadable rail
    blk = render({**r, "machine_id": "bm-c", "inputs_digest": "0" * 64,
                  "published_verdict": "UNREADABLE", "published_permitted_k": None,
                  "gap_face_has_gap_k": False, "cascade_legs": [], "cascade_reading_counts": None})
    chk("block prints the verdict", "FLOOR_IS_COMPUTABLE" in blk)
    chk("block prints the unreadable rail", "baseline_published" in blk)

    # 15. digest is order-insensitive on the readings table
    d1 = _digest({"readings": live, "x": 1})
    d2 = _digest({"readings": dict(reversed(list(live.items()))), "x": 1})
    chk("digest is order-insensitive", d1 == d2)
    chk("digest catches a changed rail", d1 != _digest({"readings": {**live, "universe": {
        "kind": "path", "k": 0.5}}, "x": 1}))

    if bad:
        print("SELFTEST FAILED %d/%d" % (ok, ok + len(bad)))
        for b in bad:
            print("  -", b)
        return 1
    print("SELFTEST OK %d/%d" % (ok, ok))
    return 0


def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest":
        return selftest()
    if cmd == "--check":
        return cmd_check()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
