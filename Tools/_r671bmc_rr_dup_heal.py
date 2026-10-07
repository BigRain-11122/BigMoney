# -*- coding: utf-8 -*-
"""r671 bm-c round_reports-bm-c.md whole-file duplication heal (scan/heal/selftest).

DEFECT (found r671 S3): logs/iteration-loop/round_reports-bm-c.md grew by
THREE whole-file concatenations during the 10-07 push-race UU closeout
windows (r666/r668/r669): blob 2,230,045B (r665) -> 4,461,521 (r666) ->
8,933,204 (r668) -> 17,873,611B (r669) = 2^3 x ~2.23MB blocks, 9,265 lines,
header line x8. Family root = r453 merge-union bare-concat law
(pit-git-surgery.md): append-only union WITHOUT exact-line dedup duplicates
the full shared history each race window; no tripwire existed, so 3 windows
went 8x undetected (next doubling would be 35MB; 95MB red line = 5
doublings away). r657-r666/r668/r669 proper entry lines were lost in the
dead-session windows BEFORE the doublings (F0 tail ends at r656) --
unrecoverable from this file, commit messages retain the record.

HEAL LAW (r453 canonical remedy applied whole-file): exact-line dedup
keep-first + set-equality zero-loss gate + quarantine. Blank lines kept
only when the previous kept line is non-blank (single separators survive,
doubled block-boundary blanks collapse).

Modes:
  scan     (default) tripwire: ACTIVE-DUP detection, zero writes. exit 0
           clean / 1 ACTIVE DUP / 2 mechanism fault.
  heal     gated: requires ACTIVE-DUP signature + writes quarantine copy
           (results/_quarantine/<ts>_r671bmc_rr_predup/, 7-day observation
           window) then heals in place; all gates fail-closed BEFORE the
           single write. Receipt results/_r671bmc_rr_dup_heal_receipt.json.
  selftest offline fixtures, zero repo writes. exit 0 all PASS else 1.

Laws: TREASURE_PROTECTION_LAW §2 (prescan done separately this window:
treasure_guard prescan zero-hit rc0), r453 dedup law, quarantine mode,
CEO anti-waste (heal refuses when scan is clean)."""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
HEADER = "# bm-c round reports (per-machine file per fleet/README s6)"
RECEIPT = os.path.join(ROOT, "results", "_r671bmc_rr_dup_heal_receipt.json")
ENTRY_RE = re.compile(rb"^2026-\d{2}-\d{2}T[\d:]{8}\+08:00 \| r\d")


def _split_bodies(raw):
    """bytes -> (list of line bodies without EOL, dominant EOL bytes)."""
    crlf = raw.count(b"\r\n")
    eol = b"\r\n" if crlf >= 10 else b"\n"
    bodies = []
    for chunk in raw.split(b"\n"):
        if chunk.endswith(b"\r"):
            chunk = chunk[:-1]
        bodies.append(chunk)
    if bodies and bodies[-1] == b"":
        bodies.pop()  # trailing EOL artifact
    return bodies, eol


def _is_blank(body):
    return body.strip(b" \t") == b""


def _is_header(body):
    return body.decode("utf-8", errors="replace").strip() == HEADER


def _metrics(raw):
    bodies, eol = _split_bodies(raw)
    seen, mult = {}, {}
    for b in bodies:
        if _is_blank(b):
            continue
        mult[b] = mult.get(b, 0) + 1
    header_count = sum(1 for b in bodies if _is_header(b))
    entry_lines = {b: c for b, c in mult.items() if ENTRY_RE.match(b)}
    top = max(mult.values()) if mult else 0
    active_dup = header_count > 1 or top >= 4
    return {
        "total_lines": len(bodies),
        "unique_nonempty": len(mult),
        "header_count": header_count,
        "max_line_multiplicity": top,
        "entry_lines_unique": len(entry_lines),
        "entry_max_multiplicity": max(entry_lines.values()) if entry_lines else 0,
        "active_dup": bool(active_dup),
        "eol": eol.decode(),
    }, bodies, eol


def _dedup(bodies):
    """keep-first exact-line dedup; blank kept only after non-blank."""
    seen = set()
    out = []
    dropped = 0
    for b in bodies:
        if _is_blank(b):
            if out and not _is_blank(out[-1]):
                out.append(b)
            else:
                dropped += 1
            continue
        if b in seen:
            dropped += 1
            continue
        seen.add(b)
        out.append(b)
    return out, dropped


def cmd_scan():
    raw = open(LEDGER, "rb").read()
    m, _, _ = _metrics(raw)
    print(json.dumps(m, ensure_ascii=False))
    if m["active_dup"]:
        print("VERDICT: ACTIVE DUP" + (" (header x%d)" % m["header_count"]
              if m["header_count"] > 1 else ""))
        return 1
    print("VERDICT: CLEAN")
    return 0


def cmd_heal():
    raw = open(LEDGER, "rb").read()
    m, bodies, eol = _metrics(raw)
    if not m["active_dup"]:
        print("HEAL REFUSED: scan clean (nothing to heal)")
        return 1
    orig_sha = hashlib.sha256(raw).hexdigest()

    # quarantine copy (byte-exact) + manifest, BEFORE any write
    import datetime as _dt
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M")
    qdir = os.path.join(ROOT, "results", "_quarantine",
                        "%s_r671bmc_rr_predup" % stamp)
    os.makedirs(qdir, exist_ok=True)
    qcopy = os.path.join(qdir, "round_reports-bm-c.md")
    with open(qcopy, "wb") as fh:
        fh.write(raw)
    qsha = hashlib.sha256(open(qcopy, "rb").read()).hexdigest()
    assert qsha == orig_sha, "quarantine copy byte-identity gate"
    manifest = {
        "event": "r671 bm-c round_reports-bm-c.md pre-heal 8x-dup copy",
        "source": "logs/iteration-loop/round_reports-bm-c.md",
        "original_bytes": len(raw),
        "original_sha256": orig_sha,
        "observation_window_days": 7,
        "reason": "2^3 whole-file concat from r666/r668/r669 push-race UU "
                  "closeouts; healed in place by _r671bmc_rr_dup_heal.py "
                  "(set-equality zero-loss); git history retains all blobs.",
    }
    with open(os.path.join(qdir, "manifest.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)

    # heal (single write, after all inputs gated)
    healed_bodies, dropped = _dedup(bodies)
    healed = eol.join(healed_bodies) + eol

    # ---- zero-loss + shape gates (fail-closed) ----
    orig_set = {b for b in bodies if not _is_blank(b)}
    healed_set = {b for b in healed_bodies if not _is_blank(b)}
    assert healed_set == orig_set, "set-equality zero-loss gate FAILED"
    assert all(b in healed_set for b in bodies if not _is_blank(b)), \
        "every dropped line must be byte-identical to a kept line"
    hcount = sum(1 for b in healed_bodies if _is_header(b))
    assert hcount == 1, "healed header count==1 gate FAILED (%d)" % hcount
    ent_mult = {}
    for b in healed_bodies:
        if ENTRY_RE.match(b):
            ent_mult[b] = ent_mult.get(b, 0) + 1
    assert all(c == 1 for c in ent_mult.values()), \
        "healed entry multiplicity all==1 gate FAILED"
    assert len(healed) < len(raw), "reduction gate FAILED"

    with open(LEDGER, "wb") as fh:
        fh.write(healed)
    post_raw = open(LEDGER, "rb").read()
    pm, _, _ = _metrics(post_raw)
    assert not pm["active_dup"], "post-heal scan clean gate FAILED"
    assert post_raw == healed, "post-write byte-identity gate FAILED"

    receipt = {
        "round": 671, "machine": "bm-c",
        "action": "round_reports-bm-c.md 2^3 whole-file dup heal",
        "prescan": "treasure_guard prescan rc0 zero-hit (this window, before heal)",
        "original_bytes": len(raw), "healed_bytes": len(post_raw),
        "dropped_lines": dropped,
        "dropped_bytes": len(raw) - len(post_raw),
        "original_sha256": orig_sha,
        "healed_sha256": hashlib.sha256(post_raw).hexdigest(),
        "metrics_before": m, "metrics_after": pm,
        "set_equality_zero_loss": True,
        "header_count_after": hcount,
        "entry_lines_after_all_unique": True,
        "quarantine_dir": os.path.relpath(qdir, ROOT),
        "quarantine_sha256": qsha,
        "family_law": "r453 merge-union exact-line dedup (pit-git-surgery.md)",
        "lost_entries_note": "r657-r666/r668/r669 proper entry lines were "
            "lost in dead-session windows BEFORE the doublings (F0 tail ends "
            "r656) -- pre-existing loss, not healable from this file; commit "
            "messages retain the record.",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("HEALED %d -> %d bytes (-%d, dropped %d lines)" % (
        len(raw), len(post_raw), len(raw) - len(post_raw), dropped))
    print("post metrics:", json.dumps(pm, ensure_ascii=False))
    print("quarantine:", receipt["quarantine_dir"])
    print("receipt:", os.path.relpath(RECEIPT, ROOT))
    return 0


def _heal_core(raw):
    """pure function for selftest (no writes)."""
    m, bodies, eol = _metrics(raw)
    healed_bodies, dropped = _dedup(bodies)
    healed = eol.join(healed_bodies) + eol
    return m, bodies, healed_bodies, healed, dropped, eol


def cmd_selftest():
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))

    hdr = HEADER.encode()
    e1 = b"2026-10-01T10:00:00+08:00 | r1 | work A"
    e2 = b"2026-10-01T10:10:00+08:00 | r2 | work B"
    e3 = b"2026-10-01T10:20:00+08:00 | r3 | work C (tail era)"
    e4 = b"2026-10-01T10:30:00+08:00 | r4 | work D (tail era 2)"
    blk1 = b"\r\n".join([hdr, b"", e1, b"", e2, b""])
    blk2 = b"\r\n".join([hdr, b"", e1, b"", e2, b"", e3, b""])
    blk3 = b"\r\n".join([hdr, b"", e1, b"", e2, b"", e3, b"", e4, b""])
    raw = blk1 + b"\r\n" + blk2 + b"\r\n" + blk3 + b"\r\n"  # 3-block concat

    m, bodies, hb, healed, dropped, eol = _heal_core(raw)
    check("detect: active dup flagged", m["active_dup"] and m["header_count"] == 3)
    orig_set = {b for b in bodies if b.strip(b" \t")}
    healed_set = {b for b in hb if b.strip(b" \t")}
    check("zero-loss: set equality", orig_set == healed_set)
    check("header x1 after heal", sum(1 for b in hb if b == hdr) == 1)
    check("entries all exactly once",
          all(healed.count(e) == 1 for e in (e1, e2, e3, e4)))
    check("reduction positive", len(healed) < len(raw))
    check("blank separators survive",
          healed.count(b"\r\n\r\n") >= 3 and b"\r\n\r\n\r\n" not in healed)
    pm, _, _ = _metrics(healed)
    check("post-heal scan clean", not pm["active_dup"])

    # clean file must NOT be flagged
    clean = blk3 + b"\r\n"
    cm, _, _ = _metrics(clean)
    check("clean file stays clean", not cm["active_dup"])

    # blank-only-run collapse: doubled blanks at block boundary collapse
    check("doubled blanks collapsed", b"\r\n\r\n\r\n" not in healed)

    bad = [n for n, c in ok if not c]
    for n, c in ok:
        print("[%s] %s" % ("PASS" if c else "FAIL", n))
    print("selftest %d/%d PASS" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if mode == "scan":
        return cmd_scan()
    if mode == "heal":
        return cmd_heal()
    if mode == "selftest":
        return cmd_selftest()
    print("usage: _r671bmc_rr_dup_heal.py [scan|heal|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
