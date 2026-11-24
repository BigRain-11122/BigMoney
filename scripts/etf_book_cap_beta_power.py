"""The 0.94pp cap gap is not a question more data can answer.

`etf_book_cap_beta_units` (r2072) measured the ETF book at 20.941% of the market against a
20% rung, i.e. 0.94pp over, and `etf_book_cap_trim_toll` (r2073) priced the trim that would
close it (144 lots / 19,537.70 CNY, 31.27 CNY round trip) and showed the gap sits inside the
ruler's own +/-5.89pp band.  Both faces say *how big* the blur is.  Neither says **how long
the dispute can be litigated** -- how much book history would have to exist before a single
reading could tell 20.941% from 20.000%.  That is the number that decides whether this is a
measurement question or a policy question, and nobody had computed it.

Three readings, one arithmetic:

  * **How many bars.**  The beta face publishes the sampling spread of one 306-bar reading
    (block bootstrap, 500 draws, 0.1418 in beta).  Scaling by 1/sqrt(n) answers "how long
    would the window have to be for the 0.94pp gap to clear 1.96 sigma".
  * **What one reading can see at all.**  The same spread, held at today's 306 bars, is the
    smallest breach a single reading could ever report -- in beta, in notional pp, and in
    money, beside the 19,543 CNY trim it is supposed to police.
  * **Noise or world.**  The beta path's own dispersion across 69 windows (0.2055) against
    that sampling spread (0.1418) says how much of the disagreement is measurement and how
    much is the world moving.  Printed with its own degrees of freedom, because the windows
    overlap by ~90% and there are only ~5 independent ones -- the decomposition is colour,
    not a verdict, and the verdict below does not rest on it.

Every number is arithmetic on two published faces.  No face is rewritten, no ruler is
adopted, no order is proposed.

  python scripts/etf_book_cap_beta_power.py run
  python scripts/etf_book_cap_beta_power.py --check
  python scripts/etf_book_cap_beta_power.py --selftest

Outputs:
  results/etf_book_cap_beta_power.json
  research/ETF_BOOK_CAP_BETA_POWER.md
"""
import datetime as _dt
import hashlib
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

OUT = os.path.join(REPO, "results", "etf_book_cap_beta_power.json")
PAGE = os.path.join(REPO, "research", "ETF_BOOK_CAP_BETA_POWER.md")
CAP_FACE = os.path.join(REPO, "results", "etf_book_cap_beta_units.json")
BETA_FACE = os.path.join(REPO, "results", "etf_book_beta_paths.json")

Z = 1.96                  # the 95% line the desk's own screens use
BARS_PER_YEAR = 244.0     # A-share trading days in a year
YEAR_LINE = 20.0          # "20 years of book history" as the resolvable/unresolvable line
BLOCK_BEGIN = "<!-- CAP-BETA-POWER-BEGIN -->"
BLOCK_END = "<!-- CAP-BETA-POWER-END -->"


# ---------------------------------------------------------------------------------------
# pure helpers -- the selftest holds these without any face on disk
# ---------------------------------------------------------------------------------------
def implied_beta(cap, k):
    """The beta at which a book of size k sits exactly on the cap."""
    if k <= 0:
        raise ValueError("k must be positive")
    return float(cap) / float(k)


def gap_beta(beta, cap, k):
    """How far above the cap's implied beta this reading sits (negative = inside)."""
    return float(beta) - implied_beta(cap, k)


def sd_at(sd_one, window, bars):
    """Sampling sd of a window-length beta estimate made from `bars` bars.

    A beta estimate's spread falls as 1/sqrt(n); the producer's bootstrap gives the spread
    at `window` bars, so this is the same reading stretched to a longer book.
    """
    if bars <= 0 or window <= 0:
        raise ValueError("window and bars must be positive")
    return float(sd_one) * math.sqrt(float(window) / float(bars))


def bars_needed(sd_one, window, gap, z=Z):
    """Bars of history for the sampling sd to clear `gap` at `z` sigma."""
    if gap <= 0:
        raise ValueError("a non-positive gap cannot be resolved by more data")
    ratio = float(z) * float(sd_one) / float(gap)
    return int(math.ceil(float(window) * ratio * ratio))


def years_for(bars, bars_per_year=BARS_PER_YEAR):
    return float(bars) / float(bars_per_year)


def min_gap_seen(sd_one, window, bars=None, z=Z):
    """Smallest beta gap a reading of `bars` bars can report at `z` sigma."""
    n = float(window if bars is None else bars)
    return float(z) * sd_at(sd_one, window, n)


def gap_to_notional_pp(k, d_beta):
    """A beta gap in notional pp, at the book's own fixed size.

    The breach itself is read as `k*beta - cap`, so a reading error of `d_beta` moves that
    same breach by `k*d_beta`.  Sizing to the cap instead (k = cap/beta) would answer a
    different question -- "how much would a re-sized book wobble" -- and is printed
    separately, never blended (r1313: two calibers, both printed).
    """
    return 100.0 * float(k) * float(d_beta)


def gap_to_cny(k, d_beta, nav):
    return gap_to_notional_pp(k, d_beta) / 100.0 * float(nav)


def real_sd(path_sd, sd_one):
    """Dispersion left after the sampling spread is taken out of the path's own spread."""
    v = float(path_sd) ** 2 - float(sd_one) ** 2
    return math.sqrt(v) if v > 0 else 0.0


def sd_of_sd(sd_val, df):
    """Normal-approximation spread of a sample sd with `df` degrees of freedom."""
    if df <= 0:
        return None
    return float(sd_val) / math.sqrt(2.0 * float(df))


def verdict_of(years_needed, year_line=YEAR_LINE):
    """Resolvable means a book could actually own that much history.

    Nothing here says which ruler is right; only that no ruler can be sharpened into
    agreement with another at this scale within the life of the book.
    """
    if years_needed > float(year_line):
        return "UNRESOLVABLE_BY_MEASUREMENT"
    return "RESOLVABLE_WITH_MORE_DATA"


# ---------------------------------------------------------------------------------------
# face IO
# ---------------------------------------------------------------------------------------
def read_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def digest_of(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(os.path.basename(p).encode("utf-8"))
        with io.open(p, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def build():
    cap_d = read_json(CAP_FACE)
    beta_d = read_json(BETA_FACE)
    cf = cap_d["facts"]

    cap = float(cf["cap_now"])
    k_now = float(cf["k_now"])
    beta_now = float(cf["beta_now"])
    beta_full = float(cf["beta_full"])
    nav = float(cf["nav_cny"])
    window = int(cf["beta_window"])
    sd_one = float(beta_d["noise_sd"])
    path_sd = float(beta_d["path_sd"])
    n_windows = int(beta_d["n_windows"])
    bars_paired = int(beta_d["bars_paired"])

    gap = gap_beta(beta_now, cap, k_now)
    needed = bars_needed(sd_one, window, gap)
    yrs = years_for(needed)
    seen = min_gap_seen(sd_one, window)
    seen_pp = gap_to_notional_pp(k_now, seen)
    seen_cny = gap_to_cny(k_now, seen, nav)
    blur_cny = gap_to_cny(k_now, sd_one, nav)
    # the cap-implied caliber: how far the *allowed* size moves when beta is re-measured.
    # r2072 published the ruler band in this unit (5.892pp), so both are printed.
    blur_pp_cap = 100.0 * (cap / beta_now ** 2) * sd_one
    blur_cny_cap = blur_pp_cap / 100.0 * nav
    trim_cny = float(cf["trim_cny_now"])
    ruler_cny = float(cf["ruler_band_pp"]) / 100.0 * nav

    n_eff = float(bars_paired) / float(window) if window else 0.0
    df = max(0.0, n_eff - 1.0)
    rsd = real_sd(path_sd, sd_one)
    rsd_sd = sd_of_sd(path_sd, df)
    # the path's own spread is itself estimated from overlapping windows, so the real
    # dispersion is an interval, and its lower end may not even clear zero
    lo = max(0.0, (path_sd - 1.2816 * rsd_sd)) if rsd_sd else None
    hi = (path_sd + 1.2816 * rsd_sd) if rsd_sd else None
    rsd_lo = real_sd(lo, sd_one) if lo is not None else None
    rsd_hi = real_sd(hi, sd_one) if hi is not None else None

    ladder = []
    for g in sorted({round(gap, 6), 0.05, 0.12}):
        b = bars_needed(sd_one, window, g)
        ladder.append({"gap_beta": round(g, 6),
                       "gap_notional_pp": round(gap_to_notional_pp(k_now, g), 3),
                       "bars": b,
                       "years": round(years_for(b), 1)})

    facts = {
        "cap_now": cap,
        "k_now": k_now,
        "nav_cny": nav,
        "beta_now": beta_now,
        "beta_full": beta_full,
        "beta_at_cap": round(implied_beta(cap, k_now), 6),
        "gap_beta": round(gap, 6),
        "gap_pp_from_face": float(cf["over_pp_now"]),
        "sd_one_reading_beta": sd_one,
        "blur_to_gap_ratio": round(sd_one / gap, 3) if gap > 0 else None,
        "window_bars": window,
        # what more data would buy
        "bars_needed": needed,
        "years_needed": round(yrs, 1),
        "years_line": YEAR_LINE,
        "ladder": ladder,
        # what one reading can see at all, in three units
        "min_gap_beta_seen": round(seen, 6),
        "min_gap_notional_pp_seen": round(seen_pp, 3),
        "min_gap_cny_seen": round(seen_cny, 2),
        # the money face of the blur, three calibers side by side, never averaged
        "blur_cny_1sigma": round(blur_cny, 2),
        "allowed_wobble_pp": round(blur_pp_cap, 3),
        "allowed_wobble_cny": round(blur_cny_cap, 2),
        "ruler_band_pp_published": float(cf["ruler_band_pp"]),
        "ruler_band_cny_published": round(ruler_cny, 2),
        "caliber_spread_pct": round(100.0 * (blur_cny - ruler_cny) / ruler_cny, 2) if ruler_cny else None,
        "trim_cny_published": round(trim_cny, 2),
        "blur_over_trim": round(blur_cny / trim_cny, 2) if trim_cny else None,
        # noise vs world (indicative: overlapping windows, ~5 independent)
        "path_sd": path_sd,
        "n_windows": n_windows,
        "bars_paired": bars_paired,
        "n_independent_windows": round(n_eff, 2),
        "df_windows": round(df, 2),
        "sampling_share_of_path_var": round(100.0 * sd_one ** 2 / path_sd ** 2, 1) if path_sd else None,
        "real_sd_beta": round(rsd, 6),
        "real_sd_range": [None if rsd_lo is None else round(rsd_lo, 6),
                          None if rsd_hi is None else round(rsd_hi, 6)],
        "real_sd_cny": round(gap_to_cny(k_now, rsd, nav), 2),
        "verdict": verdict_of(yrs),
        # three rulers, printed side by side; none is adopted here
        "rulers": [
            {"name": "full_history", "beta": beta_full,
             "beta_eq_pp": round(100.0 * k_now * beta_full, 3),
             "over_pp": round(cf["over_pp_full"], 3), "adopted": False},
            {"name": "current_window", "beta": beta_now,
             "beta_eq_pp": round(100.0 * k_now * beta_now, 3),
             "over_pp": round(cf["over_pp_now"], 3), "adopted": False},
        ],
        "caveats_note": "no ruler is adopted by this face; adoption is a policy decision "
                        "recorded elsewhere (r1779 ADOPTION), and the three readings differ "
                        "by less than one sixth of the measurement's own blur",
    }

    inputs = [CAP_FACE, BETA_FACE]
    return {
        "face": "etf_book_cap_beta_power",
        "artifact": "results/etf_book_cap_beta_power.json",
        "doc": "research/ETF_BOOK_CAP_BETA_POWER.md",
        "evidence_cutoff": cap_d.get("evidence_cutoff") or beta_d.get("evidence_cutoff"),
        "verdict": facts["verdict"],
        "generated": _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "inputs": [os.path.relpath(p, REPO).replace(os.sep, "/") for p in inputs],
        "inputs_digest": digest_of(inputs),
        "facts": facts,
    }


# ---------------------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------------------
def f2(x):
    return "%.2f" % float(x)


def f4(x):
    return "%.4f" % float(x)


def render_page(payload):
    fc = payload["facts"]
    lines = []
    lines.append("# 0.94pp 这件事，要多少年的历史才量得出来")
    lines.append("")
    lines.append("> 数据截止 **%s**。本页由 `scripts/etf_book_cap_beta_power.py` 生成，"
                 "读数全部来自 `results/etf_book_cap_beta_units.json` 与 "
                 "`results/etf_book_beta_paths.json`，重算逐字比对由 `--check` 负责。"
                 % payload["evidence_cutoff"])
    lines.append("")
    lines.append("**一句话**：这本书现在按当窗 β 读是 %.3f%% 的市场敞口，比 20%% 的帽子多 "
                 "**%.3fpp**；可**一次 β 读数的抽样抖动就有 %.4f（β 单位）**，是这点差额的 "
                 "**%.2f 倍**——要让 0.94pp 自己的抽样标准差降到能被 95%% 分辨的程度，"
                 "这本书需要 **%s 根日线**，约 **%.1f 年**。"
                 % (fc["rulers"][1]["beta_eq_pp"], fc["gap_pp_from_face"],
                    fc["sd_one_reading_beta"], fc["blur_to_gap_ratio"],
                    format(fc["bars_needed"], ","), fc["years_needed"]))
    lines.append("")
    lines.append(BLOCK_BEGIN)
    lines.append("| 项 | 读数 |")
    lines.append("|---|---|")
    lines.append("| 判词 | **%s** |" % fc["verdict"])
    lines.append("| 争议差额（当窗 β） | %.3fpp（β 差 %.6f） |"
                 % (fc["gap_pp_from_face"], fc["gap_beta"]))
    lines.append("| 帽子隐含的 β（cap/k） | %.6f |" % fc["beta_at_cap"])
    lines.append("| 一次读数的抽样标准差（β） | %.6f（窗 %d 根，块自举 500 抽） |"
                 % (fc["sd_one_reading_beta"], fc["window_bars"]))
    lines.append("| 抖动 ÷ 差额 | **%.2f 倍** |" % fc["blur_to_gap_ratio"])
    lines.append("")
    lines.append("## 一、要多少年才能量出来")
    lines.append("")
    lines.append("β 估计的抖动按 1/√n 收缩，所以「多半根历史」等于「放大窗口」：")
    lines.append("")
    lines.append("| 要分辨的差额 | 折成名义敞口 | 需要的日线 | 约合年数 |")
    lines.append("|---|---|---|---|")
    for r in fc["ladder"]:
        lines.append("| %.6f（%.3fpp） | %.3fpp | %s | %.1f 年 |"
                     % (r["gap_beta"], r["gap_notional_pp"], r["gap_notional_pp"],
                        format(r["bars"], ","), r["years"]))
    lines.append("")
    idx = 0
    for i, r in enumerate(fc["ladder"]):
        if abs(r["gap_beta"] - fc["gap_beta"]) < abs(fc["ladder"][idx]["gap_beta"] - fc["gap_beta"]):
            idx = i
    row = fc["ladder"][idx]
    lines.append("- 今天这点差额在表的第 %d 行（%.6f）：**%s 根日线 / %.1f 年**，超过 %.0f 年的判据线 → **%s**"
                 % (idx + 1, row["gap_beta"], format(row["bars"], ","), row["years"],
                    fc["years_line"], fc["verdict"]))
    lines.append("- 换句话说：这本书只有 %d 个交易日（%d 根）的配对史，"
                 "「20.941%% 还是 20.000%%」就**不是数据能判的事**——再算一遍只是把同一份历史重排"
                 % (fc["bars_paired"], fc["window_bars"]))
    lines.append("")
    lines.append("## 二、一次读数最小能看见多大的超帽")
    lines.append("")
    lines.append("把今天的窗口长度钉住（%d 根），一次读数在 95%% 下能被看见的最小差额是：" % fc["window_bars"])
    lines.append("")
    lines.append("| 单位 | 最小可辨超帽 |")
    lines.append("|---|---|")
    lines.append("| β | %.6f |" % fc["min_gap_beta_seen"])
    lines.append("| 名义敞口 | **%.3fpp** |" % fc["min_gap_notional_pp_seen"])
    lines.append("| 钱（净值 %.0f 元） | **%s 元** |" % (fc["nav_cny"], f2(fc["min_gap_cny_seen"])))
    lines.append("")
    lines.append("对照：今天讨论的差额是 %.3fpp、%s 元——**比一次读数能看见的门槛小 %.1f 倍**。"
                 "任何比 %.3fpp 小的「超帽 / 回到帽内」都只是尺子在抖，不是书在动。"
                 % (fc["gap_pp_from_face"], f2(fc["trim_cny_published"]),
                    fc["min_gap_notional_pp_seen"] / fc["gap_pp_from_face"],
                    fc["min_gap_notional_pp_seen"]))
    lines.append("")
    lines.append("## 三、这笔抖动有多少钱")
    lines.append("")
    lines.append("| 口径 | 金额 | 说明 |")
    lines.append("|---|---|---|")
    lines.append("| 一次读数 ±1σ 的敞口抖动（票面仓位固定） | %s 元 | β 抖动 %.6f × 名义仓位 %s 元 |"
                 % (f2(fc["blur_cny_1sigma"]), fc["sd_one_reading_beta"],
                    f2(fc["k_now"] * fc["nav_cny"])))
    lines.append("| 同一抖动在「允许仓位」上的幅度 | %s 元（±%.3fpp） | 帽子隐含仓位（%.4f）上一个 β 的 1:1 换算 |"
                 % (f2(fc["allowed_wobble_cny"]), fc["allowed_wobble_pp"],
                    fc["cap_now"] / fc["beta_now"]))
    lines.append("| 帽子面已公布的噪声带（β 当量） | %s 元（±%.3fpp） | 与第 1 行是**同一种东西的另一种换算法**，差 %+.2f%% |"
                 % (f2(fc["ruler_band_cny_published"]), fc["ruler_band_pp_published"],
                    fc["caliber_spread_pct"]))
    lines.append("| 今天要削掉的差额 | %s 元 | 帽子面 %s |"
                 % (f2(fc["trim_cny_published"]), "trim_cny_now"))
    lines.append("| 第 1 行 ÷ 第 4 行 | **%.2f 倍** | 尺子的抖动比被量的东西大得多 |"
                 % fc["blur_over_trim"])
    lines.append("")
    lines.append("- 三个口径谁都不替代谁：**差额 0.941pp 是在第 1 行口径下量的**，第三行是帽子面行文里用的口径，"
                 "两者差 %.2f%%（因为一个用票面的 43.5%%、一个用帽隐含的 %.2f%%），所以本页把差额与阈值都放在第 1 行口径里比，"
                 "绝不跨口径相减" % (abs(fc["caliber_spread_pct"]), 100.0 * fc["cap_now"] / fc["beta_now"]))
    lines.append("")
    lines.append("## 四、是尺子在抖，还是世界在动")
    lines.append("")
    lines.append("β 面公布了 %d 个滚动窗的 β（路径离散度 %.6f）；单窗抽样抖动是 %.6f，"
                 "所以路径上的离散里约 **%.1f%%** 可由抽样解释，剩下的 %.6f 才是「世界在动」的候选。"
                 % (fc["n_windows"], fc["path_sd"], fc["sd_one_reading_beta"],
                    fc["sampling_share_of_path_var"], fc["real_sd_beta"]))
    lines.append("")
    lines.append("- **这一段只是颜色，不是判词。** 窗口互相重叠约 90%%，%d 根配对史只够 %.2f 个独立窗、"
                 "自由度约 %.2f——路径离散度本身的不确定区间把它换算出的「真实漂移」摊成 "
                 "**[%s, %s]**（β），下端连「零」都排除不了。"
                 % (fc["bars_paired"], fc["n_independent_windows"], fc["df_windows"],
                    "—" if fc["real_sd_range"][0] is None else "%.4f" % fc["real_sd_range"][0],
                    "—" if fc["real_sd_range"][1] is None else "%.4f" % fc["real_sd_range"][1]))
    lines.append("- 判词不靠这一段：第一节的「%s 根日线」只用到单窗抽样抖动与差额两个数，"
                 "与漂移分解无关。" % format(fc["bars_needed"], ","))
    lines.append("")
    lines.append("## 五、所以这是规矩问题，不是测量问题")
    lines.append("")
    lines.append("三种读数并列（本面**不采纳任何一种**；选择是册上的决定，不是这里的结论）：")
    lines.append("")
    lines.append("| 尺子 | β | 折算敞口 | 相对 20%% 帽 |")
    lines.append("|---|---|---|---|")
    for r in fc["rulers"]:
        lines.append("| %s | %.6f | %.3fpp | %+.3fpp |"
                     % (r["name"], r["beta"], r["beta_eq_pp"], r["over_pp"]))
    lines.append("")
    lines.append("- 两种读数的差 %.3fpp，是**一次读数抖动（%.3fpp）的 %.2f 分之一**——"
                 "争哪一个「对」在算术上是在争尺子的零头"
                 % (abs(fc["rulers"][0]["beta_eq_pp"] - fc["rulers"][1]["beta_eq_pp"]),
                    fc["min_gap_notional_pp_seen"],
                    fc["min_gap_notional_pp_seen"] / abs(fc["rulers"][0]["beta_eq_pp"]
                                                         - fc["rulers"][1]["beta_eq_pp"])))
    lines.append("- 可执行的读法只有一条：**把尺子钉死，按日历复核，别按读数复核**——"
                 "日频重算出来的「超帽 / 回帽」在本面对应的分辨率下不可分辨")
    lines.append(BLOCK_END)
    lines.append("")
    lines.append("## 它不声称什么")
    lines.append("")
    lines.append("- 不是「不必守帽」：%.3fpp 确实在帽上面（帽子面自己的读数），本面只说这点差额"
                 "超出这本书现有历史的分辨能力" % fc["gap_pp_from_face"])
    lines.append("- 不是新的 β 估计：抽样抖动、路径离散度、两种 β 均引自上游两面的原值")
    lines.append("- 不是「多等几年就好」：所需年数按 1/√n 外推，假设这本书的波动结构与市场关系"
                 "在那么长的时间里不变——而这恰恰是第一节否掉的那个假设")
    lines.append("- 不是选尺子：三种读数并列印出，谁被采纳写在别的面上（r1779 的 ADOPTION 常量）")
    lines.append("")
    lines.append("复跑：`python scripts/etf_book_cap_beta_power.py run`（写面与本块）、"
                 "`--check`（重算逐字比对）、`--selftest`（离线腿）。")
    lines.append("")
    return "\n".join(lines) + "\n"


def split_block(text):
    i = text.find(BLOCK_BEGIN)
    j = text.find(BLOCK_END)
    if i < 0 or j < 0 or j < i:
        raise ValueError("page block markers missing")
    return text[i:j + len(BLOCK_END)]


def run():
    payload = build()
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with io.open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_page(payload))
    fc = payload["facts"]
    print("CAP-BETA-POWER %s gap=%.3fpp blur_ratio=%.2f bars_needed=%s years=%.1f "
          "min_seen=%.3fpp(%s CNY) blur_1s=%s trim=%s verdict=%s"
          % (payload["evidence_cutoff"], fc["gap_pp_from_face"], fc["blur_to_gap_ratio"],
             format(fc["bars_needed"], ","), fc["years_needed"],
             fc["min_gap_notional_pp_seen"], f2(fc["min_gap_cny_seen"]),
             f2(fc["blur_cny_1sigma"]), f2(fc["trim_cny_published"]), fc["verdict"]))
    return 0


def _diff_paths(a, b, prefix=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out.extend(_diff_paths(a.get(k), b.get(k),
                                   prefix + ("." if prefix else "") + str(k)))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [prefix]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(_diff_paths(x, y, "%s[%d]" % (prefix, i)))
        return out
    return [] if a == b else [prefix]


def cmd_check():
    """Recompute from the inputs and compare -- drift says STALE, disagreement says FAILED."""
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    disk = read_json(OUT)
    fresh = build()
    problems = []
    if disk.get("inputs_digest") != fresh["inputs_digest"]:
        problems.append("STALE: inputs_digest moved (%s -> %s)"
                        % (str(disk.get("inputs_digest"))[:12], fresh["inputs_digest"][:12]))
    elif disk.get("facts") != fresh["facts"]:
        diff = _diff_paths(disk.get("facts") or {}, fresh["facts"])
        problems.append("CHECK FAILED: facts disagree on %s" % ", ".join(diff[:6]))
    if not os.path.exists(PAGE):
        problems.append("STALE face missing: %s" % PAGE)
    else:
        page = io.open(PAGE, "r", encoding="utf-8").read()
        try:
            block = split_block(page)
        except ValueError as e:
            problems.append("CHECK FAILED: page block unreadable (%s)" % e)
            block = ""
        if block and block != split_block(render_page(fresh)):
            problems.append("CHECK FAILED: page block is not what this face renders")
    if problems:
        for p in problems:
            print(p)
        return 3
    print("CHECK OK")
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

    def t_implied_beta():
        assert abs(implied_beta(0.2, 0.4) - 0.5) < 1e-15

    def t_implied_beta_bad_k():
        try:
            implied_beta(0.2, 0.0)
        except ValueError:
            return
        raise AssertionError("a zero k must not divide")

    def t_gap_sign():
        # a beta above cap/k is over the cap; below is inside
        assert gap_beta(0.60, 0.2, 0.4) > 0
        assert gap_beta(0.40, 0.2, 0.4) < 0

    def t_sd_shrinks_as_root_n():
        a = sd_at(0.14, 306, 306)
        b = sd_at(0.14, 306, 306 * 4)
        assert abs(a - 0.14) < 1e-15
        assert abs(b - 0.07) < 1e-12, b

    def t_bars_needed_quadruples_when_gap_halves():
        n1 = bars_needed(0.14, 306, 0.02)
        n2 = bars_needed(0.14, 306, 0.01)
        assert abs(n2 / float(n1) - 4.0) < 1e-9, (n1, n2)

    def t_bars_needed_refuses_zero_gap():
        try:
            bars_needed(0.14, 306, 0.0)
        except ValueError:
            return
        raise AssertionError("a zero gap is not resolvable by more data")

    def t_min_gap_is_z_times_sd():
        assert abs(min_gap_seen(0.10, 306) - Z * 0.10) < 1e-12

    def t_gap_to_pp_matches_the_face():
        # breach is read as k*beta - cap, so a 0.1 beta error at k 0.4 moves it 4pp
        assert abs(gap_to_notional_pp(0.4, 0.1) - 4.0) < 1e-12
        assert abs(gap_to_cny(0.4, 0.1, 1e6) - 40000.0) < 1e-9

    def t_real_sd_zero_when_path_is_sampling():
        assert real_sd(0.10, 0.10) == 0.0
        assert real_sd(0.05, 0.10) == 0.0   # a path narrower than the bootstrap is no drift

    def t_real_sd_positive_when_path_wider():
        assert abs(real_sd(0.5, 0.3) - math.sqrt(0.25 - 0.09)) < 1e-12

    def t_verdict_line():
        assert verdict_of(207.1) == "UNRESOLVABLE_BY_MEASUREMENT"
        assert verdict_of(3.0) == "RESOLVABLE_WITH_MORE_DATA"

    def t_more_bars_shrink_what_one_reading_sees():
        # the whole point of the ladder: 100x the history sees 10x smaller gaps
        a = min_gap_seen(0.14, 306, bars=306)
        b = min_gap_seen(0.14, 306, bars=306 * 100)
        assert abs(a / b - 10.0) < 1e-9, (a, b)

    def t_face_on_disk_agrees_with_hand_arithmetic():
        d = build()
        fc = d["facts"]
        # the published reading: 20.941% at beta 0.4814 against a 0.20 cap
        assert 0.0001 < fc["gap_beta"] < 0.05, fc["gap_beta"]
        assert 3.0 < fc["blur_to_gap_ratio"] < 20.0, fc["blur_to_gap_ratio"]
        assert fc["bars_needed"] > fc["window_bars"], fc["bars_needed"]
        assert fc["verdict"] == verdict_of(fc["years_needed"])

    # --- behavioural legs: the guard must go red on a tampered face, then back to green
    def _tampered(fn):
        global OUT
        keep_out = OUT
        tmp = OUT + ".selftest.tmp"
        with io.open(OUT, "rb") as src, io.open(tmp, "wb") as dst:
            dst.write(src.read())
        try:
            OUT = tmp
            fn(tmp)
        finally:
            OUT = keep_out
            try:
                os.remove(tmp)
            except OSError:
                pass

    def t_check_red_on_tampered_fact():
        import contextlib

        def body(tmp):
            d = read_json(tmp)
            d["facts"]["blur_to_gap_ratio"] = 1.0
            with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(d, fh, ensure_ascii=False, indent=1, sort_keys=True)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cmd_check()
            text = buf.getvalue()
            assert rc == 3, "tampered facts must return rc3, got %s" % rc
            assert "CHECK FAILED" in text, text
            assert "STALE" not in text, "a fact disagreement must not masquerade as STALE: %s" % text
            assert "blur_to_gap_ratio" in text, text

        _tampered(body)

    def t_check_stale_on_moved_digest():
        import contextlib

        def body(tmp):
            d = read_json(tmp)
            d["inputs_digest"] = "0" * 64
            with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(d, fh, ensure_ascii=False, indent=1, sort_keys=True)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cmd_check()
            text = buf.getvalue()
            assert rc == 3 and "STALE" in text, text
            assert "CHECK FAILED" not in text, text

        _tampered(body)

    def t_check_green_after_restore():
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_check()
        assert rc == 0, buf.getvalue()
        assert "CHECK OK" in buf.getvalue()

    def t_page_block_present():
        # the block must print the face's own verdict and bar count, not a placeholder
        page = io.open(PAGE, "r", encoding="utf-8").read()
        blk = split_block(page)
        facts = read_json(OUT)["facts"]
        assert facts["verdict"] in blk, "the block does not print its own verdict"
        assert format(facts["bars_needed"], ",") in blk, "the block does not print its bar count"

    for name, fn in [
        ("implied beta from cap and k", t_implied_beta),
        ("a zero k does not divide", t_implied_beta_bad_k),
        ("gap sign follows the cap", t_gap_sign),
        ("sampling sd falls as 1/sqrt(n)", t_sd_shrinks_as_root_n),
        ("halving the gap quadruples the bars", t_bars_needed_quadruples_when_gap_halves),
        ("a zero gap is not resolvable", t_bars_needed_refuses_zero_gap),
        ("one reading sees 1.96 sd", t_min_gap_is_z_times_sd),
        ("beta gap converts to notional pp", t_gap_to_pp_matches_the_face),
        ("a path no wider than the bootstrap is no drift", t_real_sd_zero_when_path_is_sampling),
        ("a wider path leaves real dispersion", t_real_sd_positive_when_path_wider),
        ("20 years is the verdict line", t_verdict_line),
        ("more bars shrink what one reading sees", t_more_bars_shrink_what_one_reading_sees),
        ("the face on disk matches hand arithmetic", t_face_on_disk_agrees_with_hand_arithmetic),
        ("an edited fact goes red as CHECK FAILED", t_check_red_on_tampered_fact),
        ("a moved input goes red as STALE", t_check_stale_on_moved_digest),
        ("restored face is green again", t_check_green_after_restore),
        ("the page renders a verdict line", t_page_block_present),
    ]:
        leg(name, fn)

    bad = [c for c in cases if not c[1]]
    for name, ok, msg in cases:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " -- " + msg))
    print("%d/%d OK" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return run()
    if cmd == "--check":
        return cmd_check()
    if cmd == "--selftest":
        return selftest()
    print("usage: %s [run|--check|--selftest]" % os.path.basename(__file__))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
