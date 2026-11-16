"""What moved overnight on the money page, and did it have the right to move? (r1761)

`docs/live_book/LIVE-BOOK-<day>.json` is a snapshot of the CEO page: every number the one-pager
prints, with the bar it was priced on. The page is regenerated every day, and nobody diffs it.
So a number can change overnight for three very different reasons and all three look identical
in the morning:

  * the panel advanced -- a new bar, so every priced reading is allowed to move;
  * the clock moved -- "how long since this machine last wrote its heartbeat" must move;
  * the ruler moved -- the producer changed how it computes a number, and the page now prints a
    new value for the same day at the same cut, with no note that the definition changed.

The third one is how a book quietly rewrites its own history. It is also mechanically
detectable: if a number moved while the bar did not, either the page still contains its old
self somewhere (renamed key / changed ruler sentence), or nobody has explained the move.

This face partitions every numeric leaf of the two most recent published day pages:

  SAME CUT?   priced_bar and evidence_cutoff identical on both days -> no new data.
  CLOCK       path contains a declared clock token (age_h, silent_h, lag_days, elapsed...).
  DATA        the cut advanced -> allowed.
  MOVED       cut identical and not a clock face -> the only bucket that needs an answer.
              Then, for each moved number, the page is searched for its own alibi:
                RECOVERED_OLD_VALUE  yesterday's value still exists today under a *new* key
                                     (that is a rename, not a new measurement);
                DECLARED_RULER       the same block's ruler/basis/convention sentence changed;
                UNEXPLAINED          neither -- the page changed a number and said nothing.

It does not judge whether the move was a good idea. It only refuses to let a page change its
numbers silently while claiming to describe the same day.

Usage:
  python scripts/etf_book_day_delta.py run
  python scripts/etf_book_day_delta.py --selftest
  python scripts/etf_book_day_delta.py --check
  python scripts/etf_book_day_delta.py --md
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PAGES = os.path.join(ROOT, "docs", "live_book")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_day_delta.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_DAY_DELTA.md")

SCHEMA = "etf_book_day_delta/v1"
# Faces that are *about* the clock: they are supposed to move overnight at an unchanged cut.
# Frozen here, never inferred from the data (a wildcard would swallow the money buckets too).
CLOCK_TOKENS = ("age_h", "age_days", "silent_h", "silence_h", "owner_silent", "lag_days",
                "lag_hours", "elapsed", "generated", "now_unix", "wall_clock")
# Sentences that declare how a block was measured. A changed one is an alibi for its numbers.
RULER_TOKENS = ("ruler", "basis", "convention", "caliber", "口径", "读法")
# r1793: blocks that quote another lane's face name it in one of these fields. A number that
# still equals the cited file's own reading is a copy, and the copyist is not the author.
CITED_FIELDS = ("source", "cited_from", "quoted_from")
_DIGEST_RE = re.compile(r"^[0-9a-f]{16}$")
REL_TOL = 1e-9
ABS_TOL = 1e-9


# ----------------------------------------------------------------------------- page loading
def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def published_pages(pages_dir=None):
    """The two most recent published day pages, newest first. Never today-vs-today."""
    d = pages_dir or PAGES
    names = []
    if not os.path.isdir(d):
        return names
    for name in os.listdir(d):
        m = re.match(r"^LIVE-BOOK-(\d{8})\.json$", name)
        if m:
            names.append((m.group(1), os.path.join(d, name)))
    names.sort()
    return names


# ----------------------------------------------------------------------------- leaf walking
def numeric_leaves(obj, prefix=""):
    """path -> value for every int/float leaf (bools excluded: True is not a number here)."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(numeric_leaves(v, prefix + "/" + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(numeric_leaves(v, prefix + "/" + str(i)))
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        out[prefix] = obj
    return out


def text_leaves(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(text_leaves(v, prefix + "/" + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(text_leaves(v, prefix + "/" + str(i)))
    elif isinstance(obj, str):
        out[prefix] = obj
    return out


def _close(a, b):
    if a == b:
        return True
    scale = max(abs(float(a)), abs(float(b)))
    return abs(float(a) - float(b)) <= max(ABS_TOL, REL_TOL * scale)


def _clock_face(path):
    low = path.lower()
    return any(tok in low for tok in CLOCK_TOKENS)


def _parent(path):
    return path.rsplit("/", 1)[0] if "/" in path else ""


def _section_key(path):
    """`/derisk/instrument/vt08/top2_min` -> `derisk` (the page key a section is named by)."""
    p = str(path or "").strip("/")
    return p.split("/", 1)[0] if p else ""


def section_bars_of(doc):
    """section key -> the bar that section was priced on (r1532's one implementation).

    Returns None when the producer cannot be read at all: an unreadable guard is not
    permission to call a move explained, so every caller keeps its strict behaviour.
    """
    try:
        import live_book_section_bars as _SB
    except Exception:
        return None
    try:
        return (_SB.section_bars(doc) or {}).get("by_key") or None
    except Exception:
        return None


def _ruler_sentences(texts, parent):
    """Declared-ruler sentences that sit in the block the number came from."""
    out = {}
    for p, v in texts.items():
        if _parent(p) != parent:
            continue
        tail = p.rsplit("/", 1)[-1].lower()
        if any(tok in tail for tok in RULER_TOKENS):
            out[p] = v
    return out


def _section_digests(doc):
    """section key -> the set of 16-hex panel digests that section names anywhere inside it.

    r1793: the family-coherence block reprices "a few arms per cycle", so on any given morning
    some arms are priced on one panel and the rest on another -- the face says so in its own
    `panels` list. When that set changes, the section's numbers are allowed to move *because
    the thing they were priced on changed*, and saying so is not the same as letting a number
    move silently. Only a 16-hex token counts: an 8-hex prefix in prose is a name, not an id.
    """
    out = {}
    for p, v in text_leaves(doc or {}).items():
        k = _section_key(p)
        if not k:
            continue
        for tok in re.split(r"[^0-9a-f]+", v.lower()):
            if _DIGEST_RE.match(tok):
                out.setdefault(k, set()).add(tok)
    return out


def _block_at(doc, parent):
    """The block a leaf sits in, so its own declared source can be read."""
    cur = doc
    for part in [x for x in str(parent or "").split("/") if x]:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur if isinstance(cur, dict) else None


def _cited_value(block):
    """`results/x.json:fresh_pairs` -> the value that file holds there right now (r1793).

    A page that quotes another lane's status face is not the author of that number. If the
    cited file still reads exactly what the page prints, the page is a copyist, and accusing
    it of editing its own history is the wrong finding -- the upstream face moved.
    """
    if not isinstance(block, dict):
        return None, None
    for name in CITED_FIELDS:
        spec = block.get(name)
        if not isinstance(spec, str) or ":" not in spec:
            continue
        rel, _, field = spec.partition(":")
        full = os.path.join(ROOT, rel.strip())
        if not os.path.isfile(full):
            continue
        try:
            with open(full, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError):
            continue
        cur = doc
        for part in field.strip().split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = None
                break
        if isinstance(cur, (int, float)) and not isinstance(cur, bool):
            return cur, spec
    return None, None


# ----------------------------------------------------------------------------- the diff
def _verdict_of(counts, same_cut):
    """One implementation of the precedence, so run() and the selftest cannot disagree."""
    if counts["unexplained"]:
        return "UNEXPLAINED_MOVES"
    if same_cut and (counts["recovered_old_value"] + counts["declared_ruler"]
                     + counts.get("input_identity_changed", 0)
                     + counts.get("quoted_from_source", 0)
                     + counts["section_advanced"]):
        return "EXPLAINED_MOVES"
    if same_cut and counts["moved"] == 0:
        return "CLEAN"
    if not same_cut:
        return "DATA_ADVANCED"
    return "EXPLAINED_MOVES"


def delta(today, prev, sec_a=None, sec_b=None):
    ta, tb = numeric_leaves(today), numeric_leaves(prev)
    xa, xb = text_leaves(today), text_leaves(prev)
    cut_a = (today.get("priced_bar"), today.get("evidence_cutoff"))
    cut_b = (prev.get("priced_bar"), prev.get("evidence_cutoff"))
    same_cut = cut_a == cut_b

    appeared = sorted(p for p in ta if p not in tb)
    vanished = sorted(p for p in tb if p not in ta)
    shared = [p for p in ta if p in tb]
    moved = sorted(p for p in shared if not _close(ta[p], tb[p]))
    dig_a, dig_b = _section_digests(today), _section_digests(prev)

    moves = []
    for p in moved:
        m = {"path": p, "prev": tb[p], "today": ta[p], "delta": ta[p] - tb[p]}
        if _clock_face(p):
            m["kind"] = "CLOCK"
        elif not same_cut:
            m["kind"] = "DATA_ADVANCED"
        else:
            # r1532 the headline bar is not the page's only bar: the 11-16 page carried a
            # derisk section priced on 11-13, so 258 leaves moved "at the same cut" only
            # because the sections were a different generation. Ask the section face which
            # bar each block was priced on before accusing the page of changing its numbers.
            _k = _section_key(p)
            _ba = (sec_a or {}).get(_k)
            _bb = (sec_b or {}).get(_k)
            if _ba and _bb and str(_ba) != str(_bb):
                m["kind"] = "SECTION_ADVANCED"
                m["evidence"] = ("这一节自己换了代：`%s` %s → %s（标题那根 bar 两天相同，这一节不同）"
                                 "；分节 bar 面：results/live_book_section_bars.json"
                                 % (_k, _bb, _ba))
            else:
                old = tb[p]
                _da = dig_a.get(_k) or set()
                _db = dig_b.get(_k) or set()
                _gain = sorted(_da - _db)
                _lost = sorted(_db - _da)
                cited, cited_from = _cited_value(_block_at(today, _parent(p)))
                alibi = None
                if _gain or _lost:
                    m["kind"] = "INPUT_IDENTITY_CHANGED"
                    m["evidence"] = (
                        "这一节的输入身份变了：`%s` 昨天按 %s 定价、今天按 %s 定价"
                        "——数字换的是「拿什么算的」，不是同一根 bar 上的读数"
                        % (_k, "、".join(sorted(_db)) or "（未声明）",
                           "、".join(sorted(_da)) or "（未声明）"))
                elif cited is not None and _close(cited, ta[p]):
                    m["kind"] = "QUOTED_FROM_SOURCE"
                    m["evidence"] = ("这个数不是这页算的：`%s` 现在读 %s，与今天印的 %s 相同"
                                     "——页只是转抄，动的是被引用的那张面"
                                     % (cited_from, cited, ta[p]))
                if m.get("kind") in ("INPUT_IDENTITY_CHANGED", "QUOTED_FROM_SOURCE"):
                    moves.append(m)
                    continue
                for q in appeared:                  # the old number survives under a NEW name
                    if _close(ta[q], old):
                        alibi = q
                        break
                if alibi:
                    m["kind"] = "RECOVERED_OLD_VALUE"
                    m["evidence"] = ("昨天的 %s 今天仍在这页上：`%s`（改名，不是重算）"
                                     % (old, alibi))
                else:
                    par_a = _ruler_sentences(xa, _parent(p))
                    par_b = _ruler_sentences(xb, _parent(p))
                    changed = [k for k in par_a if k in par_b and par_a[k] != par_b[k]]
                    if changed:
                        m["kind"] = "DECLARED_RULER"
                        m["evidence"] = "同块口径句改了：`%s`" % changed[0]
                    else:
                        m["kind"] = "UNEXPLAINED"
                        m["evidence"] = "没有旧值留存，也没有口径声明"
        moves.append(m)

    counts = {
        "leaves_today": len(ta),
        "leaves_prev": len(tb),
        "shared": len(shared),
        "identical": len(shared) - len(moved),
        "moved": len(moved),
        "clock": sum(1 for m in moves if m["kind"] == "CLOCK"),
        "data_advanced": sum(1 for m in moves if m["kind"] == "DATA_ADVANCED"),
        "recovered_old_value": sum(1 for m in moves if m["kind"] == "RECOVERED_OLD_VALUE"),
        "declared_ruler": sum(1 for m in moves if m["kind"] == "DECLARED_RULER"),
        "input_identity_changed": sum(1 for m in moves
                                     if m["kind"] == "INPUT_IDENTITY_CHANGED"),
        "quoted_from_source": sum(1 for m in moves if m["kind"] == "QUOTED_FROM_SOURCE"),
        "section_advanced": sum(1 for m in moves if m["kind"] == "SECTION_ADVANCED"),
        "unexplained": sum(1 for m in moves if m["kind"] == "UNEXPLAINED"),
        "appeared": len(appeared),
        "vanished": len(vanished),
    }
    if counts["unexplained"]:
        verdict = "UNEXPLAINED_MOVES"
    elif same_cut and (counts["recovered_old_value"] + counts["declared_ruler"]
                       + counts["input_identity_changed"] + counts["quoted_from_source"]
                       + counts["section_advanced"]):
        verdict = "EXPLAINED_MOVES"
    elif same_cut and counts["moved"] == 0:
        verdict = "CLEAN"
    elif not same_cut:
        verdict = "DATA_ADVANCED"
    else:
        verdict = "EXPLAINED_MOVES"
    assert verdict == _verdict_of(counts, same_cut), "two implementations of the precedence"

    money_leaves = [m for m in moves if m["kind"] in ("RECOVERED_OLD_VALUE", "DECLARED_RULER",
                                                      "INPUT_IDENTITY_CHANGED",
                                                      "QUOTED_FROM_SOURCE",
                                                      "SECTION_ADVANCED", "UNEXPLAINED")]
    blocks = sorted({"/".join(p.split("/")[:3]) for p in appeared})
    return {
        "same_cut": same_cut,
        "verdict": verdict,
        "cut_today": {"priced_bar": cut_a[0], "evidence_cutoff": cut_a[1]},
        "cut_prev": {"priced_bar": cut_b[0], "evidence_cutoff": cut_b[1]},
        "counts": counts,
        "moves": moves,
        "money_moves": money_leaves,
        "appeared_blocks": blocks,
        "appeared_paths": appeared[:40],
        "vanished_paths": vanished[:40],
    }


def run(pages_dir=None):
    names = published_pages(pages_dir)
    if len(names) < 2:
        return {"schema": SCHEMA, "verdict": "NO_SECOND_PAGE", "note":
                "只有一张已发布日页：没有第二个可比的快照，本面拒绝编造隔夜差"}
    (day_a, path_a), (day_b, path_b) = names[-1], names[-2]
    today, prev = _load(path_a), _load(path_b)
    # r1793: the headline bar is not the page's only bar (r1532). Hand the diff each
    # section's own bar so a section that changed generation is named as such instead of
    # being reported as a page that moved 258 numbers at an unchanged cut.
    sec_a = section_bars_of(today)
    sec_b = section_bars_of(prev)
    d = delta(today, prev, sec_a=sec_a, sec_b=sec_b)
    payload = {
        "schema": SCHEMA,
        "today": {"day": day_a, "file": os.path.basename(path_a),
                  "priced_bar": today.get("priced_bar"),
                  "evidence_cutoff": today.get("evidence_cutoff")},
        "prev": {"day": day_b, "file": os.path.basename(path_b),
                 "priced_bar": prev.get("priced_bar"),
                 "evidence_cutoff": prev.get("evidence_cutoff")},
        "section_bars_read": bool(sec_a and sec_b),
        "section_bars_ref": "results/live_book_section_bars.json",
        "evidence_cutoff": today.get("evidence_cutoff"),
    }
    payload.update(d)
    payload["verdict"] = (
        "UNEXPLAINED_MOVES" if d["counts"]["unexplained"] else
        ("CLEAN" if d["same_cut"] and d["counts"]["moved"] == 0 else
         ("DATA_ADVANCED" if not d["same_cut"] else "EXPLAINED_MOVES")))
    return payload


# ----------------------------------------------------------------------------- md
def write_md(p):
    lines = ["# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）", ""]
    if p.get("verdict") == "NO_SECOND_PAGE":
        lines += ["- 只有一张已发布日页，没有可比的隔夜快照：本面不产出任何位移判读。"]
        _write(OUT_MD, lines)
        return
    c = p["counts"]
    lines += [
        "- 比较：`%s` → `%s`" % (p["prev"]["file"], p["today"]["file"]),
        "- 价格依据：%s（前一天 %s）｜数据截止：%s（前一天 %s）"
        % (p["cut_today"]["priced_bar"], p["cut_prev"]["priced_bar"],
           p["cut_today"]["evidence_cutoff"], p["cut_prev"]["evidence_cutoff"]),
        "- 判决：**%s**" % p["verdict"],
        "",
        "## 一句话",
    ]
    if p["same_cut"]:
        _expl = (c["recovered_old_value"] + c["declared_ruler"] + c["section_advanced"]
                 + c.get("input_identity_changed", 0) + c.get("quoted_from_source", 0))
        lines.append(
            "两天**是同一根 bar**（没有新数据进来），这页有 **%d** 个数变了；其中 **%d** 个是钟面"
            "（机器多久没说话之类，本来就该走）、**%d** 个能给出解释（旧数还在页上／口径句改了／"
            "这一节换了代／这一节换了定价的输入／这个数只是转抄别面）、**%d** 个没解释。"
            "新增 **%d** 个数字叶子、消失 **%d** 个。"
            % (c["moved"], c["clock"], _expl, c["unexplained"], c["appeared"], c["vanished"]))
    else:
        lines.append(
            "两天**不是同一根 bar**（%s → %s），数据推进了，先分不清“数据动”和“口径动”；"
            "这一面在数据日推进的隔夜不给任何指控，只记录 **%d** 个位移与 **%d** 个新增叶子。"
            % (p["cut_prev"]["priced_bar"], p["cut_today"]["priced_bar"],
               c["moved"], c["appeared"]))

    lines += ["", "## 动的数（全部 %d 个）" % c["moved"], "",
              "| 数字 | 昨天 | 今天 | 判读 | 依据 |", "|---|---|---|---|---|"]
    for m in p["moves"]:
        lines.append("| `%s` | %s | %s | %s | %s |"
                     % (m["path"], m["prev"], m["today"], m["kind"], m.get("evidence", "")))
    if not p["moves"]:
        lines.append("| — | — | — | — | 一个都没动 |")

    if p.get("vanished_paths"):
        lines += ["", "## 今天没有了的数（%d 个，列前 40）" % c["vanished"], ""]
        lines += ["- `%s`" % v for v in p["vanished_paths"]]
    if p.get("appeared_blocks"):
        lines += ["", "## 今天新出现的数（%d 个）落在这几块上" % c["appeared"], ""]
        lines += ["- `%s`" % b for b in p["appeared_blocks"][:20]]

    if p["money_moves"]:
        lines += ["", "## 钱的两处（同一根 bar 上改了定价口径）", ""]
        for m in p["money_moves"]:
            lines.append("- `%s`：**%s → %s**（差 %s）｜%s｜%s"
                         % (m["path"], m["prev"], m["today"],
                            round(m["delta"], 6), m["kind"], m.get("evidence", "")))
        lines += ["",
                  "同一个隔夜、同一根 bar、同一笔钱，这页昨天给一个答案、今天给另一个。"
                  "两个答案不可能都对：走 `RECOVERED_OLD_VALUE`／`DECLARED_RULER` 的那一条说明"
                  "**是新答案改了算法**（旧数还在页上或口径句改了），读的人要按新口径重读昨天的判断；"
                  "没有这两条说明的，就是这页偷偷换了数。"]

    un = [m for m in p["moves"] if m["kind"] == "UNEXPLAINED"]
    if un:
        cnt = {}
        for m in un:
            cnt[_section_key(m["path"])] = cnt.get(_section_key(m["path"]), 0) + 1
        lines += ["", "## 还有哪些节在同 bar 上改了数（%d 个）" % len(un), ""]
        for k in sorted(cnt, key=lambda x: (-cnt[x], x)):
            lines.append("- `%s`：%d 个" % (k, cnt[k]))
        lines += ["",
                  "这几节的位移**没有任何解释**（不是转抄、不是换输入、不是换代）。"
                  "页要在同一根 bar 上改这些数，就得自己写出理由；写不出来，读的人就分不清"
                  "「今天变了」和「口径变了」。"]

    lines += ["", "## 怎么读", "",
              "- `CLOCK`＝钟面（`age_h`/`silent_h`/`lag_days` 这类）：没有新 bar 也该走，不构成问题；"
              "但它的存在说明「哪些数允许自己走」是**名单制**的，名单写在本脚本顶部，不由数据推出来。",
              "- `DATA_ADVANCED`＝数据推进了，所有定价读数都允许动。",
              "- `RECOVERED_OLD_VALUE`＝昨天那个数今天还在页上，只是换了名字——那是**改名**不是重算；"
              "读的人必须知道这一点，否则会把「口径换了」读成「今天变了」。",
              "- `DECLARED_RULER`＝同一块里的口径句（`ruler`/`basis`/`convention`）改了，"
              "位移由它自己声明；句子改了而读者没看见，等于数被悄悄换了定义。",
              "- `SECTION_ADVANCED`＝这一**节**自己换了代（标题那根 bar 两天相同，这一节不同，"
              "按 `results/live_book_section_bars.json` 判）：不是同 bar 重算漂移，而是页面里"
              "混着两代数据（页面本身另有 `PAGE_MIXES_BARS` 面在报）。",
              "- `INPUT_IDENTITY_CHANGED`＝这一节**拿什么算**变了：它在自己身上写下的面板指纹"
              "（16 位十六进制）两天不同。族面是按「几个臂已重算」分批定价的，换一批臂，"
              "同一根 bar 上这一节的数就会动——这是它自己的输入变了，不是它在同一天改了口径。"
              "本档与 `DECLARED_RULER` 同一弱点：它信的是这一节自己的宣告，不独立复算。",
              "- `QUOTED_FROM_SOURCE`＝这个数不是这页算的：它的块里写着 `source`（如"
              "`results/x.json:fresh_pairs`），而那个文件**现在**读到的值正好等于今天印的值。"
              "页只是转抄，动的是被引用的那张面（另一条车道）；写这张面的人不是改数的人。",
              "- `UNEXPLAINED`＝既没有旧值留存、也没有口径声明——**这一档非零就是本面要报的事**。",
              "", "## 未验证（如实）", "",
              "- 只比**相邻两天**：更早的口径变更若在两页之前发生，本面看不见（可手工指定更多日页，未做）。",
              "- 「旧值仍在」靠数值相等判定（相对 1e-9）：两个无关的数恰好相等的概率不低，"
              "所以 `RECOVERED_OLD_VALUE` 是**线索**不是证明，行里同时印出它在哪个键上，供人核。",
              "- 钟面名单是写死的：新出现的钟面字段会被算成 `MOVED`，本面会如实报（宁可多报）。",
              "- 本面不判「这个改动是否合理」，也不碰任何生产件；它只读已发布日页。"]
    _write(OUT_MD, lines)


def _write(path, lines):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ----------------------------------------------------------------------------- selftest
def _page(bar, gap, ruler, age, extra=None):
    p = {"priced_bar": bar, "evidence_cutoff": bar,
         "cash_money": {"forward": {"gap_bp": gap, "ruler": ruler}},
         "fleet": {"rows": [{"age_h": age}]}}
    if extra:
        p["cash_money"]["forward"].update(extra)
    return p


def selftest():
    fails = [0]
    total = [0]

    def check(name, cond, got=""):
        total[0] += 1
        if cond:
            print("  OK   %s" % name)
        else:
            fails[0] += 1
            print("  FAIL %s  %s" % (name, got))

    # L1 identical pages -> nothing moved
    p = _page("2026-11-13", 50.81, "rate only", 40.5)
    d = delta(p, json.loads(json.dumps(p)))
    check("L1 same page: zero moves", d["counts"]["moved"] == 0, d["counts"])
    check("L1 verdict CLEAN", (d["counts"]["unexplained"] == 0 and d["same_cut"]) is True)

    # L2 money number moves at the same cut, no alibi -> UNEXPLAINED
    a = _page("2026-11-13", 77.79, "rate only", 41.4)
    b = _page("2026-11-13", 50.81, "rate only", 40.5)
    d = delta(a, b)
    kinds = {m["path"]: m["kind"] for m in d["moves"]}
    check("L2 money move flagged", kinds.get("/cash_money/forward/gap_bp") == "UNEXPLAINED", kinds)
    check("L2 clock face exempt", kinds.get("/fleet/rows/0/age_h") == "CLOCK", kinds)
    check("L2 unexplained counted", d["counts"]["unexplained"] == 1, d["counts"])

    # L3 old value survives under a new key -> RECOVERED, not an accusation
    a = _page("2026-11-13", 77.79, "rate only", 41.4, {"gap_bp_gross": 50.81})
    d = delta(a, b)
    m = [x for x in d["moves"] if x["path"] == "/cash_money/forward/gap_bp"][0]
    check("L3 rename recognised", m["kind"] == "RECOVERED_OLD_VALUE", m)
    check("L3 alibi names the new key", "gap_bp_gross" in (m.get("evidence") or ""), m)
    check("L3 nothing unexplained", d["counts"]["unexplained"] == 0, d["counts"])

    # L4 ruler sentence changed in the same block -> DECLARED
    a = _page("2026-11-13", 77.79, "rate only, net of per-roll commission", 41.4)
    d = delta(a, b)
    m = [x for x in d["moves"] if x["path"] == "/cash_money/forward/gap_bp"][0]
    check("L4 declared ruler recognised", m["kind"] == "DECLARED_RULER", m)

    # L5 new bar -> priced readings are allowed to move, the clock face keeps its own label
    a = _page("2026-11-16", 77.79, "rate only", 41.4)
    b = _page("2026-11-13", 50.81, "rate only", 40.5)
    d = delta(a, b)
    kinds = {m["path"]: m["kind"] for m in d["moves"]}
    check("L5 cut advanced bucket",
          kinds.get("/cash_money/forward/gap_bp") == "DATA_ADVANCED", kinds)
    check("L5 clock still named clock", kinds.get("/fleet/rows/0/age_h") == "CLOCK", kinds)
    check("L5 nothing accused on a data day", d["counts"]["unexplained"] == 0, d["counts"])
    check("L5 same_cut false", d["same_cut"] is False)

    # L6 tolerance: float noise below 1e-9 relative is not a move
    a = _page("2026-11-13", 50.8100000000001, "rate only", 40.5)
    d = delta(a, b)
    check("L6 float noise ignored", d["counts"]["moved"] == 0, d["counts"])

    # L7 int/float same value is not a move; bool is not a number
    a = {"x": 5.0, "flag": True, "y": 1}
    b = {"x": 5, "flag": False, "y": 1.0}
    d = delta(a, b)
    check("L7 int==float and bool excluded", d["counts"]["moved"] == 0, d["moves"])

    # L8 vanished key is reported (history dropped, not a move)
    a = {"keep": 1.0}
    b = {"keep": 1.0, "gone": 42.0}
    d = delta(a, b)
    check("L8 vanished reported", d["counts"]["vanished"] == 1, d["counts"])
    check("L8 vanished not a move", d["counts"]["moved"] == 0, d["counts"])

    # L9 appeared key with no move is counted separately
    a = {"keep": 1.0, "new": 7.0}
    b = {"keep": 1.0}
    d = delta(a, b)
    check("L9 appeared counted", d["counts"]["appeared"] == 1 and d["counts"]["moved"] == 0, d["counts"])

    # L10 verdict precedence: one unexplained beats any number of explained moves
    a = _page("2026-11-13", 77.79, "new ruler", 41.4, {"gap_bp_gross": 50.81})
    b = _page("2026-11-13", 50.81, "rate only", 40.5)
    a["other"] = {"note_num": 9.0}
    b["other"] = {"note_num": 3.0}
    d = delta(a, b)
    check("L10 unexplained dominates", d["counts"]["unexplained"] == 1 and
          d["counts"]["recovered_old_value"] + d["counts"]["declared_ruler"] >= 1, d["counts"])

    # L11 clock token must not swallow money paths that merely contain similar words
    a = {"cash": {"cagr_pct": 9.12}, "fleet": {"age_h": 40.0}}
    b = {"cash": {"cagr_pct": 8.0}, "fleet": {"age_h": 30.0}}
    d = delta(a, b)
    kinds = {m["path"]: m["kind"] for m in d["moves"]}
    check("L11 money path not treated as clock", kinds.get("/cash/cagr_pct") == "UNEXPLAINED", kinds)

    # L12 no second page -> refuse to invent a delta
    r = run(pages_dir=os.path.join(ROOT, "results", "_selftest_no_such_dir"))
    check("L12 single page refused", r.get("verdict") == "NO_SECOND_PAGE", r.get("verdict"))

    # L13 a section that changed generation explains its own leaves (r1793)
    a = {"priced_bar": "2026-11-16", "derisk": {"x": 2.0}}
    b = {"priced_bar": "2026-11-16", "derisk": {"x": 1.0}}
    d = delta(a, b, sec_a={"derisk": "2026-11-16"}, sec_b={"derisk": "2026-11-13"})
    kinds = {m["path"]: m["kind"] for m in d["moves"]}
    check("L13 section generation named",
          kinds.get("/derisk/x") == "SECTION_ADVANCED", kinds)
    check("L13 not an accusation", d["counts"]["unexplained"] == 0, d["counts"])
    check("L13 verdict explained", d["verdict"] == "EXPLAINED_MOVES", d["verdict"])

    # L14 same section bar on both days -> the move stays unexplained (the guard must bite)
    d = delta(a, b, sec_a={"derisk": "2026-11-16"}, sec_b={"derisk": "2026-11-16"})
    check("L14 same-section move still accused",
          d["counts"]["unexplained"] == 1, d["counts"])

    # L15 an unreadable section face is not permission: old strict behaviour survives
    d = delta(a, b, sec_a=None, sec_b=None)
    check("L15 no section face -> still accused",
          d["counts"]["unexplained"] == 1, d["counts"])

    # L16 r1793: the section's own declared world-set changed -> its numbers may move
    a = {"priced_bar": "2026-11-16",
         "family_coherence": {"panels": ["0988c6530a481fa1", "e6f9d0e81a64ec75"],
                              "verdict": "MIXED_WORLDS", "gap_pp": 2.0}}
    b = {"priced_bar": "2026-11-16",
         "family_coherence": {"panels": ["0988c6530a481fa1"],
                              "verdict": "ONE_WORLD", "gap_pp": 1.0}}
    d = delta(a, b)
    k = {m["path"]: m["kind"] for m in d["moves"]}
    check("L16 input identity change recognised",
          k.get("/family_coherence/gap_pp") == "INPUT_IDENTITY_CHANGED", k)
    check("L16 alibi names both digests",
          ("e6f9d0e81a64ec75" in (d["moves"][0].get("evidence") or "")
           and "0988c6530a481fa1" in (d["moves"][0].get("evidence") or "")), d["moves"])
    check("L16 nothing unexplained", d["counts"]["unexplained"] == 0, d["counts"])

    # L17 same world-set on both days -> the move is still an accusation (the guard must bite)
    a2 = json.loads(json.dumps(a))
    a2["family_coherence"]["panels"] = ["0988c6530a481fa1"]
    d = delta(a2, b)
    check("L17 same world-set -> still accused",
          d["counts"]["unexplained"] == 1, d["counts"])

    # L18 r1793: a number copied from a cited face is not this page's to explain
    cited = os.path.join(ROOT, "results", "_selftest_cited_day_delta.json")
    try:
        with open(cited, "w", encoding="utf-8") as fh:
            json.dump({"fresh_pairs": 185}, fh)
        a3 = {"priced_bar": "2026-11-16",
              "roster": {"rows": [{"laneside": {"value": 185,
                                                "source": "results/_selftest_cited_day_delta.json:fresh_pairs"}}]}}
        b3 = {"priced_bar": "2026-11-16",
              "roster": {"rows": [{"laneside": {"value": 187,
                                                "source": "results/_selftest_cited_day_delta.json:fresh_pairs"}}]}}
        d = delta(a3, b3)
        check("L18 quoted value recognised",
              d["moves"][0]["kind"] == "QUOTED_FROM_SOURCE", d["moves"])
        check("L18 nothing unexplained", d["counts"]["unexplained"] == 0, d["counts"])
        # L18b the cited face no longer says what the page prints -> back to an accusation
        with open(cited, "w", encoding="utf-8") as fh:
            json.dump({"fresh_pairs": 99}, fh)
        d = delta(a3, b3)
        check("L18b cited face disagrees -> accused",
              d["counts"]["unexplained"] == 1, d["counts"])
    finally:
        try:
            os.remove(cited)
        except OSError:
            pass

    print("selftest %d/%d %s" % (total[0] - fails[0], total[0], "PASS" if not fails[0] else "FAIL"))
    return 0 if not fails[0] else 1


# ----------------------------------------------------------------------------- check
def check_published():
    """Re-derive from disk and compare with the published payload, number for number."""
    published = _load(OUT_JSON)
    fresh = run()
    bad = []
    for k in ("verdict", "same_cut"):
        if published.get(k) != fresh.get(k):
            bad.append(k)
    for k, v in fresh["counts"].items():
        if published["counts"].get(k) != v:
            bad.append("counts.%s" % k)
    if len(published.get("moves") or []) != len(fresh["moves"]):
        bad.append("moves.len")
    if bad:
        print("check FAIL: %s" % ", ".join(bad))
        return 1
    print("check OK: verdict=%s moved=%d unexplained=%d (re-derived from the published pages)"
          % (fresh["verdict"], fresh["counts"]["moved"], fresh["counts"]["unexplained"]))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check_published()
    payload = run()
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)
    if payload.get("verdict") == "NO_SECOND_PAGE":
        print("NO_SECOND_PAGE %s" % payload.get("note"))
        return 0
    c = payload["counts"]
    print("%s moved=%d clock=%d explained=%d unexplained=%d appeared=%d vanished=%d"
          % (payload["verdict"], c["moved"], c["clock"],
             c["recovered_old_value"] + c["declared_ruler"], c["unexplained"],
             c["appeared"], c["vanished"]))
    for m in payload["moves"]:
        print("  %-22s %s  %s -> %s  %s"
              % (m["kind"], m["path"], m["prev"], m["today"], m.get("evidence", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
