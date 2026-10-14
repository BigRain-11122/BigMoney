# r1007 ledger path-split heal (5th instance, r985/r991 family precedent)
# orphan: logs/iteration-loop/round_reports-bm-c.md received r996+ closeout writes
# canonical: root round_reports-bm-c.md stalled at r995-fuchan 10:54:38
# heal = line-level union verbatim (treasure_guard rc3 honored, carve-out per law)
#   + never-written-rounds backfill MARKER ONLY (fu-shu prohibition: no fabrication)
#   + orphan-tail freeze pointer
# zero deletion, zero rewrite of existing lines, append-only on both faces
import io, json, hashlib, datetime

CAN = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md"
ORPH = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
RCPT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1007bmc_ledger_heal_receipt.json"

can_raw = io.open(CAN, encoding="utf-8", errors="replace", newline="").read()
orph_raw = io.open(ORPH, encoding="utf-8", errors="replace", newline="").read()
can_lines = can_raw.splitlines()
orph_lines = orph_raw.splitlines()
can_set = set(can_lines)

# newline style of canonical (last line wins)
crlf = can_raw.endswith("\r\n") or ("\r\n" in can_raw and "\n" not in can_raw.replace("\r\n", ""))

# union scope: only recent split-window rows (2026-10-14T* after 10h) missing from canonical
missing_recent = [l for l in orph_lines
                  if l not in can_set and l.startswith("2026-10-14T") and l[11:13] >= "10"]
# dedupe preserve order
seen = set()
union_rows = []
for l in missing_recent:
    if l not in seen:
        seen.add(l)
        union_rows.append(l)

labels = []
for l in union_rows:
    parts = [p.strip() for p in l.split("|")]
    labels.append(parts[1] if len(parts) > 1 else "?")

marker = ("[r1007 path-split heal backfill marker 2026-10-14T20:0x] rounds r1003/r1004/r1005 have no row in ANY ledger "
          "(dead-chain windows absorbed by r1006 per state-bm-c.json r1006_absorb_note; authoritative faces = state "
          "absorb/closeout notes + git commits 8e980ce3e/6cd270b40/27e514139/af6ec72f9; fu-shu prohibition honored -- "
          "no retroactive fabrication)")
pointer = ("[r1007 freeze pointer 2026-10-14T20:0x] post-r1006 closeout writes on this file are FROZEN per fleet/README "
           "s6 + r750 law: bm-c round rows go to ROOT round_reports-bm-c.md (canonical). Recent rows r996-r1006 union'd "
           "verbatim to canonical this window (receipt results/_r1007bmc_ledger_heal_receipt.json). This legacy file is "
           "kept read-only as history.")

nl = "\r\n" if crlf else "\n"
append_can = nl.join(union_rows + [marker]) + nl
append_orph = pointer + nl

before_can = hashlib.sha256(can_raw.encode("utf-8", "replace")).hexdigest()
before_orph = hashlib.sha256(orph_raw.encode("utf-8", "replace")).hexdigest()

with io.open(CAN, "a", encoding="utf-8", newline="") as f:
    f.write(append_can)
with io.open(ORPH, "a", encoding="utf-8", newline="") as f:
    f.write(append_orph)

after_can_raw = io.open(CAN, encoding="utf-8", errors="replace", newline="").read()
after_orph_raw = io.open(ORPH, encoding="utf-8", errors="replace", newline="").read()

receipt = {
    "heal": "r1007 ledger path-split 5th instance (r985/r991 family)",
    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    "canonical": CAN,
    "orphan": ORPH,
    "treasure_guard_prescan": "rc3 HARD REJECT (registry hit) honored -> line-level union carve-out per law",
    "union_rows_count": len(union_rows),
    "union_row_labels": labels,
    "never_written_rounds_marker_only": ["r1003", "r1004", "r1005"],
    "zero_deletion": True,
    "verbatim_assert": all(l in after_can_raw for l in union_rows),
    "prior_lines_untouched_assert": after_can_raw.startswith(can_raw[:can_raw.rfind(nl) + 1] if can_raw else ""),
    "orphan_pointer_appended": pointer in after_orph_raw,
    "sha256_canonical_before": before_can,
    "sha256_canonical_after": hashlib.sha256(after_can_raw.encode("utf-8", "replace")).hexdigest(),
    "sha256_orphan_before": before_orph,
    "sha256_orphan_after": hashlib.sha256(after_orph_raw.encode("utf-8", "replace")).hexdigest(),
}
io.open(RCPT, "w", encoding="utf-8").write(json.dumps(receipt, ensure_ascii=False, indent=1))
print(json.dumps({k: receipt[k] for k in ("union_rows_count", "union_row_labels", "verbatim_assert",
                                           "prior_lines_untouched_assert", "orphan_pointer_appended")}))
