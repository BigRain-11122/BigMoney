# r985 ledger path-split heal (r749/r780 family recurrence, 3rd instance)
# Face A: 20 rows (19 labels, r967 x2) exist ONLY in ROOT orphan file (closeout scripts cloned
#   a ROOT-era template) -> verbatim line-level union into canonical face.
# Face B: 8 rounds (r960/961/964/966/972/973/978/979) have NO contemporaneous row anywhere
#   (dead-session era absorbed by successors) -> single consolidated disclosure row; NO retroactive
#   fabrication (fu-shu prohibition); authoritative records = state-bm-c.json notes + git commits.
# treasure_guard rc3 honored -> line-level union carve-out (additive only, zero delete).
# Receipt: results/_r985bmc_ledger_heal_receipt.json
import hashlib, json, os, re, datetime

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ROOT_FILE = os.path.join(BM, "round_reports-bm-c.md")
CANON_FILE = os.path.join(BM, "logs", "iteration-loop", "round_reports-bm-c.md")
RECEIPT = os.path.join(BM, "results", "_r985bmc_ledger_heal_receipt.json")

now_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
TARGETS = list(range(958, 985))  # r958..r984

root_bytes = open(ROOT_FILE, "rb").read()
canon_bytes = open(CANON_FILE, "rb").read()
root_lines = root_bytes.decode("utf-8").splitlines(keepends=True)
canon_text = canon_bytes.decode("utf-8")

def label_pat(n):
    return re.compile(r"\|\s*r" + str(n) + r"\s*\|")

# canonical pre-heal must hold ZERO target labels
for n in TARGETS:
    assert not label_pat(n).search(canon_text), f"FAIL: r{n} already in canonical (union no-op guard)"

# Face A extraction: attribute each root line to the EARLIEST-position target-label match
migrated = []  # (label, line_bytes) in file order
for ln in root_lines:
    best = None  # (pos, n)
    for n in TARGETS:
        m = label_pat(n).search(ln)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), n)
    if best is not None:
        migrated.append((best[1], ln.encode("utf-8")))

mig_labels = [n for n, _ in migrated]
seq = mig_labels[:]
assert seq == sorted(seq), f"migrated block not monotonic: {seq}"
from collections import Counter
per_label = Counter(mig_labels)
missing = [n for n in TARGETS if n not in per_label]
for n in missing:
    assert not any(label_pat(n).search(l) for l in root_lines), f"r{n} unexpectedly in root"
assert missing == [960, 961, 964, 966, 972, 973, 978, 979], f"missing set unexpected: {missing}"

block = b"".join(b for _, b in migrated)
block_sha = hashlib.sha256(block).hexdigest()

consolidated = (
    f"{now_iso} | r960/961/964/966/972/973/978/979(consolidated) | LEDGER BACKFILL MARKER (r985 heal): these 8 rounds "
    "have NO contemporaneous row in any face -- all were dead sessions absorbed by successor windows (r749 path-split "
    "family 3rd instance era: sibling rows were miswritten to the ROOT orphan face, migrated verbatim above; these 8 "
    "were never written at all). Authoritative per-round records = state-bm-c.json rXXX_absorb_note keys + closeout "
    "commit messages (git log). One-line faces: r960(dead: W229 prereg e485a0b3f committed, died pre-closeout) + "
    "r961(dead: W229 splice on disk, zero commit) -> absorbed by r962 (17th, estate 2ae8553e6); r964/r966 dead + "
    "splice-continuation window -> absorbed by r967 (19th, W231 estate via r966 commits); r972/r973 dead (W233 "
    "prereg/splice) -> absorbed by r974 (21st, estate 260217d39); r978/r979 dead absorb generations -> landed by r980 "
    "(22nd-generation). Rows NOT fabricated retroactively (fu-shu prohibition); zero information loss. "
    "| evidence: results/_r985bmc_ledger_heal_receipt.json | next: r985 row follows (canonical path restored)\n"
).encode("utf-8")

with open(CANON_FILE, "ab") as f:
    if canon_bytes and not canon_bytes.endswith(b"\n"):
        f.write(b"\n")
    f.write(block)
    f.write(consolidated)

# verify
canon_after_bytes = open(CANON_FILE, "rb").read()
expected = canon_bytes + (b"\n" if canon_bytes and not canon_bytes.endswith(b"\n") else b"") + block + consolidated
assert canon_after_bytes == expected, "canonical byte equation failed"
canon_after = canon_after_bytes.decode("utf-8")
for n, k in per_label.items():
    cnt = len(label_pat(n).findall(canon_after))
    assert cnt == k, f"r{n} count {cnt} != extracted {k} after heal"

# freeze pointer appended to ROOT orphan (additive only, rows stay per r645 zero-delete precedent)
pointer = (
    "\n> [r985 ledger-heal pointer 2026-10-14] Rounds r958-r984-set rows above were appended here by closeout "
    "scripts cloned from a ROOT-era template (r749/r780 path-split family, 3rd instance; canonical face = "
    "logs/iteration-loop/round_reports-bm-c.md per r645 surgery). Migrated rows verbatim-unioned to canonical this "
    "window; 8 never-written rounds covered by a consolidated backfill marker there. Receipt "
    "results/_r985bmc_ledger_heal_receipt.json. THIS FILE IS THE FROZEN r645 ORPHAN ARCHIVE - do NOT append round "
    "rows here; all closeout scripts must write logs/iteration-loop/round_reports-bm-c.md (r750 law).\n"
)
with open(ROOT_FILE, "ab") as f:
    f.write(pointer.encode("utf-8"))

receipt = {
    "op": "ledger path-split heal 3rd instance: 20-row verbatim union + 8-round consolidated backfill marker",
    "round": 985,
    "family": "r749 path-split / r780 heal precedent",
    "migrated_labels": sorted(per_label),
    "migrated_rows_total": len(migrated),
    "per_label_rows": dict(per_label),
    "migrated_bytes": len(block),
    "migrated_block_sha256": block_sha,
    "missing_rounds_consolidated": missing,
    "canonical_bytes_pre": len(canon_bytes),
    "canonical_bytes_post": len(expected),
    "root_bytes_pre": len(root_bytes),
    "root_bytes_post": len(root_bytes) + len(pointer.encode("utf-8")),
    "treasure_guard": "prescan rc3 honored -> line-level union carve-out",
    "zero_delete": True,
    "asserts": ["pre-heal canonical holds zero 958+ labels", "monotonic migrated block", "per-label count preserved post",
                "canonical byte equation", "missing absent from both faces"],
    "ts": now_iso,
}
json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"migrated_rows": len(migrated), "labels": sorted(per_label), "missing": missing, "block_sha256": block_sha[:16]}))
