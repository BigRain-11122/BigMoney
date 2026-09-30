"""Canonical data-panel gate (RW-4 slice-2, T-127 / D-20260930-05).

Audit root (P0-4, docs/audits/bigmoney-credibility-audit-20260930.md):
data/daily holds 1724 CSVs where only the 48 bare-code core48 files are
the fresh in-service panel; 1670+ prefixed legacy files stopped
2026-09-22, and every bare code ALSO exists as a prefixed twin
(sh510300.csv vs 510300.csv). Any full-directory read is polluted by
stale bars + duplicate securities (tasks/backtest_task.py used the
filename itself as the symbol).

Gate legs (audit RW-4 row; fail-closed: gate fail = batch NOT
accepted, callers must refuse/exit non-zero):

  G1 canonicalization -- strip the sh/sz prefix; the bare 6-digit
     code IS the canonical key (load_core isdigit precedent). A
     requested symbol list must satisfy len(set(list)) == len(list)
     AFTER canonicalization -- twins/duplicates = REFUSE.

  G2 stale exclusion -- a symbol whose last bar trails the panel
     anchor date by more than stale_days (calendar; default 5, the
     audit Q7 caliber that produced the 53-fresh/1671-stale split)
     is excluded from the batch panel and REPORTED, never silently
     dropped. Excluding a symbol the batch explicitly requires
     (required=...) = REFUSE.

  G3 in-service lock -- faces that run the in-service panel (live
     paper anchors, registered-member reruns) may only assemble
     symbols inside the FROZEN whitelist below. The universe is this
     list, NOT the directory listing: new/stale files can no longer
     silently expand or shrink the in-service panel. Out-of-lock
     symbol, missing in-lock file, or stale in-lock member = REFUSE.

Honest number disclosure (governance §10): the audit row says the
in-service panel is "locked to 30"; no in-repo count reproduces 30
(48 bare core48 / 53 fresh incl. ETF-lane twins / 6 registered / 18
held / 22 PROSPECT). The lock below = the REAL in-service universe
(the 48 bare core48 codes) and the delivery memo
results/RW4_PANEL_GATE_20260930.md discloses the divergence
instead of fabricating a 30-member panel.

Adoption state after this slice: live/paper.py load_core runs the
gate in in-service mode (behavior-identical today, proven by the
6/6 anchor gates); general batch faces adopt via
panel_gate.gate(symbols, mode="batch") at assembly time. Direct
prefix readers (div_lowvol family / trial_labor_w4 w5 /
regime_calibration) are judged or archived lines -- they stay on
their frozen calibers (archive-valuation law) and new batches must
not reuse their read pattern.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# G3: frozen in-service whitelist (48 bare core48 codes, RW-4 lock face).
# Frozen 2026-09-30 (r476). Changing this list = conscious re-freeze with a
# delivery memo, never a silent directory-derived drift.
# ---------------------------------------------------------------------------
INSERVICE_WHITELIST: tuple[str, ...] = (
    "159901", "159915", "159919", "159920", "159928", "159934", "159949",
    "159980", "159985", "159992", "159995", "159996", "510050", "510300",
    "510310", "510330", "510500", "511010", "511090", "511260", "512000",
    "512010", "512100", "512170", "512200", "512400", "512480", "512660",
    "512690", "512710", "512720", "512800", "512880", "512980", "513050",
    "513100", "513180", "513500", "513520", "515000", "515030", "515050",
    "515170", "515220", "515790", "518880", "588000", "588080",
)
INSERVICE_SHA16 = hashlib.sha256(",".join(INSERVICE_WHITELIST).encode()
                                 ).hexdigest()[:16]

# G2: stale window (calendar days, audit Q7 caliber -> 53 fresh / 1671 stale)
STALE_DAYS_DEFAULT = 5

_PREFIX_RE = re.compile(r"^(?:sh|sz)?(\d{6})$")


def canonical_symbol(sym: str) -> str:
    """Bare 6-digit code is the canonical key ('sh510300'/'510300.csv'
    -> '510300'). Anything that does not resolve to a 6-digit code
    raises ValueError (fail-closed: unknown key shapes are refused,
    not guessed)."""
    s = str(sym).strip().lower()
    if s.endswith(".csv"):
        s = s[:-4]
    s = os.path.basename(s)
    m = _PREFIX_RE.match(s)
    if not m:
        raise ValueError(f"non-canonical symbol shape: {sym!r}")
    return m.group(1)


@dataclass
class PanelInventory:
    """Directory scan face: canonical code -> which file serves it."""
    bare: dict = field(default_factory=dict)      # code -> filename (bare key)
    prefixed: dict = field(default_factory=dict)  # code -> filename (sh/sz key)
    last_bars: dict = field(default_factory=dict)  # code -> 'YYYY-MM-DD' (canonical face)

    @property
    def twins(self) -> list:
        return sorted(set(self.bare) & set(self.prefixed))

    def serving_file(self, code: str) -> str:
        return self.bare.get(code) or self.prefixed[code]


def _tail_last_bar(path: str) -> str | None:
    """Last row's date column via full-tail read (r474 probe face).
    Returns None on empty/undecodable file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().strip().splitlines()
        if len(lines) < 2:
            return None
        return lines[-1].split(",")[0].strip('"').strip()
    except Exception:
        return None


def scan_daily_dir(daily_dir: str) -> PanelInventory:
    inv = PanelInventory()
    for f in sorted(os.listdir(daily_dir)):
        if not f.endswith(".csv"):
            continue
        stem = f[:-4]
        try:
            code = canonical_symbol(stem)
        except ValueError:
            continue  # non-instrument file shapes are not panel members
        m = re.match(r"^(sh|sz)\d{6}$", stem)
        if m:
            inv.prefixed[code] = f
        else:
            inv.bare[code] = f
    for code in set(inv.bare) | set(inv.prefixed):
        # canonical face = bare file when a twin exists (load_core precedent)
        inv.last_bars[code] = _tail_last_bar(
            os.path.join(daily_dir, inv.serving_file(code)))
    return inv


@dataclass
class GateResult:
    ok: bool
    mode: str
    accepted: list
    excluded: dict = field(default_factory=dict)   # code -> reason
    reasons: list = field(default_factory=list)     # refusal reasons (ok=False)

    def refuse(self, reason: str) -> None:
        if reason not in self.reasons:
            self.reasons.append(reason)


def gate(symbols, mode: str = "batch", *, daily_dir: str | None = None,
         inventory: PanelInventory | None = None,
         anchor: str | None = None, stale_days: int = STALE_DAYS_DEFAULT,
         required=(), whitelist=INSERVICE_WHITELIST) -> GateResult:
    """Batch-acceptance gate. mode='inservice' enforces G1+G2+G3;
    mode='batch' enforces G1+G2 (whitelist not applied -- research
    batches may name wider universes, staleness still fails closed).

    anchor: 'YYYY-MM-DD' staleness reference; default = panel max
    last bar (data-feed freshness caliber, NOT the evidence_cutoff --
    historical truncation is RW-2's jurisdiction, not this gate's).
    """
    res = GateResult(ok=True, mode=mode, accepted=[])
    seq = []
    for s in symbols:
        try:
            seq.append(canonical_symbol(s))
        except ValueError as exc:
            res.ok = False
            res.refuse(f"non-canonical symbol: {exc}")
    if len(set(seq)) != len(seq):  # G1 acceptance face (audit verbatim)
        res.ok = False
        dups = sorted({c for c in seq if seq.count(c) > 1})
        res.refuse(f"twin/duplicate symbols after canonicalization: {dups} "
                   f"(len(set)==len(list) violated)")
    inv = inventory or scan_daily_dir(daily_dir)

    def _d(a: str, b: str):  # calendar-day delta a-b (ISO dates sort)
        from datetime import date
        y1, m1, d1 = map(int, a.split("-"))
        y2, m2, d2 = map(int, b.split("-"))
        return (date(y1, m1, d1) - date(y2, m2, d2)).days

    bars = {c: inv.last_bars.get(c) for c in set(seq)}
    have_bar = {c: b for c, b in bars.items() if b}
    if anchor is None:
        anchor = max(have_bar.values()) if have_bar else None
    required = {canonical_symbol(r) for r in required}

    wl = set(whitelist)
    if mode == "inservice":  # G3: the lock is the FULL universe -- a
        for code in sorted(wl - set(seq)):  # missing member = silent shrink
            res.ok = False            # of the in-service panel = refuse
            res.refuse(f"missing in-lock symbol in in-service batch: {code}")
    for code in sorted(set(seq)):
        if mode == "inservice" and code not in wl:  # G3 out-of-lock
            res.ok = False
            res.refuse(f"out-of-lock symbol in in-service batch: {code}")
            continue
        if mode == "inservice" and code not in inv.bare:
            # canonical face = the BARE file; a prefixed twin must never
            # substitute for it in the in-service panel (audit P0-4
            # twin face: prefixed twins carry divergent/stale bars)
            res.ok = False
            res.refuse(f"in-service member not served by canonical bare "
                       f"file: {code}")
            continue
        last = inv.last_bars.get(code)
        if not last:
            if mode == "inservice" or code in required:
                res.ok = False
                res.refuse(f"missing panel file for required/in-service symbol: {code}")
            else:
                res.excluded[code] = "no panel file / no bars"
            continue
        if anchor and _d(anchor, last) > stale_days:  # G2 stale
            if code in required:
                res.ok = False
                res.refuse(f"stale required symbol: {code} last_bar={last} "
                           f"anchor={anchor} stale_days={stale_days}")
            elif mode == "inservice":
                res.ok = False
                res.refuse(f"stale in-service member (lock breach): {code} "
                           f"last_bar={last} anchor={anchor}")
            else:
                res.excluded[code] = f"stale last_bar={last} (>{stale_days}d behind {anchor})"
            continue
        res.accepted.append(code)
    return res


def verify() -> bool:
    """Self-check: whitelist frozen (sha16 pinned), no duplicates, the
    audit's len(set)==len(list) face holds on the lock itself."""
    ok = len(INSERVICE_WHITELIST) == 48
    ok &= len(set(INSERVICE_WHITELIST)) == len(INSERVICE_WHITELIST)
    ok &= hashlib.sha256(",".join(INSERVICE_WHITELIST).encode()
                         ).hexdigest()[:16] == INSERVICE_SHA16
    ok &= canonical_symbol("sh510300") == "510300"
    ok &= canonical_symbol("510300.csv") == "510300"
    ok &= canonical_symbol("sz159915") == "159915"
    return bool(ok)


if __name__ == "__main__":
    print(f"INSERVICE_WHITELIST n={len(INSERVICE_WHITELIST)} "
          f"sha16={INSERVICE_SHA16}")
    print(f"STALE_DAYS_DEFAULT={STALE_DAYS_DEFAULT}")
    print("verify:", "PASS" if verify() else "FAIL")
    raise SystemExit(0 if verify() else 1)
