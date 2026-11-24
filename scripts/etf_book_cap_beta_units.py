"""One cap, two units: the book is 2.18x the ladder in notional and at the cap in beta.

The CEO page prints the book next to the risk ladder and says only that it is "listed in
the same table but does not enter the verdict".  The cap-vs-book face files it as
`own_rule` with `gap_pp 23.5` -- i.e. the ETF book carries 43.5% of NAV while the RED rung
allows 20%.  Read as notional exposure that is a 2.18x breach; read as *market* exposure it
is a different number entirely, because 43.5% of a book whose realised beta is 0.48 is not
43.5% of the market.

This face does the conversion instead of arguing about it:

  1. beta-units exposure = k x beta, with beta read from `etf_book_beta_paths` (both the
     full-history and the current-window reading, because that face itself says the window
     choice is worth only 1.96pp of k while the ruler carries 12.24pp of noise);
  2. the ladder rung that binds today, machine-read from the market clock, plus the other
     rungs as frozen law so a reader can see what each rung would allow in notional;
  3. the trim in CNY that would put beta-units exactly on the cap, and the ruler noise in
     the same units, so "over" and "at" can be told apart;
  4. the identity that makes the book what it is: k = beta_target / beta.  If that holds,
     the book's own rule *is* the RED rung expressed in beta units, held in every regime --
     which is why the rungs above RED are unreachable without leverage.

Nothing here is a recommendation: both readings are printed, the noise is printed next to
them, and the verdict says which question each one answers.
"""
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

OUT = os.path.join(REPO, "results", "etf_book_cap_beta_units.json")
PAGE = os.path.join(REPO, "research", "ETF_BOOK_CAP_BETA_UNITS.md")
BETA_FACE = os.path.join(REPO, "results", "etf_book_beta_paths.json")
CLOCK_FACE = os.path.join(REPO, "results", "market_clock", "call_latest.json")
TICKET_PTR = os.path.join(REPO, "results", "etf_book_order", "latest.json")
CAP_FACE = os.path.join(REPO, "results", "regime_cap_vs_book.json")

# firm/risk/REGIME_GUARD.md section 1 (frozen).  Only the rung that binds today is
# machine-read (market_clock.position_cap_ladder); the rest are quoted so the page can show
# what each rung would allow, and the face asserts the quoted rung equals the read one.
RUNGS = (("RED", 0.20), ("ORANGE", 0.50), ("YELLOW", 0.65), ("GREEN", 0.80),
         ("GREENxHOT", 0.95))
RUNG_SOURCE = "firm/risk/REGIME_GUARD.md section 1 (frozen law)"
SIZE_TOL = 0.005          # 0.5pp on k: the same "same size" tolerance the rulers table uses


# ---------------------------------------------------------------------------------------
# pure helpers (the selftest holds these without any face on disk)
# ---------------------------------------------------------------------------------------
def beta_units(k, beta):
    """Market exposure implied by holding `k` of a book whose beta is `beta`."""
    return float(k) * float(beta)


def multiple(x, cap):
    if cap <= 0:
        raise ValueError("cap must be positive")
    return float(x) / float(cap)


def trim_cny(k, beta, cap, nav):
    """CNY to sell so that beta-units lands on the cap.  Negative = already inside."""
    if beta <= 0:
        raise ValueError("beta must be positive")
    return (beta_units(k, beta) - float(cap)) / float(beta) * float(nav)


def band_units(k_noise_sd, beta):
    """The beta ruler's own k-noise, carried into beta units."""
    return abs(float(k_noise_sd)) * float(beta)


def verdict_of(cap, eq, band):
    """Three states, and the middle one is the honest one for this book.

    A number inside the ruler's own noise is neither compliance nor breach; calling it
    either way is arithmetic pretending to be measurement (r1935 family).
    """
    band = abs(float(band))
    if float(eq) - float(cap) > band:
        return "OVER_CAP_BEYOND_THE_RULER"
    if float(cap) - float(eq) > band:
        return "UNDER_CAP_BEYOND_THE_RULER"
    return "AT_CAP_WITHIN_RULER_NOISE"


def reading_in_notional(k, cap):
    """The other unit, stated as its own verdict so the two never get merged."""
    m = multiple(k, cap)
    if m > 1.0:
        return "ABOVE_CAP", m
    if m < 1.0:
        return "INSIDE_CAP", m
    return "AT_CAP", m


def rung_rows(eq, beta):
    """What each rung of the frozen ladder would allow, in the same two units."""
    rows = []
    for name, cap in RUNGS:
        allowed_k = (float(cap) / float(beta)) if beta > 0 else None
        rows.append({
            "rung": name,
            "cap": float(cap),
            "headroom_pp": round(100.0 * (float(cap) - float(eq)), 2),
            "k_allowed": None if allowed_k is None else round(allowed_k, 6),
            "needs_leverage": bool(allowed_k is not None and allowed_k > 1.0),
        })
    return rows


# ---------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------
def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def digest_of(paths):
    h = hashlib.sha256()
    for p in paths:
        with open(p, "rb") as fh:
            blob = fh.read()
        h.update(os.path.basename(p).encode("utf-8"))
        h.update(str(len(blob)).encode("ascii"))
        h.update(blob)
    return h.hexdigest()


def input_paths(ticket_path):
    return [BETA_FACE, CLOCK_FACE, TICKET_PTR, ticket_path, CAP_FACE]


def build():
    beta_f = load(BETA_FACE)
    clock = load(CLOCK_FACE)
    ptr = load(TICKET_PTR)
    ticket_path = os.path.join(os.path.dirname(TICKET_PTR), ptr["file"])
    ticket = load(ticket_path)
    cap_f = load(CAP_FACE)

    state = str(clock.get("regime_v3", {}).get("state") or "?")
    cap = float(clock["position_cap_ladder"])
    k = float(ptr["k_now"])
    nav = float(ticket["ticket"]["nav"])
    b_now = float(beta_f["beta_now"])
    b_full = float(beta_f["beta_full"])
    b_target = float(beta_f.get("beta_target") or 0.0)
    noise = float(beta_f["k_noise_sd"])
    window = int(beta_f.get("window") or 0)

    eq_now = beta_units(k, b_now)
    eq_full = beta_units(k, b_full)
    band = band_units(noise, b_now)
    verdict = verdict_of(cap, eq_now, band)
    notional_state, notional_mult = reading_in_notional(k, cap)

    # the identity that explains the book: k = beta_target / beta
    ident_now = (b_target / b_now) if (b_target and b_now) else None
    ident_full = (b_target / b_full) if (b_target and b_full) else None
    ident_gap_pp = None if ident_full is None else round(100.0 * (k - ident_full), 4)

    # the quoted rung for today's state must equal the rung the clock read
    quoted = dict(RUNGS).get(state)
    rung_agrees = (quoted is not None and abs(float(quoted) - cap) < 1e-9)

    facts = {
        "state": state,
        "cap_now": cap,
        "cap_source": "results/market_clock/call_latest.json:position_cap_ladder",
        "rungs_source": RUNG_SOURCE,
        "quoted_rung_agrees_with_clock": bool(rung_agrees),
        "nav_cny": nav,
        "k_now": k,
        "beta_now": b_now,
        "beta_full": b_full,
        "beta_window": window,
        "beta_target": b_target,
        "k_noise_sd": noise,
        "beta_eq_now": round(eq_now, 6),
        "beta_eq_full": round(eq_full, 6),
        "beta_eq_now_pp": round(100.0 * eq_now, 3),
        "beta_eq_full_pp": round(100.0 * eq_full, 3),
        "over_pp_now": round(100.0 * (eq_now - cap), 3),
        "over_pp_full": round(100.0 * (eq_full - cap), 3),
        "notional_multiple": round(notional_mult, 4),
        "notional_reading": notional_state,
        "beta_multiple_now": round(multiple(eq_now, cap), 4),
        "beta_multiple_full": round(multiple(eq_full, cap), 4),
        "ruler_band_pp": round(100.0 * band, 3),
        "verdict": verdict,
        "trim_cny_now": round(trim_cny(k, b_now, cap, nav), 2),
        "trim_cny_full": round(trim_cny(k, b_full, cap, nav), 2),
        "notional_allowed_now_cny": round(cap / b_now * nav, 2),
        "notional_allowed_full_cny": round(cap / b_full * nav, 2),
        "sizing_identity": {
            "rule": "k = beta_target / beta",
            "k_from_now_beta": None if ident_now is None else round(ident_now, 6),
            "k_from_full_beta": None if ident_full is None else round(ident_full, 6),
            "k_now_minus_identity_pp": ident_gap_pp,
            "holds_now": ident_gap_pp is not None and abs(ident_gap_pp) <= 100.0 * SIZE_TOL,
        },
        "rungs": rung_rows(eq_now, b_now),
        "cross_face": {
            "cap_vs_book_kind": cap_f.get("verdict", {}).get("book"),
            "why_named": "the cap face files the book as own_rule; this face measures what "
                         "own_rule means in the cap's own unit",
        },
        "caveats": [
            "beta is a linear factor reading on a 306-bar window; the beta face itself calls "
            "the window pair worth 1.96pp of k against a 12.24pp ruler, so no claim here "
            "rests on the window choice alone -- both readings are printed",
            "market-equivalence is first order: the book holds commodities and gold, whose "
            "beta to the equity benchmark is not the same risk as an equity sleeve",
            "the trim is arithmetic to the cap, not an order: the ladder caps new risk and "
            "this book has no scheduled trade before its next decision bar",
            "rungs above RED are quoted frozen law, not machine faces; only today's rung is "
            "read from the clock, and the face asserts the two agree",
        ],
    }
    return facts, ticket_path


# ---------------------------------------------------------------------------------------
# page (readings rendered from the face; --check compares them, never a hand-copied table)
# ---------------------------------------------------------------------------------------
BEGIN, END = "<!-- CAP-BETA-BEGIN -->", "<!-- CAP-BETA-END -->"


def render_block(f):
    lines = ["| 读法 | 持仓 | 帽子 | 倍数 | 超出 | 判词 |",
             "|---|---|---|---|---|---|"]
    lines.append("| 名义（仓位 / 帽子） | %.3f%% | %.1f%% | %.2fx | %+.1fpp | %s |"
                 % (100.0 * f["k_now"], 100.0 * f["cap_now"], f["notional_multiple"],
                    100.0 * (f["k_now"] - f["cap_now"]), f["notional_reading"]))
    lines.append("| β 当量（当窗 β %.3f） | %.3f%% | %.1f%% | %.2fx | %+.2fpp | %s |"
                 % (f["beta_now"], f["beta_eq_now_pp"], 100.0 * f["cap_now"],
                    f["beta_multiple_now"], f["over_pp_now"], f["verdict"]))
    lines.append("| β 当量（全史 β %.3f） | %.3f%% | %.1f%% | %.2fx | %+.2fpp | %s |"
                 % (f["beta_full"], f["beta_eq_full_pp"], 100.0 * f["cap_now"],
                    f["beta_multiple_full"], f["over_pp_full"],
                    verdict_of(f["cap_now"], f["beta_eq_full"], f["ruler_band_pp"] / 100.0)))
    body = "\n".join(lines)

    rungs = "\n".join(
        "| %s | %.0f%% | %+.1fpp | %.3f | %s |"
        % (r["rung"], 100.0 * r["cap"], r["headroom_pp"], r["k_allowed"],
           "要杠杆" if r["needs_leverage"] else "--")
        for r in f["rungs"])

    ident = f["sizing_identity"]
    # a negative trim means "already inside": printing it as money to sell would be a lie
    trim_now = max(0.0, float(f["trim_cny_now"]))
    trim_full = max(0.0, float(f["trim_cny_full"]))
    return (
        "%s\n" % BEGIN
        + "| 项 | 读数 |\n|---|---|\n"
        + "| 政体态 / 当期帽子 | %s / %.0f%% |\n" % (f["state"], 100.0 * f["cap_now"])
        + "| 书的仓位 k | %.4f（%s 元 NAV） |\n" % (f["k_now"], "{:,.0f}".format(f["nav_cny"]))
        + "| β（当窗 %d 根 / 全史） | %.4f / %.4f |\n" % (f["beta_window"], f["beta_now"],
                                                        f["beta_full"])
        + "| β 当量（当窗 / 全史） | %.3f%% / %.3f%% |\n" % (f["beta_eq_now_pp"],
                                                           f["beta_eq_full_pp"])
        + "| 尺子自身噪声（β 当量） | ±%.2fpp |\n" % f["ruler_band_pp"]
        + "| 判词 | **%s** |\n" % f["verdict"]
        + "| 卖到帽子上的钱（当窗 β / 全史 β） | %s / %s 元 |\n"
        % ("{:,.0f}".format(trim_now), "{:,.0f}".format(trim_full))
        + "\n" + body + "\n\n"
        + "- 同一顶帽子两种单位：名义上 **%.2fx**（%s），β 当量上 **%.2fx**（%s）；差别不在账面，在单位\n"
        % (f["notional_multiple"], f["notional_reading"], f["beta_multiple_now"],
           f["verdict"])
        + "- 这本书自己的规则是 `%s`：0.2 / %.3f = %.4f，与票面 k=%.4f 差 %.2fpp（%s）\n"
        % (ident["rule"], f["beta_full"], ident["k_from_full_beta"], f["k_now"],
           ident["k_now_minus_identity_pp"], "成立" if ident["holds_now"] else "不成立")
        + "- 于是它在**任何政体**下都按 β 当量 20% 跑：其它档位要的 k 全部 >1（要杠杆），"
          "RED 档是它唯一会碰到的档\n"
        + "\n阶梯各档换算：\n\n| 档 | 帽子 | 距当前 β 当量 | 该档允许的 k | 备注 |\n"
          "|---|---|---|---|---|\n" + rungs + "\n"
        + END
    )


def write_doc(f):
    block = render_block(f)
    head = (
        "# 同一顶帽子，两种单位\n\n"
        "CEO 一页纸上，ETF 复合书与阶梯总帽并排放着，只写了一句「列在同一张表但不进裁决」；"
        "帽子对账面则把它归成 `own_rule`，差额 23.5pp。读者据此只能得到「这本书是帽子的 2.18 倍」"
        "这个结论——而这个结论量的是**名义敞口**，不是**市场敞口**。\n\n"
        "这本书持仓 43.5%，其实现 β 约 0.48，所以它对市场的敞口是 43.5% × 0.48 ≈ 20.9%。"
        "同一顶 20% 的帽子，用两种单位去量，一个说超 2.18 倍，一个说超 0.94pp，"
        "而后者还在尺子自己 ±5.89pp 的噪声里。本面把两种单位并排印出来，并回答第三个问题："
        "这本书的仓位规则与帽子是不是一回事。\n\n"
        "## 读数\n\n"
    )
    tail = (
        "\n## 它不声称什么\n\n"
        "- 不是「超额合规」的辩护：β 当量 20.94% 确实在 20% 上面，只是在尺子噪声之内；"
        "真要严格在帽下，今天该卖 19,543 元（当窗 β）或 0 元（全史 β）\n"
        "- 不是新回测：全部数字由三张既有面（β 面、帽子对账面、市场时钟）与本票面算术派生\n"
        "- 不是建议改 β 目标：把 β 目标从 0.2 抬到 0.8 会让这本书在 GREEN 档用满杠杆预算，"
        "那是设计决定，不是本面能签的字\n"
        "- β 是一阶线性读数，商品与黄金袖对指数 β 不承载其在组合内的真实风险\n\n"
        "复跑：`python scripts/etf_book_cap_beta_units.py`（写面与本块）、`--check`（重算逐字比对）、"
        "`--selftest`（离线腿）。\n"
    )
    text = head + block + tail
    old = None
    if os.path.exists(PAGE):
        with io.open(PAGE, encoding="utf-8") as fh:
            old = fh.read()
    if old and BEGIN in old and END in old:
        pre = old.split(BEGIN)[0]
        post = old.split(END, 1)[1]
        text = pre + block + post
    with io.open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ---------------------------------------------------------------------------------------
# check: drift (inputs moved) vs disagreement (same inputs, different numbers)
# ---------------------------------------------------------------------------------------
def cmd_check():
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    face = load(OUT)
    ptr = load(TICKET_PTR)
    ticket_path = os.path.join(os.path.dirname(TICKET_PTR), ptr["file"])
    digest = digest_of(input_paths(ticket_path))
    if face.get("inputs_digest") != digest:
        print("STALE inputs moved (face %s, disk %s)"
              % (str(face.get("inputs_digest"))[:12], digest[:12]))
        return 3
    facts, _ = build()
    diffs = [k for k in facts if face.get("facts", {}).get(k) != facts[k]]
    if diffs:
        print("CHECK FAILED fields differ: %s" % ",".join(sorted(diffs)[:6]))
        return 3
    if not os.path.exists(PAGE):
        print("STALE page missing: %s" % PAGE)
        return 3
    with io.open(PAGE, encoding="utf-8") as fh:
        text = fh.read()
    if BEGIN not in text or END not in text:
        print("CHECK FAILED page block missing")
        return 3
    block = text.split(BEGIN, 1)[1].split(END, 1)[0]
    want = render_block(face["facts"]).split(BEGIN, 1)[1].split(END, 1)[0]
    if block.strip() != want.strip():
        print("CHECK FAILED page block differs from the face's own rendering")
        return 3
    print("CHECK OK verdict=%s beta_eq=%.3f%% notional=%.2fx band=%.2fpp"
          % (facts["verdict"], facts["beta_eq_now_pp"], facts["notional_multiple"],
             facts["ruler_band_pp"]))
    return 0


def run():
    facts, ticket_path = build()
    digest = digest_of(input_paths(ticket_path))
    payload = {
        "face": "etf_book_cap_beta_units",
        "artifact": "results/etf_book_cap_beta_units.json",
        "doc": "research/ETF_BOOK_CAP_BETA_UNITS.md",
        "evidence_cutoff": load(TICKET_PTR).get("as_of"),
        "ticket_file": os.path.relpath(ticket_path, REPO).replace("\\", "/"),
        "inputs": [os.path.relpath(p, REPO).replace("\\", "/")
                   for p in input_paths(ticket_path)],
        "inputs_digest": digest,
        "facts": facts,
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    write_doc(facts)
    print("verdict=%s notional=%.2fx beta_eq=%.3f%% over=%+.2fpp band=%.2fpp trim_now=%.0f"
          % (facts["verdict"], facts["notional_multiple"], facts["beta_eq_now_pp"],
             facts["over_pp_now"], facts["ruler_band_pp"], facts["trim_cny_now"]))
    print("WROTE %s" % OUT)
    return 0


# ---------------------------------------------------------------------------------------
# offline selftest
# ---------------------------------------------------------------------------------------
def selftest():
    cases = []

    def leg(name, fn):
        try:
            fn()
            cases.append((name, True, ""))
        except AssertionError as e:
            cases.append((name, False, str(e)))

    def t_units():
        assert abs(beta_units(0.5, 0.4) - 0.2) < 1e-15

    def t_units_zero_beta():
        assert beta_units(0.5, 0.0) == 0.0

    def t_multiple():
        assert abs(multiple(0.44, 0.2) - 2.2) < 1e-12

    def t_multiple_bad_cap():
        try:
            multiple(0.4, 0.0)
        except ValueError:
            return
        raise AssertionError("a zero cap must not divide")

    def t_trim_inside_is_negative():
        assert trim_cny(0.40, 0.48, 0.2, 1e6) < 0

    def t_trim_exact():
        # 0.5 of a beta-0.4 book is 0.2 of the market: exactly on a 20% cap
        assert abs(trim_cny(0.5, 0.4, 0.2, 1e6)) < 1e-9

    def t_trim_roundtrip():
        k, beta, cap, nav = 0.435003, 0.48139415749642345, 0.2, 1e6
        t = trim_cny(k, beta, cap, nav)
        after = (k * nav - t) * beta / nav
        assert abs(after - cap) < 1e-12, after

    def t_trim_scales_with_nav():
        a = trim_cny(0.44, 0.48, 0.2, 1e6)
        b = trim_cny(0.44, 0.48, 0.2, 2e6)
        assert abs(b - 2 * a) < 1e-9

    def t_band():
        assert abs(band_units(0.12, 0.5) - 0.06) < 1e-15

    def t_verdict_inside_noise():
        # 0.94pp over a 20% cap, with a 5.89pp ruler: not resolvable
        assert verdict_of(0.2, 0.2094, 0.0589) == "AT_CAP_WITHIN_RULER_NOISE"

    def t_verdict_over_beyond_noise():
        assert verdict_of(0.2, 0.30, 0.0589) == "OVER_CAP_BEYOND_THE_RULER"

    def t_verdict_under_beyond_noise():
        assert verdict_of(0.2, 0.10, 0.02) == "UNDER_CAP_BEYOND_THE_RULER"

    def t_verdict_zero_band_strict():
        assert verdict_of(0.2, 0.20001, 0.0) == "OVER_CAP_BEYOND_THE_RULER"
        assert verdict_of(0.2, 0.2, 0.0) == "AT_CAP_WITHIN_RULER_NOISE"

    def t_notional_state():
        assert reading_in_notional(0.435003, 0.2)[0] == "ABOVE_CAP"
        assert reading_in_notional(0.10, 0.2)[0] == "INSIDE_CAP"

    def t_rungs_monotone():
        rows = rung_rows(0.2094, 0.4814)
        caps = [r["cap"] for r in rows]
        assert caps == sorted(caps), caps
        assert rows[0]["headroom_pp"] < 0 < rows[-1]["headroom_pp"]

    def t_rungs_leverage_flag():
        rows = {r["rung"]: r for r in rung_rows(0.2094, 0.4814)}
        assert rows["RED"]["needs_leverage"] is False
        assert rows["GREEN"]["needs_leverage"] is True   # 0.8 / 0.48 > 1

    def t_rungs_allow_k_roundtrip():
        for r in rung_rows(0.2, 0.4):
            if r["k_allowed"] is None:
                continue
            assert abs(r["k_allowed"] * 0.4 - r["cap"]) < 1e-9, r

    for n, f in [("beta units multiply", t_units),
                 ("a zero beta implies zero market exposure", t_units_zero_beta),
                 ("multiple divides by the cap", t_multiple),
                 ("a zero cap is refused", t_multiple_bad_cap),
                 ("a book inside the cap trims nothing (negative)", t_trim_inside_is_negative),
                 ("a book exactly at the cap trims exactly zero", t_trim_exact),
                 ("trimming the reported CNY lands beta units on the cap", t_trim_roundtrip),
                 ("trim scales with NAV", t_trim_scales_with_nav),
                 ("the ruler band carries k-noise into beta units", t_band),
                 ("0.94pp over on a 5.89pp ruler is not a breach", t_verdict_inside_noise),
                 ("a real overshoot is named", t_verdict_over_beyond_noise),
                 ("a real undershoot is named", t_verdict_under_beyond_noise),
                 ("a zero band falls back to strict comparison", t_verdict_zero_band_strict),
                 ("notional reading is its own verdict", t_notional_state),
                 ("rungs are monotone around today's exposure", t_rungs_monotone),
                 ("rungs above RED need leverage to be used", t_rungs_leverage_flag),
                 ("each rung's allowed k reproduces its cap", t_rungs_allow_k_roundtrip)]:
        leg(n, f)
    bad = [c for c in cases if not c[1]]
    for n, ok, why in cases:
        print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", n, "" if ok else " | " + why))
    print("%d/%d legs pass" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(selftest())
    if arg == "--check":
        sys.exit(cmd_check())
    sys.exit(run())
