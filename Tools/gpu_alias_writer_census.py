"""Every spelling of one GPU number on the fleet faces, who writes it, and which names lie.

Question this face answers
--------------------------
`fleet: GPU face self-consistent on heartbeat` went red in round 2131 and again in round 2132
(76 MiB spread inside the FREE family: gpu_free_mib high, gpu_free_vram_mib low, 19 keys in the
family). Both rounds carried it, and a carried red is the r1789 failure mode -- readers learn to
skip the leg and then miss the real defect that stands next to it.

The leg could only say "these two numbers disagree". This face says *why* a face can disagree at
all: thirty-odd aliases of free/used/total are written by whoever touched the heartbeat last, and
a second writer that probes nvidia-smi at a different moment leaves half the aliases at its own
snapshot. It also names the spelling-table defect r2131 found by hand: keys whose name promises
GiB (`gpu_free_gib`, `vram_used_gib`) while the toolchain reads and writes MiB, so writer and
checker agree with each other and a reader is told 13752 GiB.

Reuse, not rewrite
------------------
Family/unit resolution, the pair/prose readings, `audit()` and the live nvidia-smi probe all come
from Tools/gpu_face.py (r1909). This module adds only what that tool does not answer: writer
attribution and the name-vs-unit question.

Read-only by design: the only file it writes is results/gpu_alias_writer_census.json, plus the
research page under --write. It never touches a heartbeat.

Recomputable on its own:
  $ python Tools/gpu_alias_writer_census.py
  $ python Tools/gpu_alias_writer_census.py --check      # rc 3 + STALE when a face or writer moved
  $ python Tools/gpu_alias_writer_census.py --selftest
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import gpu_face as gf  # noqa: E402  (same toolchain that writes and audits these faces)

OUT_PATH = os.path.join(BASE, "results", "gpu_alias_writer_census.json")
DOC_PATH = os.path.join(BASE, "research", "GPU_ALIAS_WRITER_CENSUS.md")
FACES = os.path.join(BASE, "fleet", "machines", "*.json")

# the two files that own the aliases; every other mention is a candidate second writer
OWNERS = ("Tools/gpu_face.py", "Tools/heartbeat_write.py")
# one-off closeout helpers (_r1234bmc_*) and selftests write synthetic faces in temp dirs
NOISE = re.compile(r"(^_r\d|selftest|_probe|heartbeat_alias_audit|gpu_alias_writer_census)")


def _now():
    return dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _local_machine():
    """This host's fleet id. The only face a local nvidia-smi is allowed to judge."""
    try:
        with open(os.path.join(BASE, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def load_faces(pattern=FACES):
    out = {}
    for p in sorted(glob.glob(pattern)):
        mid = os.path.splitext(os.path.basename(p))[0]
        try:
            with open(p, encoding="utf-8") as fh:
                out[mid] = (p, json.load(fh))
        except Exception as exc:  # a half-written heartbeat is a finding, not a crash
            out[mid] = (p, {"_load_error": str(exc)[:200]})
    return out


def inventory(face):
    """[(key, family, unit, value_mib)] for every GPU-memory spelling the face carries."""
    rows = []
    for k, v in (face or {}).items():
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            fam, unit = gf.gpu_mem_family(k)
            if fam:
                rows.append({"key": k, "family": fam, "unit": unit,
                             "value_mib": round(gf._mb(k, v), 1), "value_raw": v,
                             "nested": False})
        elif isinstance(v, dict):
            for sk, sv in v.items():
                if isinstance(sv, bool) or not isinstance(sv, (int, float)):
                    continue
                fam, unit = gf.gpu_mem_family("%s_%s" % (k, sk))
                if fam:
                    rows.append({"key": "%s.%s" % (k, sk), "family": fam, "unit": unit,
                                 "value_mib": round(sv * 1024.0 if unit == "gb" else sv, 1),
                                 "value_raw": sv, "nested": True})
    return rows


GIB_CEILING = 512.0  # no single GPU in this fleet offers more than half a terabyte of VRAM


def unit_lies(rows):
    """`*_gib` spellings carrying a number that cannot be GiB.

    r2149 fixed the RULE that put MiB numbers under GiB names (`gpu_mem_family` now resolves
    `gib` to gb, and audit() walks every spelling on the face instead of a tabulated list).
    The numbers already written do not fix themselves -- a heartbeat is merge-only until a
    probe runs -- and a reader that trusts the name now multiplies by 1024, so 13752 would be
    read as 13,752 GiB free. This stays as the residue watch: any `_gib` key above any card's
    capacity is a MiB number waiting for that machine's next `gpu_face apply`.
    """
    out = []
    for r in rows:
        toks = [t for t in r["key"].lower().split(".")[-1].split("_") if t]
        if not toks:
            continue
        if toks[-1] == "gib" and r["unit"] == "gb" and float(r["value_raw"]) > GIB_CEILING:
            out.append({"key": r["key"], "value": r["value_raw"],
                        "implied_reading": "%s GiB" % r["value_raw"],
                        "actual_reading": "%s MiB (%.1f GiB) -- a probe must rewrite it"
                                          % (r["value_raw"], float(r["value_raw"]) / 1024.0)})
    return out


def code_mentions(keys, roots=("Tools", "scripts")):
    """{key: [repo-relative file, ...]} in one pass over the two code trees."""
    keys = [k for k in keys if k]
    if not keys:
        return {}
    pat = re.compile("|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True)))
    hits = {k: [] for k in keys}
    for root in roots:
        for p in glob.glob(os.path.join(BASE, root, "*.py")):
            rel = os.path.relpath(p, BASE).replace("\\", "/")
            try:
                with open(p, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except Exception:
                continue
            found = set(pat.findall(text))
            for k in found:
                if k in hits:
                    hits[k].append(rel)
    return {k: sorted(v) for k, v in hits.items()}


def second_writers(mentions):
    """Keys a file other than the two owners also spells -- the ones that can go stale alone."""
    out = {}
    for k, files in mentions.items():
        others = [f for f in files if f not in OWNERS and not NOISE.search(os.path.basename(f))]
        if others:
            out[k] = others
    return out


def census(pattern=FACES, live=True):
    faces = load_faces(pattern)
    per_machine = {}
    all_keys = set()
    for mid, (path, face) in faces.items():
        rows = inventory(face)
        all_keys.update(r["key"] for r in rows)
        per_machine[mid] = {
            "path": os.path.relpath(path, BASE).replace("\\", "/"),
            "keys": len(rows),
            "audit": gf.audit(face) if "_load_error" not in face else [],
            "load_error": face.get("_load_error"),
            "families": {},
        }
        for fam in ("free", "used", "total"):
            vals = [r for r in rows if r["family"] == fam]
            if not vals:
                continue
            hi = max(vals, key=lambda r: r["value_mib"])
            lo = min(vals, key=lambda r: r["value_mib"])
            per_machine[mid]["families"][fam] = {
                "n_keys": len(vals),
                "spread_mib": round(hi["value_mib"] - lo["value_mib"], 1),
                "high": hi["key"], "low": lo["key"],
                "high_mib": hi["value_mib"], "low_mib": lo["value_mib"],
                "within_tolerance": (hi["value_mib"] - lo["value_mib"]) < gf.TOL_MIB,
            }

    mentions = code_mentions(sorted(all_keys))
    second = second_writers(mentions)
    lies = {}
    for mid, (path, face) in faces.items():
        rows = inventory(face)
        got = unit_lies(rows)
        if got:
            lies[mid] = got

    # r2134: one probe, one machine. nvidia-smi on this box says nothing about another box's
    # card (12 GB vs 16 GB here), so judging every face against it would print a 12,812 MiB
    # "staleness" that is really just a different GPU -- the exact class of lie this face audits.
    local = _local_machine()
    probe = None
    if live:
        try:
            probe = gf.probe_live()
        except Exception as exc:
            probe = {"_error": str(exc)[:200]}
    live_free = None
    if probe and "total_mib" in probe:
        live_free = probe["total_mib"] - probe["used_mib"]

    stale_now = {}
    if live_free is not None and local in faces:
        rows = [r for r in inventory(faces[local][1]) if r["family"] == "free"]
        off = [{"key": r["key"], "value_mib": r["value_mib"],
                "delta_mib": round(r["value_mib"] - live_free, 1)}
               for r in rows if abs(r["value_mib"] - live_free) >= gf.TOL_MIB]
        if off:
            stale_now[local] = off

    findings = sum(len(v["audit"]) for v in per_machine.values())
    if findings:
        verdict = "INCONSISTENT"
    elif lies:
        verdict = "NAMES_LIE"
    elif second:
        verdict = "SECOND_WRITER_RISK"
    elif not per_machine:
        verdict = "NO_FACE"
    else:
        verdict = "CONSISTENT"

    parts = []
    if findings:
        for mid, v in per_machine.items():
            for a in v["audit"]:
                parts.append("%s %s family spreads %.1f MiB (%s vs %s)"
                             % (mid, a.get("family"), a.get("spread_mib", 0),
                                a.get("high"), a.get("low")))
    if lies:
        k = sum(len(v) for v in lies.values())
        parts.append("%d GiB-named key(s) carry MiB numbers, so a reader of the face is told "
                     "a number that cannot be GiB" % k)
    if second:
        parts.append("%d alias(es) are also spelled outside gpu_face/heartbeat_write, so one of "
                     "them can age alone" % len(second))
    if not parts:
        parts.append("every GPU spelling on the fleet faces agrees within %.0f MiB and only the "
                     "owning tools spell them" % gf.TOL_MIB)

    return {
        "face": "gpu_alias_writer_census",
        "question": ("which spellings of one GPU number live on the fleet faces, which code can "
                     "write each, and which names promise a unit they do not carry?"),
        "generated": _now(),
        "verdict": verdict,
        "sentence": "; ".join(parts),
        "live_probe": probe,
        "live_free_mib": live_free,
        "live_probe_machine": local,
        "machines": per_machine,
        "names_lie": lies,
        "second_writer_risk": second,
        "stale_against_live_now": stale_now,
        "tolerance_mib": gf.TOL_MIB,
        "owners": list(OWNERS),
    }


def _inputs_digest(pattern=FACES, roots=("Tools", "scripts")):
    """Byte digest of every face and code file this census reads (r1311: bytes, not dates)."""
    h = hashlib.sha256()
    for p in sorted(glob.glob(pattern)):
        with open(p, "rb") as fh:
            h.update(fh.read())
    for root in roots:
        for p in sorted(glob.glob(os.path.join(BASE, root, "*.py"))):
            with open(p, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()


def check(out_path=OUT_PATH):
    """Re-derive against the faces on disk. A face or writer that moved is STALE, not wrong."""
    if not os.path.exists(out_path):
        return {"ok": False, "problems": ["STALE: face missing -- %s has never been written"
                                          % os.path.relpath(out_path, BASE)]}
    with open(out_path, encoding="utf-8") as fh:
        prev = json.load(fh)
    problems = []
    if prev.get("inputs_digest") != _inputs_digest():
        problems.append("STALE: a heartbeat or a code tree this census reads has been rewritten "
                        "since %s" % prev.get("generated"))
    now = census(live=False)
    prev_without_live = {k: v for k, v in prev.items()
                         if k not in ("inputs_digest", "live_probe", "live_free_mib",
                                      "stale_against_live_now", "generated", "elapsed_sec")}
    now_without_live = {k: v for k, v in now.items()
                        if k not in ("inputs_digest", "live_probe", "live_free_mib",
                                     "stale_against_live_now", "generated", "elapsed_sec")}
    if prev_without_live != now_without_live:
        problems.append("CHECK FAILED: same inputs, different inventory -- the face does not "
                        "reproduce (verdict %s -> %s)" % (prev.get("verdict"), now.get("verdict")))
    return {"ok": not problems, "problems": problems, "checked_at": _now()}


def write_doc(doc, path=DOC_PATH):
    m = doc["machines"]
    L = []
    L.append("# GPU alias writer census\n")
    L.append("_generated %s · verdict **%s**_\n" % (doc["generated"], doc["verdict"]))
    L.append("%s\n" % doc["sentence"])
    L.append("## Why this face exists\n")
    L.append("`fleet: GPU face self-consistent on heartbeat` has been carried red twice (r2131, "
             "r2132) with a 76 MiB spread among 19 FREE aliases. The leg can only say two numbers "
             "disagree; it cannot say who put them there. A red that nobody can act on is a red "
             "readers learn to skip (r1789), so this face names the writer and the spelling.\n")
    L.append("## Faces read\n")
    L.append("| machine | keys | free spread (MiB) | high | low | audit findings |")
    L.append("|---|---|---|---|---|---|")
    for mid, v in m.items():
        f = v["families"].get("free") or {}
        L.append("| %s | %d | %s | %s | %s | %d |"
                 % (mid, v["keys"], f.get("spread_mib", "-"), f.get("high", "-"),
                    f.get("low", "-"), len(v["audit"])))
    L.append("")
    # a spread the tolerance rejects is only actionable once the two numbers are on the page
    for mid, v in m.items():
        f = v["families"].get("free") or {}
        if f and not f.get("within_tolerance"):
            L.append("**%s** carries two free-VRAM readings %s MiB apart: `%s` says %s MiB and "
                     "`%s` says %s MiB. A reader of that heartbeat has no way to know which half "
                     "is the GPU and which half is an older probe left behind.\n"
                     % (mid, f["spread_mib"], f["high"], f.get("high_mib"), f["low"],
                        f.get("low_mib")))
        u = v["families"].get("used") or {}
        if u and not u.get("within_tolerance"):
            L.append("**%s** likewise carries used readings %s MiB apart (`%s` %s MiB vs `%s` "
                     "%s MiB).\n"
                     % (mid, u["spread_mib"], u["high"], u.get("high_mib"),
                        u["low"], u.get("low_mib")))
    if doc["names_lie"]:
        L.append("## Names that promise GiB and carry MiB\n")
        L.append("The toolchain resolves the unit from the spelling, so a `*_gib` key is read as "
                 "MiB and writer and checker agree with each other. A reader is handed the second "
                 "column.\n")
        L.append("| machine | key | on the face | what it actually is |")
        L.append("|---|---|---|---|")
        for mid, rows in doc["names_lie"].items():
            for r in rows:
                L.append("| %s | `%s` | %s | %s |" % (mid, r["key"], r["implied_reading"],
                                                      r["actual_reading"]))
        L.append("")
    if doc["second_writer_risk"]:
        L.append("## Aliases spelled outside the owning tools\n")
        L.append("`Tools/gpu_face.py` and `Tools/heartbeat_write.py` restate every alias from one "
                 "probe. A file below also spells the key: if it writes its own probe into the "
                 "heartbeat, half the family moves and the other half keeps the old snapshot.\n")
        L.append("| key | other files |")
        L.append("|---|---|")
        for k, files in sorted(doc["second_writer_risk"].items()):
            L.append("| `%s` | %s |" % (k, ", ".join("`%s`" % f for f in files[:4])))
        L.append("")
    if doc.get("live_free_mib") is not None:
        L.append("## Against the live probe\n")
        L.append("nvidia-smi on **%s** right now: %s MiB free of %s MiB. Only that face is judged "
                 "against it -- a probe on this box says nothing about another box's card, which "
                 "is why the other machines are absent from this section rather than marked "
                 "stale.\n"
                 % (doc.get("live_probe_machine"), doc["live_free_mib"],
                    doc["live_probe"].get("total_mib")))
        if doc["stale_against_live_now"]:
            for mid, rows in doc["stale_against_live_now"].items():
                L.append("- **%s**: %s" % (mid, ", ".join(
                    "`%s` %+.1f MiB" % (r["key"], r["delta_mib"]) for r in rows[:6])))
        else:
            L.append("- every free alias on every face is within %.0f MiB of the live probe.\n"
                     % doc["tolerance_mib"])
        L.append("")
    L.append("## Fix order (for a contention-free round)\n")
    L.append("1. Drop or rename the `*_gib` spellings: a key that cannot be read as its own name "
             "is a trap regardless of who writes it (`gpu_face.key_unit` is the single place to "
             "change, and `restate()` will follow).\n")
    L.append("2. Move any second writer onto `heartbeat_write.write()` instead of writing GPU keys "
             "itself, so one probe per round owns the whole family.\n")
    L.append("3. Only then re-run the leg: while a second writer exists the spread can reappear "
             "on any round, which is why it was carried twice rather than fixed once.\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    return path


def selftest():
    ok = []

    def t(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    # family + unit resolution is inherited, but the census depends on it: pin the contract
    t("gpu_free_mib reads as free/mib", gf.gpu_mem_family("gpu_free_mib") == ("free", "mib"))
    t("gpu_vram_free_gb reads as free/gb", gf.gpu_mem_family("vram_free_gb") == ("free", "gb"))
    t("gpu_free_gib resolves to gb (name honoured since r2149)",
      gf.gpu_mem_family("gpu_free_gib") == ("free", "gb"))

    rows = inventory({"gpu_free_mib": 13752, "vram_free_gb": 13.4,
                      "gpu_free_gib": 13752, "gpu": {"free_gb": 13.4, "used_mib": 2632},
                      "ram_free_gb": 12.0})
    keys = [r["key"] for r in rows]
    t("inventory skips RAM keys", "ram_free_gb" not in keys)
    t("inventory reads nested GPU block", "gpu.free_gb" in keys and "gpu.used_mib" in keys)
    t("inventory normalises gb to MiB",
      [r["value_mib"] for r in rows if r["key"] == "vram_free_gb"] == [13721.6])

    lies = unit_lies(rows)
    t("unit_lies names only the gib spelling",
      [r["key"] for r in lies] == ["gpu_free_gib"], str(lies))
    t("unit_lies shows the size of the lie",
      lies and lies[0]["implied_reading"] == "13752 GiB")
    healed = inventory({"gpu_free_mib": 13752, "gpu_free_gib": 13.4})
    serviceable = [r["key"] for r in unit_lies(healed)]
    t("unit_lies is silent once the probe rewrote the key in GiB",
      serviceable == [], str(serviceable))

    # a face two writers touched: the family disagrees, and audit must see it
    bad = {"gpu_free_mib": 13676, "gpu_free_vram_mib": 13752, "gpu_used_mib": 2632,
           "gpu_mem_total_mib": 16384}
    t("audit sees the 76 MiB split", gf.audit(bad) != [])
    good = {"gpu_free_mib": 13752, "gpu_free_vram_mib": 13752, "gpu_used_mib": 2632,
            "gpu_mem_total_mib": 16384}
    t("audit passes a single-probe face", gf.audit(good) == [])

    # writer attribution: the owner does not count as a second writer
    sw = second_writers({"gpu_free_mib": ["Tools/gpu_face.py", "Tools/heartbeat_write.py"]})
    t("owners are not second writers", sw == {})
    sw = second_writers({"gpu_free_vram_mib": ["Tools/gpu_face.py", "Tools/_r1070bmc_close.py"]})
    t("a closeout helper is noise, not a writer", sw == {})
    sw = second_writers({"gpu_free_vram_mib": ["Tools/gpu_face.py", "Tools/some_loop.py"]})
    t("a live tool is flagged", sw == {"gpu_free_vram_mib": ["Tools/some_loop.py"]})

    # the verdict must move with the evidence, not stay on one word
    t("verdict is one of the five states",
      census(pattern=os.path.join(BASE, "no_such_dir", "*.json"), live=False)["verdict"] == "NO_FACE")
    # r2134: a local probe must never be used to call another machine's card stale
    doc_live = census(live=True)
    t("live probe judges one machine only",
      doc_live["live_probe_machine"] in (None,) or
      set(doc_live["stale_against_live_now"]) <= {doc_live["live_probe_machine"]},
      str(sorted(doc_live["stale_against_live_now"])))

    # check() must be able to say STALE rather than quietly reproduce
    tmp = os.path.join(BASE, "results", "_gpu_alias_census_selftest.json")
    doc = census(live=False)
    doc["inputs_digest"] = "deadbeef"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    try:
        r = check(tmp)
        t("check calls a moved input STALE", not r["ok"] and any("STALE" in p for p in r["problems"]),
          str(r.get("problems")))
    finally:
        os.remove(tmp)

    bad_legs = [n for n, c, _ in ok if not c]
    for n, c, d in ok:
        print("[%s] %s%s" % ("PASS" if c else "FAIL", n, (" | " + d) if (d and not c) else ""))
    print("\nSummary: %d/%d PASS" % (len(ok) - len(bad_legs), len(ok)))
    return 0 if not bad_legs else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--no-live", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check:
        r = check()
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["ok"] else 3

    t0 = dt.datetime.now()
    doc = census(live=not args.no_live)
    doc["inputs_digest"] = _inputs_digest()
    doc["elapsed_sec"] = round((dt.datetime.now() - t0).total_seconds(), 2)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("%s | %s" % (doc["verdict"], doc["sentence"]))
    if args.write:
        print("wrote %s" % os.path.relpath(write_doc(doc), BASE))
    print("wrote %s (%.1fs)" % (os.path.relpath(OUT_PATH, BASE), doc["elapsed_sec"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
