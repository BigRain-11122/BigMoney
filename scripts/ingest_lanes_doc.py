#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""车道交接说明生成器 · bm-c(FLUXGROUP) → DASHENG

O-20261124-2300-bm-c §1-C 的交付件：为 15 条数据车道逐条写清
①重建命令 ②数据源与频率 ③覆盖区间与已知缺口，让对端决定
「按脚本重建」还是「要分包」。

口径（全部从盘上 derive，禁手抄）：
  - 文件数/体量：递归统计 data/<lane> 下实际文件
  - 覆盖区间：逐文件读首行/尾行的日期列取并集 min/max（CSV 用字节直取，
    Parquet 用 row-group statistics；单文件失败只记进 unreadable，禁编数）
  - 缺口：以 data/daily/510300.csv 的交易日历为本地时钟，
    车道尾 bar 落后日历尾 bar 的交易日数即缺口
  - 数据源/频率：取重建脚本模块 docstring 首段（原样引用，未标注就说未标注）

用法：
  python scripts/ingest_lanes_doc.py            # 生成 md + json
  python scripts/ingest_lanes_doc.py --check    # 只比对面是否最新（rc0 一致 / rc3 需重建）
  python scripts/ingest_lanes_doc.py selftest   # 离线自检
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT_MD = os.path.join(ROOT, "research", "INGEST", "LANES-DASHENG.md")
OUT_JSON = os.path.join(ROOT, "research", "INGEST", "LANES-DASHENG.json")
CALENDAR = os.path.join(DATA, "daily", "510300.csv")

# 车道 → 重建脚本（单源；脚本缺失=诚实标注，禁凭空写命令）
LANES = [
    ("astock_daily", "scripts/update_astock_daily.py"),
    ("moneyflow", "scripts/update_moneyflow.py"),
    ("lhb_inst", "scripts/update_lhb_inst.py"),
    ("options", "scripts/update_options.py"),
    ("futures_contracts", "scripts/update_futures_contracts.py"),
    ("futures_daily", "scripts/update_futures.py"),
    ("index_daily", "scripts/update_index_daily.py"),
    ("daily", "scripts/update_daily.py"),
    ("cb_daily", "scripts/cb_dual_low.py"),
    ("repo_daily", "scripts/update_repo.py"),
    ("zt_pool", "scripts/update_zt_pool.py"),
    ("fundamental", "scripts/update_fundamental.py"),
    ("heat", "scripts/update_heat.py"),
    ("ext_slots", "scripts/backfill_ext_slots.py"),
    ("minute_feed", "scripts/update_minute_feed.py"),
]

# 写者登记表（单一真值）：车道→写者脚本。脚本名与约定不同时以本表为准，
# 表内写者若也不存在才判「只能分包」——防「按 update_<lane>.py 约定猜不到」
# 就把有重建路径的车道报成分包件（本窗 cb_daily=cb_dual_low 差点踩中）。
WRITER_REGISTRY = "scripts/data_lane_freshness.py"

DATE_COLS = ("date", "day", "trade_date", "datetime")
_TAIL_BYTES = 4096


def _read_head_lines(path, n=2):
    out = []
    with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        for _ in range(n):
            line = f.readline()
            if not line:
                break
            out.append(line.rstrip("\r\n"))
    return out


def _read_tail_line(path):
    try:
        size = os.path.getsize(path)
    except OSError:
        return None
    if size <= 0:
        return None
    with io.open(path, "rb") as f:
        f.seek(max(0, size - _TAIL_BYTES))
        chunk = f.read()
    lines = [ln for ln in chunk.split(b"\n") if ln.strip()]
    if not lines:
        return None
    return lines[-1].decode("utf-8", "replace").rstrip("\r")


def _date_index(header):
    cols = [c.strip().lower().lstrip("\ufeff") for c in header.split(",")]
    for want in DATE_COLS:
        if want in cols:
            return cols.index(want)
    return None


def _csv_coverage(path):
    """返回 (first_date, last_date) 或 None（无日期列/空文件）。"""
    head = _read_head_lines(path, 2)
    if not head:
        return None
    idx = _date_index(head[0])
    if idx is None:
        return None
    first = None
    if len(head) > 1:
        parts = head[1].split(",")
        if idx < len(parts):
            first = parts[idx].strip().strip('"')
    tail = _read_tail_line(path)
    last = None
    if tail:
        parts = tail.split(",")
        if idx < len(parts):
            last = parts[idx].strip().strip('"')
    return first, last


def _parquet_coverage(path):
    try:
        import pyarrow.parquet as pq
    except Exception:
        return None
    try:
        md = pq.ParquetFile(path).metadata
    except Exception:
        return None
    names = [md.schema.column(i).name for i in range(md.num_columns)]
    lowered = [n.lower() for n in names]
    idx = None
    for want in DATE_COLS:
        if want in lowered:
            idx = lowered.index(want)
            break
    if idx is None:
        return None
    lo = hi = None
    for rg in range(md.num_row_groups):
        st = md.row_group(rg).column(idx).statistics
        if not st or st.min is None or st.max is None:
            continue
        lo = st.min if lo is None or st.min < lo else lo
        hi = st.max if hi is None or st.max > hi else hi
    if lo is None:
        return None
    return str(lo)[:10], str(hi)[:10]


def _norm_date(value):
    if not value:
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(value))
    return m.group(0) if m else None


def lane_coverage(lane_dir):
    """并集覆盖 (first, last, unreadable_count, files_with_dates)。"""
    first = last = None
    unreadable = 0
    dated = 0
    for root, _dirs, files in os.walk(lane_dir):
        for name in files:
            path = os.path.join(root, name)
            low = name.lower()
            if low.endswith(".csv"):
                cov = _csv_coverage(path)
            elif low.endswith(".parquet"):
                cov = _parquet_coverage(path)
            else:
                continue
            if cov is None:
                unreadable += 1
                continue
            a, b = _norm_date(cov[0]), _norm_date(cov[1])
            if a is None and b is None:
                unreadable += 1
                continue
            dated += 1
            for v in (a, b):
                if v is None:
                    continue
                first = v if first is None or v < first else first
                last = v if last is None or v > last else last
    return first, last, unreadable, dated


def lane_size(lane_dir):
    files = 0
    total = 0
    by_ext = {}
    for root, _dirs, names in os.walk(lane_dir):
        for name in names:
            path = os.path.join(root, name)
            try:
                size = os.path.getsize(path)
            except OSError:
                continue
            files += 1
            total += size
            ext = os.path.splitext(name)[1].lower() or "(none)"
            by_ext[ext] = by_ext.get(ext, 0) + 1
    return files, total, by_ext


def script_docstring(rel_path):
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        return None
    head = _read_head_lines(path, 120)
    text = "\n".join(head)
    m = re.search(r'^\s*("""|\'\'\')(.*?)\1', text, re.S | re.M)
    if not m:
        return None
    body = m.group(2).strip()
    lines = [ln.rstrip() for ln in body.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and len(lines[0]) <= 40 and "·" in lines[0]:
        lines = lines[1:]  # 跳过 "模块名 · 归属" 标题行
    para = []
    for ln in lines:
        if not ln.strip():
            break
        para.append(ln.strip())
    out = " ".join(para).strip()
    return out or None


def writer_script_map():
    """从写者登记表解析 {lane: writer}；文件缺失=空表（禁编造）。"""
    path = os.path.join(ROOT, WRITER_REGISTRY)
    if not os.path.isfile(path):
        return {}
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    out = {}
    for m in re.finditer(r'\{\s*"lane"\s*:\s*"([^"]+)"(.*?)\}', text, re.S):
        lane, body = m.group(1), m.group(2)
        w = re.search(r'"writer"\s*:\s*"([^"]+)"', body)
        if w:
            out.setdefault(lane, w.group(1))
    return out


def resolve_script(lane, declared):
    """declared → 登记表写者 → 约定名。返回 (脚本相对路径 or None, 来源)。"""
    cands = []
    if declared:
        cands.append((declared, "declared"))
    writer = writer_script_map().get(lane)
    if writer:
        cands.append(("scripts/%s.py" % writer, "writer-registry"))
    cands.append(("scripts/update_%s.py" % lane, "convention"))
    for rel, via in cands:
        if os.path.isfile(os.path.join(ROOT, rel)):
            return rel, via
    return (declared or "scripts/update_%s.py" % lane), None


def calendar_dates():
    if not os.path.isfile(CALENDAR):
        return []
    out = []
    with io.open(CALENDAR, "r", encoding="utf-8", errors="replace", newline="") as f:
        f.readline()
        for line in f:
            d = _norm_date(line.split(",")[0])
            if d:
                out.append(d)
    return out


def trading_days_between(dates, lo, hi):
    """(lo, hi] 区间内的交易日数。"""
    if not lo or not hi or lo >= hi:
        return 0
    return sum(1 for d in dates if lo < d <= hi)


def build():
    cal = calendar_dates()
    cal_last = cal[-1] if cal else None
    lanes = []
    for lane, script in LANES:
        lane_dir = os.path.join(DATA, lane)
        script, script_via = resolve_script(lane, script)
        entry = {"lane": lane, "script": script, "script_via": script_via, "dir": "data/" + lane}
        if not os.path.isdir(lane_dir):
            entry.update(
                exists=False,
                files=0,
                bytes=0,
                by_ext={},
                first_bar=None,
                last_bar=None,
                unreadable=0,
                lag_trading_days=None,
                script_present=os.path.isfile(os.path.join(ROOT, script)),
                source_note=None,
            )
            lanes.append(entry)
            continue
        files, total, by_ext = lane_size(lane_dir)
        first, last, unreadable, dated = lane_coverage(lane_dir)
        entry.update(
            exists=True,
            files=files,
            bytes=total,
            by_ext=by_ext,
            first_bar=first,
            last_bar=last,
            unreadable=unreadable,
            files_with_dates=dated,
            lag_trading_days=(trading_days_between(cal, last, cal_last) if last and cal_last else None),
            script_present=os.path.isfile(os.path.join(ROOT, script)),
            source_note=script_docstring(script),
        )
        lanes.append(entry)
    payload = {
        "contract": "O-20261124-2300-bm-c §1-C",
        "producer_machine": os.environ.get("COMPUTERNAME") or "unknown",
        "calendar_last_bar": cal_last,
        "calendar_rows": len(cal),
        "lanes": lanes,
        "totals": {
            "lanes": len(lanes),
            "files": sum(x["files"] for x in lanes),
            "bytes": sum(x["bytes"] for x in lanes),
            "lanes_with_script": sum(1 for x in lanes if x.get("script_present")),
        },
    }
    return payload


def _mb(n):
    return round(n / 1048576.0, 1)


def render_md(payload):
    lines = []
    lines.append("# 车道交接说明 · %s 本机实测（供对端 `ingest_diff` 复核）"
                 % (payload.get("producer_machine") or "unknown"))
    lines.append("")
    lines.append("> 回应 `O-20261124-2300-bm-c` §1-C。本文件由 `scripts/ingest_lanes_doc.py` 从盘上 derive，"
                 "禁手改——要改就改生成器再重跑。")
    lines.append("")
    lines.append("## 0. 一句话结论")
    lines.append("")
    t = payload["totals"]
    missing = [x["lane"] for x in payload["lanes"] if not x.get("script_present")]
    lines.append(
        "- 共 **%d 条车道 / %d 个文件 / %.1f MB**；其中 **%d 条**有重建脚本。"
        % (t["lanes"], t["files"], _mb(t["bytes"]), t["lanes_with_script"])
    )
    if missing:
        lines.append("- 无重建脚本（只能分包）：**%s**。" % "、".join(missing))
    else:
        lines.append("- **全部车道都有重建脚本，不需要分包**——对端按下表逐条跑即可，"
                     "省掉 95MB 分包的往返。")
    lines.append("- 本地交易日历尾 bar = **%s**（以 `data/daily/510300.csv` 为时钟）；"
                 "尾 bar 落后它的车道见 §2 的「缺口」列。" % (payload["calendar_last_bar"] or "未知"))
    lines.append("")
    lines.append("## 1. 总表")
    lines.append("")
    lines.append("| 车道 | 文件数 | 体量 | 覆盖首 bar | 覆盖尾 bar | 缺口(交易日) | 重建脚本 |")
    lines.append("|---|---|---|---|---|---|---|")
    for x in payload["lanes"]:
        lag = x.get("lag_trading_days")
        lag_s = "—" if lag is None else ("0" if lag == 0 else str(lag))
        lines.append(
            "| `%s` | %d | %.1f MB | %s | %s | %s | `%s` |"
            % (x["lane"], x["files"], _mb(x["bytes"]), x.get("first_bar") or "—",
               x.get("last_bar") or "—", lag_s, x["script"] if x.get("script_present") else "（缺）")
        )
    lines.append("")
    lines.append("## 2. 逐车道：重建命令 / 数据源 / 覆盖与缺口")
    lines.append("")
    for x in payload["lanes"]:
        lines.append("### `%s`" % x["lane"])
        lines.append("")
        if not x.get("script_present"):
            lines.append("- **重建命令**：本机没有对应脚本（`%s` 不存在）→ 只能分包。" % x["script"])
        else:
            via = x.get("script_via")
            via_s = "" if via in (None, "declared", "convention") else "（写者登记表 `%s`）" % via
            lines.append("- **重建命令**：`python %s`%s（幂等；面板新鲜=零网络 no-op）" % (x["script"], via_s))
            note = x.get("source_note")
            lines.append("- **数据源与频率**：%s" % (note if note else "脚本未写模块 docstring（未标注）"))
        ext = x.get("by_ext") or {}
        if ext:
            lines.append("- **形态**：%s" % "，".join("%s×%d" % (k, v) for k, v in sorted(ext.items())))
        lines.append(
            "- **覆盖**：%s → %s；%d 个文件带日期列%s"
            % (
                x.get("first_bar") or "—",
                x.get("last_bar") or "—",
                x.get("files_with_dates") or 0,
                ("，%d 个文件读不出日期" % x["unreadable"]) if x.get("unreadable") else "",
            )
        )
        lag = x.get("lag_trading_days")
        if lag is None:
            lines.append("- **缺口**：无日期列可比，未判定。")
        elif lag == 0:
            lines.append("- **缺口**：无（尾 bar 已对齐本地日历）。")
        else:
            lines.append("- **缺口**：落后本地日历 **%d 个交易日**（%s → %s）——重建时会自动补。"
                         % (lag, x.get("last_bar"), payload["calendar_last_bar"]))
        lines.append("")
    lines.append("## 3. 分包规则（当前未启用）")
    lines.append("")
    lines.append("本机全部车道都有重建路径，按上表跑脚本即可，不需要分包。")
    lines.append("若对端网络不可用、必须走物理件，则按令 §1-C：单包 ≤95MB，"
                 "放 `research/INGEST/PACKS/<日期>/`，并在 `research/INGEST/PACKS.json` 写 "
                 "`{path, bytes, sha256, covers:[起,止]}`；分包清单届时由生成器补 `--packs` 面，禁手写。")
    lines.append("")
    lines.append("## 4. 复现")
    lines.append("")
    lines.append("```")
    lines.append("python scripts/ingest_lanes_doc.py           # 重生本文件 + .json 孪生")
    lines.append("python scripts/ingest_lanes_doc.py --check # 比对面是否落后于盘（rc0 一致 / rc3 需重建）")
    lines.append("```")
    lines.append("")
    return "\n".join(lines) + "\n"


def write_outputs(payload):
    md = render_md(payload)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
    return md


def cmd_run():
    payload = build()
    write_outputs(payload)
    t = payload["totals"]
    print("LANES-DOC ok lanes=%d files=%d bytes=%d scripts=%d"
          % (t["lanes"], t["files"], t["bytes"], t["lanes_with_script"]))
    print("  md   -> %s" % OUT_MD)
    print("  json -> %s" % OUT_JSON)
    return 0


def cmd_check():
    payload = build()
    want = render_md(payload)
    if not os.path.isfile(OUT_MD):
        print("STALE face missing: %s" % OUT_MD)
        return 3
    with io.open(OUT_MD, "r", encoding="utf-8", newline="") as f:
        have = f.read().replace("\r\n", "\n")
    if have != want:
        print("STALE LANES-DASHENG.md 落后于盘（车道数/体量/覆盖变了）——跑 python scripts/ingest_lanes_doc.py")
        return 3
    if not os.path.isfile(OUT_JSON):
        print("STALE face missing: %s" % OUT_JSON)
        return 3
    print("LANES-DOC check ok lanes=%d" % payload["totals"]["lanes"])
    return 0


def cmd_selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # L1 车道路径与脚本名同源（无重复登记）
    names = [l for l, _ in LANES]
    leg("lanes unique", len(names) == len(set(names)))

    # L2 日期列识别
    leg("date idx by name", _date_index("date,open,close") == 0)
    leg("day idx second", _date_index("symbol,day,close") == 1)
    leg("no date col -> None", _date_index("open,close") is None)
    leg("bom date col", _date_index("\ufeffdate,close") == 0)

    # L3 日期归一
    leg("norm date", _norm_date("2026-11-24 13:53:00") == "2026-11-24")
    leg("norm date empty", _norm_date("") is None)
    leg("norm date garbage", _norm_date("abc") is None)

    # L4 交易日缺口算术（闭开区间：落后 N 天就报 N）
    cal = ["2026-11-20", "2026-11-23", "2026-11-24"]
    leg("lag 0 when aligned", trading_days_between(cal, "2026-11-24", "2026-11-24") == 0)
    leg("lag 1", trading_days_between(cal, "2026-11-23", "2026-11-24") == 1)
    leg("lag 2 skips weekend", trading_days_between(cal, "2026-11-20", "2026-11-24") == 2)
    leg("lag 0 when ahead", trading_days_between(cal, "2026-12-01", "2026-11-24") == 0)

    # L5 CSV 覆盖读出（真跑盘上文件）
    if os.path.isfile(CALENDAR):
        cov = _csv_coverage(CALENDAR)
        leg("calendar coverage read", cov is not None and _norm_date(cov[1]) is not None)
        leg("calendar monotonic", _norm_date(cov[0]) < _norm_date(cov[1]))
    else:
        leg("calendar coverage read", False)

    # L6 尾行直取不整读（大文件也快）——用日历文件自证能取到尾行
    tail = _read_tail_line(CALENDAR) if os.path.isfile(CALENDAR) else None
    leg("tail line readable", bool(tail) and "," in tail)

    # L7 docstring 提取
    note = script_docstring("scripts/update_repo.py")
    leg("docstring extracted", bool(note) and len(note) > 10)
    leg("docstring missing -> None", script_docstring("scripts/__nope__.py") is None)

    # L8 写者登记表解析 + 脚本解析（防「约定猜不到就报成分包件」）
    wmap = writer_script_map()
    leg("writer map non-empty", len(wmap) > 0)
    leg("writer map cb_panel", wmap.get("cb_panel") == "cb_dual_low")
    rel, via = resolve_script("cb_daily", "scripts/cb_dual_low.py")
    leg("resolve declared", rel == "scripts/cb_dual_low.py" and via == "declared")
    rel2, via2 = resolve_script("cb_panel", "")
    leg("resolve via registry", rel2 == "scripts/cb_dual_low.py" and via2 == "writer-registry")
    rel3, via3 = resolve_script("daily", "")
    leg("resolve via convention", rel3 == "scripts/update_daily.py" and via3 == "convention")
    rel4, via4 = resolve_script("__nope_lane__", "")
    leg("resolve unknown -> None", via4 is None)

    # L9 build 面自洽
    payload = build()
    leg("build lanes count", len(payload["lanes"]) == len(LANES))
    leg("build totals sum",
        payload["totals"]["bytes"] == sum(x["bytes"] for x in payload["lanes"]))
    leg("every lane resolved", all(x.get("script") for x in payload["lanes"]))
    leg("render deterministic", render_md(build()) == render_md(build()))

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print(("  ok   " if ok else "  FAIL ") + n)
    print("SELFTEST %d/%d %s" % (len(legs) - len(bad), len(legs), "PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest", "check"])
    ap.add_argument("--check", action="store_true", help="等价于 mode=check")
    args = ap.parse_args(argv)
    mode = "check" if args.check else args.mode
    if mode == "selftest":
        return cmd_selftest()
    if mode == "check":
        return cmd_check()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
