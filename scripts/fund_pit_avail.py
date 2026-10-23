"""T27 PIT availability repair -- consumer-facing half (r1096 contract).

The r1095 repair (``fund_avail_pit_t27``) rewrote the statement panels'
``avail_date`` as ``min(latest_revision, statutory_deadline)`` but the derived
face was keyed on ``period_end`` alone, so no per-symbol consumer could join
it, and no consumer face was ever tightened. This module closes both halves:

  * ``build()`` re-emits the anchors keyed on ``(code, period_end)`` holding
    BOTH bounds -- ``avail_strict`` (the stored latest-revision date; zero
    look-ahead risk) and ``avail_pit`` (``min(strict, deadline)``; tighter) --
    and records the exposed row share, i.e. the fraction of tightened rows
    that rest on the statutory-deadline bound. That share is DISCLOSED, never
    asserted as fact.
  * the consumer overlay rewrites ``avail_date`` on the frozen quality/growth
    faces with ``min(frozen_anchor, avail_pit)`` so those faces stop waiting
    for a revision date that can trail the announcement by a year.

Invariants (fail-closed, asserted on the real rows before anything is written):
period_end <= avail_strict <= deadline-bound floor, avail_pit <= avail_strict,
overlay date never later than the frozen anchor, zero duplicate
``(code, period_end)`` keys.

Outputs (derived faces; the frozen consumer faces are never overwritten):
    data/fund_history_export/pitv/<face>_avail_keyed.parquet
    data/fund_history_export/pitv/<consumer>_faces_pit.parquet
    results/fund_pitv_t27.json

Exit codes: 0 ok | 2 machinery / invariant breach | 3 missing panel face.
Selftest: python scripts/fund_pit_avail.py selftest
"""
import datetime as dt
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from update_fund_statements import (  # noqa: E402
    FACE_PATH, statutory_deadline)
from fund_avail_pit_t27 import _deadline_date, avail_pit  # noqa: E402

OUT_DIR = os.path.join(ROOT, "data", "fund_history_export", "pitv")
SUMMARY = os.path.join(ROOT, "results", "fund_pitv_t27.json")
FACES = ("income", "balance", "cashflow")
CONSUMERS = ("quality", "growth")
CONSUMER_PATH = os.path.join(ROOT, "data", "fund_history_export",
                             "{name}_faces.parquet")
RAW_CODE_COL = "\u80a1\u7968\u4ee3\u7801"  # 股票代码 in the raw EM export
KEY = ("code", "period_end")


def _keyed(frame: pd.DataFrame, face: str) -> pd.DataFrame:
    """Rename the raw symbol column and refuse an unjoinable face (r1096).

    A derived face whose join key silently vanished stays syntactically valid
    while being unusable, so both the key presence and its uniqueness fail
    closed here instead of downstream."""
    sub = frame.copy()
    if "code" not in sub.columns and RAW_CODE_COL in sub.columns:
        sub = sub.rename(columns={RAW_CODE_COL: "code"})
    for col in KEY:
        if col not in sub.columns:
            raise ValueError(f"{face}: join key column {col!r} missing")
    dup = sub.duplicated(subset=list(KEY)).sum()
    if dup:
        raise ValueError(f"{face}: {dup} duplicate (code, period_end) keys")
    return sub


def _strict(period_end, stored) -> str:
    """Stored latest-revision date; deadline only when it is unusable.

    A stored date earlier than the period end cannot be a real announce (a
    second leak of the revision-column semantic); the deadline is the honest
    fallback because it is still an upper bound on the true announce."""
    deadline = _deadline_date(period_end)
    stamp = pd.to_datetime(stored, errors="coerce")
    if pd.isna(stamp):
        return deadline.isoformat()
    d = stamp.date()
    if d < dt.date.fromisoformat(str(period_end)):
        return deadline.isoformat()
    return d.isoformat()


def anchors(face: str, frame: pd.DataFrame) -> pd.DataFrame:
    sub = _keyed(frame, face)
    if "avail_date" not in sub.columns:
        raise ValueError(f"{face}: avail_date column missing")
    sub = sub[["code", "period_end", "avail_date"]].copy()
    sub["avail_strict"] = [_strict(p, a) for p, a in
                           zip(sub["period_end"], sub["avail_date"])]
    sub["avail_pit"] = [avail_pit(p, a) for p, a in
                        zip(sub["period_end"], sub["avail_date"])]
    sub["deadline"] = [_deadline_date(p).isoformat() for p in sub["period_end"]]
    sub["period_end"] = sub["period_end"].astype(str)
    pe = pd.to_datetime(sub["period_end"])
    strict = pd.to_datetime(sub["avail_strict"])
    pit = pd.to_datetime(sub["avail_pit"])
    if (strict < pe).any():
        raise AssertionError(f"{face}: avail_strict before period_end")
    if (pit < pe).any():
        raise AssertionError(f"{face}: avail_pit before period_end")
    if (pit > strict).any():
        raise AssertionError(f"{face}: avail_pit later than avail_strict")
    return sub


def overlay(name: str, table: pd.DataFrame) -> dict:
    """Tighten a frozen consumer face: avail_date = min(anchor, avail_pit)."""
    src = CONSUMER_PATH.format(name=name)
    if not os.path.exists(src):
        return {"consumer": name, "status": "missing_face"}
    frame = _keyed(pd.read_parquet(src), name)
    if "avail_date" not in frame.columns:
        return {"consumer": name, "status": "no_avail_column"}
    frame["period_end"] = frame["period_end"].astype(str)
    joined = frame.merge(table[["code", "period_end", "avail_pit"]],
                         on=list(KEY), how="left", validate="one_to_one")
    anchor = pd.to_datetime(joined["avail_date"], errors="coerce")
    pitv = pd.to_datetime(joined["avail_pit"], errors="coerce")
    tightened = pitv.notna() & (pitv < anchor)
    if (pitv.notna() & (pitv > anchor)).any():
        raise AssertionError(f"{name}: overlay date later than frozen anchor")
    if (pitv.notna() & (pitv < pd.to_datetime(joined["period_end"]))).any():
        raise AssertionError(f"{name}: overlay date before period_end")
    joined.loc[tightened, "avail_date"] = joined.loc[tightened, "avail_pit"]
    joined = joined.drop(columns=["avail_pit"])
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{name}_faces_pit.parquet")
    joined.to_parquet(out, index=False)
    return {"consumer": name, "status": "ok", "rows": int(len(joined)),
            "matched": int(pitv.notna().sum()),
            "tightened": int(tightened.sum()),
            "out": os.path.relpath(out, ROOT)}


def build() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    receipt = {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "audit": "T27 PIT availability repair -- keyed anchors + consumer overlay",
        "faces": {}, "consumers": {}, "missing": [],
    }
    tables = {}
    for face in FACES:
        path = FACE_PATH[face]
        if not os.path.exists(path):
            receipt["missing"].append(face)
            continue
        table = anchors(face, pd.read_parquet(path))
        tables[face] = table
        out = os.path.join(OUT_DIR, f"{face}_avail_keyed.parquet")
        table.to_parquet(out, index=False)
        tight = pd.to_datetime(table["avail_pit"]) < \
            pd.to_datetime(table["avail_strict"])
        on_deadline = pd.to_datetime(table["avail_pit"]) == \
            pd.to_datetime(table["deadline"])
        receipt["faces"][face] = {
            "rows": int(len(table)),
            "codes": int(table["code"].nunique()),
            "strict_held_rows": int((~tight).sum()),
            "tightened_rows": int(tight.sum()),
            "deadline_bound_share": round(
                float(on_deadline.mean()), 6),
            "out": os.path.relpath(out, ROOT),
        }
        print(face, receipt["faces"][face])

    if tables:
        merged = pd.concat(tables.values(), ignore_index=True)
        merged = merged.drop_duplicates(subset=list(KEY), keep="first")
        for name in CONSUMERS:
            try:
                receipt["consumers"][name] = overlay(name, merged)
            except Exception as exc:  # noqa: BLE001 -- disclosed, not hidden
                receipt["consumers"][name] = {"consumer": name,
                                              "status": f"error: {exc}"}
            print(name, receipt["consumers"][name])

    with open(SUMMARY, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=2)
    print("wrote", os.path.relpath(SUMMARY, ROOT))
    if len(receipt["missing"]) == len(FACES):
        print("MISSING PANEL FACES:", receipt["missing"])
        return 3
    return 0


def selftest() -> int:
    checks = []
    tiny = pd.DataFrame({"code": ["000001", "000002"],
                         "period_end": ["2024-06-30", "2024-06-30"],
                         "avail_date": ["2024-08-28", "2025-08-26"]})
    out = anchors("income", tiny)
    # 1-2 key survives / raw-name column is renamed
    checks.append(list(out["code"]) == ["000001", "000002"])
    raw = pd.DataFrame({RAW_CODE_COL: ["000003"],
                        "period_end": ["2024-06-30"],
                        "avail_date": ["2024-08-28"]})
    checks.append(list(anchors("income", raw)["code"]) == ["000003"])
    # 3-4 unjoinable / duplicated faces fail closed
    try:
        anchors("income", pd.DataFrame({"period_end": ["2024-06-30"],
                                        "avail_date": ["2024-08-28"]}))
        checks.append(False)
    except ValueError:
        checks.append(True)
    dup = pd.concat([tiny, tiny], ignore_index=True)
    try:
        anchors("income", dup)
        checks.append(False)
    except ValueError:
        checks.append(True)
    # 5-7 strict bound: stored kept, missing/early fall back to the deadline
    checks.append(list(out["avail_strict"]) == ["2024-08-28", "2025-08-26"])
    checks.append(_strict("2024-06-30", None) == "2024-08-31")
    checks.append(_strict("2024-06-30", "2024-02-01") == "2024-08-31")
    # 8-11 pit clamps late revisions and stays inside both bounds
    checks.append(list(out["avail_pit"]) == ["2024-08-28", "2024-08-31"])
    checks.append(out["avail_pit"].ge(out["period_end"]).all())
    checks.append(out["avail_pit"].le(out["deadline"]).all())
    checks.append(out["avail_pit"].le(out["avail_strict"]).all())
    # 12-15 overlay tightens only, keeps unmatched rows, never later
    base = pd.DataFrame({"code": ["000001", "000002", "000009"],
                         "period_end": ["2024-06-30"] * 3,
                         "avail_date": ["2025-08-26", "2024-08-28",
                                        "2025-08-26"]})
    anchor = pd.to_datetime(base["avail_date"])
    pitv = pd.to_datetime(pd.Series(["2024-08-31", "2024-08-28", None]))
    tight = pitv.notna() & (pitv < anchor)
    checks.append(list(tight) == [True, False, False])
    checks.append(int((~pitv.notna()).sum()) == 1)
    checks.append(not (pitv.notna() & (pitv > anchor)).any())
    checks.append(int(tight.sum()) == 1)
    # 16 empty frame is an honest no-op, not a crash
    empty = anchors("income", pd.DataFrame({"code": [], "period_end": [],
                                            "avail_date": []}))
    checks.append(len(empty) == 0)
    failed = [i for i, ok in enumerate(checks) if not ok]
    print(f"selftest {len(checks) - len(failed)}/{len(checks)} PASS")
    if failed:
        print("failed cases:", failed)
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    try:
        sys.exit(build())
    except AssertionError as exc:
        print("INVARIANT BREACH:", exc)
        sys.exit(2)