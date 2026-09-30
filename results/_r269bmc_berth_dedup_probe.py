"""_r269bmc_berth_dedup_probe.py -- berth dedup guard probe (bm-c r269).

Origin case (live fire this probe mechanizes): INNOVATION-QUOTA-SLOT-11
(MOM-TIMING-P1, zoo #95) was berthed r267 + frozen r268 WITHOUT the berth
gate noticing that zoo #95 was ALREADY burned judged-negative 0/3 by
SLOT-3 HIGHERMOM-TIMING-P1 (r239 berth + r240 burn, 2026-09-29, same cells
MOM3/4/5, same frozen constants). Root causes: (1) the r240 harvest never
wrote the closure verdict back to the zoo row (zoo #95 showed
"frozen, unburned" to every later supply scan -- fixed by the r269
write-back); (2) the berth gate had no mechanical cross-check of prior
burned batches (results/innovation_quota/*.json) or same-zoo-row preregs.

Law face: RANDOM_LARGE_SAMPLE_LAW s5 (same method same params = no
re-run; reopen only via the frozen reopen channels) + O-1820
meaningfulness law (a re-burn of a known verdict = empty burn) +
anti-duplication iron law (user order "do not develop duplicates").

Probe logic (read-only, repo-tree scan):
  1. every research/INNOVATION_QUOTA_*_PREREG.md -> status class
     (retracted / closed-judged / active-frozen / active-berth) + zoo
     row ids referenced in its text (pattern "zoo #NN");
  2. every results/innovation_quota/*.json carrying trials_ledger.total
     = judged product -> its prereg file -> that prereg's zoo ids
     (the burned-zoo set);
  3. zoo row text marks: a row carrying a "judged 判决"/"judged-negative"
     mark = burned row; a burned row without "撤回"/retraction note next
     to a live berth declare = the pre-r269 hole face;
  4. FLAG = an ACTIVE (bertH/frozen, not judged, not retracted) prereg
     whose zoo ids intersect the burned-zoo set, or whose zoo row is a
     burned row. Zero flags = CLEAN.

Usage: run | selftest   (exit 0 clean; 1 = flag(s) found = berth-dup
risk, refuse the berth; 2 = mechanism error, report honestly).
Facts -> results/_r269bmc_berth_dedup_probe_facts.json (run mode).
"""
import argparse
import glob
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(ROOT, "research")
RESULTS_IQ = os.path.join(ROOT, "results", "innovation_quota")
ZOO_PATH = os.path.join(ROOT, "research", "shortline", "ASTYLE_ZOO.md")
OUT = os.path.join(ROOT, "results", "_r269bmc_berth_dedup_probe_facts.json")

PREREG_GLOB = "INNOVATION_QUOTA_*_PREREG.md"


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return ""


def zoo_ids_of_text(text):
    return {int(m) for m in re.findall(r"zoo\s*#(\d+)", text)}


def classify_status(banner, own_product_judged):
    """Status precedence: judged-product > retracted > closed marks >
    frozen > berth. own_product_judged = a judged product names this
    prereg file (self-closure beats a stale banner)."""
    if own_product_judged:
        return "closed-judged-product"
    if "RETRACTED" in banner:
        return "retracted"
    if ("已判决" in banner) or ("judged-negative" in banner) or \
            ("关单" in banner):
        return "closed-judged-banner"
    if "FROZEN" in banner:
        return "active-frozen"
    if "BERTH" in banner:
        return "active-berth"
    return "unknown"


def prereg_banner(path):
    """First status line: the '> **状态' block head (first ~1200 chars
    of the file carry it in every in-tree prereg)."""
    head = _read(path)[:1600]
    for line in head.splitlines():
        if "状态" in line and line.lstrip().startswith(">"):
            return line
    return ""


def scan(research_dir, results_dir, zoo_path):
    """Read-only scan -> (faces dict, flags list). No writes."""
    faces = {"preregs": {}, "judged_products": {}, "zoo_rows": {},
             "burned_zoo_ids": sorted(set())}
    # 1. judged products + their preregs (the burned-zoo authority)
    judged_files = set()
    burned = set()
    for prod in sorted(glob.glob(os.path.join(results_dir, "*.json"))):
        try:
            with open(prod, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        led = d.get("trials_ledger") or {}
        if led.get("total") is None:
            continue
        m = re.search(r"research/([A-Za-z0-9_\-]+\.md)", str(d.get("prereg", "")))
        pref = m.group(1) if m else None
        zids = zoo_ids_of_text(_read(os.path.join(research_dir, pref))) \
            if pref and os.path.exists(os.path.join(research_dir, pref)) \
            else set()
        judged_files.add(pref)
        burned |= zids
        faces["judged_products"][os.path.basename(prod)] = {
            "batch": d.get("batch"), "prereg": pref, "zoo_ids": sorted(zids)}
    # 2. preregs status + zoo ids
    for pre in sorted(glob.glob(os.path.join(research_dir, PREREG_GLOB))):
        name = os.path.basename(pre)
        banner = prereg_banner(pre)
        cls = classify_status(banner, name in judged_files)
        zids = zoo_ids_of_text(_read(pre))
        faces["preregs"][name] = {"status_class": cls, "zoo_ids": sorted(zids)}
    faces["burned_zoo_ids"] = sorted(burned)
    # 3. zoo row marks (burn mark + retraction mark per id)
    zoo_text = _read(zoo_path)
    rows = {}
    for line in zoo_text.splitlines():
        m = re.match(r"\|\s*(\d{1,3})\s*\|", line)
        if not m:
            continue
        rid = int(m.group(1))
        burned_row = ("judged 判决" in line) or ("judged-negative" in line)
        rows[rid] = {"burned_mark": burned_row,
                     "retracted_mark": ("撤回" in line) or ("RETRACTED" in line)}
    faces["zoo_rows"] = {str(k): v for k, v in rows.items() if v["burned_mark"]}
    # 4. flags: active prereg over a burned zoo id / burned zoo row
    flags = []
    for name, f in faces["preregs"].items():
        if not f["status_class"].startswith("active"):
            continue
        for rid in f["zoo_ids"]:
            why = []
            if rid in burned:
                why.append(f"zoo #{rid} already burned by a judged batch")
            row = rows.get(rid)
            if row and row["burned_mark"] and not row["retracted_mark"]:
                why.append(f"zoo #{rid} row carries a burn verdict without "
                           "retraction")
            if why:
                flags.append({"prereg": name, "zoo_id": rid, "why": why})
    return faces, flags


def cmd_run():
    try:
        faces, flags = scan(RESEARCH, RESULTS_IQ, ZOO_PATH)
    except Exception as ex:
        print(f"GATE-REFUSE(exit2): probe mechanism error: {ex}")
        return 2
    facts = {
        "probe": "berth dedup guard (r269) -- active prereg x burned-zoo "
                 "cross-check + zoo burn-mark audit",
        "machine": "bm-c", "round": "r269",
        "origin_case": "INNOVATION-QUOTA-SLOT-11 MOM-TIMING-P1 (zoo #95) "
                       "intercepted pre-burn r269: same family/cells/"
                       "constants already judged-negative 0/3 by SLOT-3 "
                       "HIGHERMOM-TIMING-P1 (r240); W3 s7 reopen channels "
                       "zero-hit; prereg flipped RETRACTED, zoo row "
                       "write-back landed same window",
        "law_refs": ["RANDOM_LARGE_SAMPLE_LAW s5 (same method same params "
                     "= no re-run)", "O-1820 meaningfulness (known-verdict "
                     "re-burn = empty burn)", "anti-dup iron law"],
        "scan": faces,
        "flags": flags,
        "verdict": "CLEAN" if not flags else f"FLAG x{len(flags)}",
    }
    with open(OUT + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(OUT + ".tmp", OUT)
    print(f"berth_dedup_probe: {facts['verdict']} "
          f"(preregs={len(faces['preregs'])} judged_products="
          f"{len(faces['judged_products'])} burned_zoo_ids="
          f"{faces['burned_zoo_ids']}) -> {OUT}")
    for fl in flags:
        print(f"  FLAG: {fl['prereg']} zoo #{fl['zoo_id']}: {fl['why']}")
    return 1 if flags else 0


def cmd_selftest():
    tmp = tempfile.mkdtemp(prefix="berth_dedup_probe_st_")
    ok = []
    try:
        rd = os.path.join(tmp, "research")
        rs = os.path.join(tmp, "results")
        os.makedirs(rd); os.makedirs(rs)
        zoo = os.path.join(tmp, "zoo.md")
        # fixture: judged W-A (zoo #901) + active frozen W-B (zoo #901)
        # = the interception case; clean W-C (zoo #902); retracted W-D
        # (zoo #901) = no flag post-retraction.
        with open(os.path.join(rd, "INNOVATION_QUOTA_WA_PREREG.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("> 状态：已判决关单（judged-negative 0/3）\n zoo #901\n")
        with open(os.path.join(rs, "WA-PROD.json"), "w", encoding="utf-8") as fh:
            json.dump({"batch": "WA", "prereg": "research/"
                        "INNOVATION_QUOTA_WA_PREREG.md",
                       "trials_ledger": {"prev_total": 1, "total": 2}}, fh)
        with open(os.path.join(rd, "INNOVATION_QUOTA_WB_PREREG.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("> 状态：FROZEN——冻结于跑前\n zoo #901\n")
        with open(os.path.join(rd, "INNOVATION_QUOTA_WC_PREREG.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("> 状态：FROZEN——冻结于跑前\n zoo #902\n")
        with open(os.path.join(rd, "INNOVATION_QUOTA_WD_PREREG.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("> 状态：RETRACTED（撤回）原 FROZEN\n zoo #901\n")
        with open(zoo, "w", encoding="utf-8") as fh:
            fh.write("| 900 | clean row | a | b |\n"
                     "| 901 | burned+retracted row | a | judged 判决="
                     "judged-negative 族关单 + 撤回 |\n"
                     "| 902 | clean row | a | b |\n")
        faces, flags = scan(rd, rs, zoo)
        names = {fl["prereg"]: fl for fl in flags}
        ok.append(("dup case caught (active frozen over burned zoo #901)",
                   "INNOVATION_QUOTA_WB_PREREG.md" in names))
        ok.append(("clean prereg (zoo #902) not flagged",
                   "INNOVATION_QUOTA_WC_PREREG.md" not in names))
        ok.append(("retracted prereg (zoo #901) not flagged",
                   "INNOVATION_QUOTA_WD_PREREG.md" not in names))
        ok.append(("judged prereg itself not flagged (self-closure)",
                   "INNOVATION_QUOTA_WA_PREREG.md" not in names))
        ok.append(("burned set = {901}", faces["burned_zoo_ids"] == [901]))
        # zoo-row-only hole face: burn mark present, berth active, and
        # the burned id discovered via the ROW (not via a judged
        # prereg zoo-ref) -- row mark without retraction = flag path
        with open(os.path.join(rd, "INNOVATION_QUOTA_WE_PREREG.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("> 状态：BERTH\n zoo #903\n")
        with open(zoo, "a", encoding="utf-8") as fh:
            fh.write("| 903 | burned row no retraction | a | judged 判决="
                     "judged-negative 族关单 + 泊位 declare |\n")
        _, flags2 = scan(rd, rs, zoo)
        ok.append(("zoo-row burn mark (no retraction) flags active berth",
                   any(fl["prereg"] == "INNOVATION_QUOTA_WE_PREREG.md"
                       for fl in flags2)))
        # staged-product (no verdict) does not count as judged
        with open(os.path.join(rs, "WF-STAGED.json"), "w", encoding="utf-8") as fh:
            json.dump({"batch": "WF", "trials_ledger": {}}, fh)
        faces3, _ = scan(rd, rs, zoo)
        ok.append(("staged product (no ledger total) not in judged set",
                   "WF-STAGED.json" not in faces3["judged_products"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n_ok = sum(1 for _, v in ok if v)
    print(f"berth_dedup_probe selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return cmd_selftest() if a.cmd == "selftest" else cmd_run()


if __name__ == "__main__":
    sys.exit(main())
