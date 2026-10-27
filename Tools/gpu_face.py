# -*- coding: utf-8 -*-
"""gpu_face.py -- one authoritative GPU face for fleet/machines/<id>.json.

WHY (O-20261026-0810-bm-a 4: "bm-c heartbeat gpu_util_pct stuck at 0 while the
GPU is actually at 100%"):
  The heartbeat is merge-only by law (Tools/heartbeat_write.py, r1110), so every
  round that ever wrote a GPU field left its key behind. A dozen per-round closeout
  scripts each invented their own spelling -- gpu_free_vram_mb / gpu_free_mib /
  gpu_idle_vram_gb / gpu_free_gb / gpu_used_mib / gpu_vram_free_mb -- and each
  wrote it ONCE, at that round's reading. The live face now carries 25 GPU keys
  whose values disagree by up to 13 GB (free 13.72 GB beside free 1.31 GB beside
  781 MB), plus gpu_util_pct pinned to a literal 0 by _r1029bmc_close.py. A fleet
  audit reading any one of those keys is reading a random round's snapshot, not
  the machine. That is not a stale number: it is an unowned face.

LAW this tool enforces:
  1. ONE PROBE: every GPU field comes from one nvidia-smi call, so the fields are
     consistent with each other by construction rather than by hope.
  2. ONE SPELLING TABLE: the canonical keys plus every legacy alias observed on
     the live face are written together from the same probe, so a consumer cannot
     read the wrong generation of the face.
  3. AUDIT IS A PURE FUNCTION: audit(face) returns the disagreements; it is what
     the selftest pins, and it never repairs anything on its own.
  4. FAILURE IS LOUD: no nvidia-smi / unparsable output -> rc 2 and NOTHING is
     written (a heartbeat with a fresh ts and an invented GPU number is worse than
     an old one).

CLI:
  python Tools/gpu_face.py probe      # json probe only, no writes
  python Tools/gpu_face.py audit      # disagreements on the live heartbeat
  python Tools/gpu_face.py apply      # probe -> heartbeat (merge-only writer)
  python Tools/gpu_face.py selftest
Exit: 0 ok, 2 probe/mechanism fault, 3 face refused by writer.
"""
from __future__ import unicode_literals

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# free/used families: (canonical value selector, unit divisor)
FREE_KEYS = (
    "gpu_free_mib", "gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
    "gpu_free_mem_mib", "gpu_free_vram_gb", "gpu_free_gb", "gpu_idle_mb",
    "gpu_idle_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
    # r1278: the same words in the other order. apply() covered the face but left
    # these two at a random round's snapshot, which is how a fleet audit could read
    # 2008 MiB used beside a 1354 MiB probe -- a half-owned face is still unowned.
    "gpu_vram_free_mb", "gpu_vram_free_mib", "gpu_vram_free_gb",
    # r1299: a round wrote the spelling with NO gpu prefix. It sat outside both the
    # table and the unowned detector (which keyed on a 'gpu' prefix), so the smoke
    # face counted 14 keys and disagreed by 242 MiB while nothing pointed at the key
    # responsible. A GPU-memory key is owned by this tool whatever its prefix.
    "free_vram_mb",
    # r1169: the GB spellings of the same two orders were still outside the table,
    # so a heartbeat carrying free_vram_gb / vram_free_gb audited as "unowned" and
    # could keep a random round's number while every MiB sibling was rewritten.
    "free_vram_gb", "vram_free_gb",
)

# Keys whose value is a formatted pair rather than a scalar (r1299: the live face
# carried gpu_free = "14111, 16384" -- free, total -- written once by an inline
# round script and never refreshed, i.e. invisible to every numeric audit).
PAIR_FREE_TOTAL = ("gpu_free",)
USED_KEYS = (
    "gpu_used_mib", "gpu_used_mb", "gpu_used_vram_mb", "gpu_used_vram_mib",
    "gpu_mem_used_mib", "gpu_vram_used_mb", "gpu_vram_used_mib",
)
TOTAL_KEYS = ("gpu_mem_total_mib", "gpu_total_vram_mib")
GB_KEYS = ("gpu_free_gb", "gpu_free_vram_gb", "free_vram_gb", "vram_free_gb")

# r1177: the spelling table has now been widened by ENUMERATION three times (the
# prefix rule r1299, the RAM list r1169, the free GB pair r1169b) and each time a
# new spelling landed on the live face with a random round's number. The durable
# form is to derive family and unit from the tokens, then let apply() restate
# whatever spelling the face actually carries.
_FILLER_TOKENS = {"gpu", "vram", "mem", "memory", "v", "mb", "mib", "gb"}


def gpu_mem_family(k):
    """('free'|'used'|'total', 'gb'|'mib') for a GPU-memory spelling, else (None, None)."""
    if not gpu_mem_key(k):
        return (None, None)
    toks = [t for t in k.lower().split("_") if t]
    if not toks:
        return (None, None)
    unit = "gb" if toks[-1] == "gb" else "mib"
    body = set(toks) - _FILLER_TOKENS
    if "total" in body:
        return ("total", unit)
    if "used" in body:
        return ("used", unit)
    if "free" in body or "idle" in body:
        return ("free", unit)
    return (None, None)


def restate(face, fields):
    """Fields for every numeric GPU-memory spelling the face already carries.

    apply() writes the canonical aliases; this covers the aliases nobody tabulated
    (vram_used_gb was the live one) so a spelling cannot age just by being new.
    String-valued keys are left alone: the '<free>, <total>' pair has its own leg.
    """
    total = fields["gpu_mem_total_mib"]
    used = fields["gpu_used_mib"]
    value = {"free": total - used, "used": used, "total": total}
    extra = {}
    for k, v in face.items():
        if k in fields or k in PAIR_FREE_TOTAL:
            continue
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        fam, unit = gpu_mem_family(k)
        if fam is None:
            continue
        extra[k] = round(value[fam] / 1024.0, 1) if unit == "gb" else value[fam]
    return extra

# one disagreement of this size or more is a defect (probe granularity is 1 MiB)
TOL_MIB = 64.0


def key_unit(k):
    """'gb' or 'mib' for a GPU-memory spelling, derived from the tokens.

    r1311: `gpu_vram_free_gb` was on FREE_KEYS but not on GB_KEYS, so apply() wrote the
    MiB number 15099 into a key whose name promises GB, and audit() read it back as MiB --
    writer and checker agreed with each other and the reader got a face that said 15099 GB.
    The unit is in the spelling, so ask the spelling instead of maintaining a second list.
    """
    _fam, unit = gpu_mem_family(k)
    if unit:
        return unit
    return "gb" if k in GB_KEYS else "mib"


def _mb(key, value):
    """Value in MiB for a family key (whatever unit its name promises)."""
    return float(value) * 1024.0 if key_unit(key) == "gb" else float(value)


def parse_smi(text):
    """Parse 'util, used, total' CSV. Raises ValueError on anything else."""
    line = [l for l in (text or "").splitlines() if l.strip()]
    if not line:
        raise ValueError("empty nvidia-smi output")
    nums = [p.strip() for p in line[0].split(",")]
    if len(nums) < 3:
        raise ValueError("expected 3 CSV fields, got %r" % line[0])
    util = float(nums[0].replace("%", ""))
    used = int(float(nums[1].replace("MiB", "").strip()))
    total = int(float(nums[2].replace("MiB", "").strip()))
    if total <= 0 or used < 0 or used > total:
        raise ValueError("incoherent memory: used=%d total=%d" % (used, total))
    return {"util_pct": util, "used_mib": used, "total_mib": total}


def _run_smi(smi=None):
    exe = smi or os.environ.get("GPU_FACE_SMI") or "nvidia-smi"
    if exe != "nvidia-smi" and not os.path.exists(exe):
        raise RuntimeError("nvidia-smi not found: %s" % exe)
    out = subprocess.run(
        [exe, "--query-gpu=utilization.gpu,memory.used,memory.total",
         "--format=csv,noheader"],
        capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError("nvidia-smi rc=%d: %s"
                           % (out.returncode, (out.stderr or "").strip()[:120]))
    return out.stdout


def fields_from(probe, stamp):
    """Canonical + legacy alias fields, all from one probe."""
    free = probe["total_mib"] - probe["used_mib"]
    f = {
        "gpu_util_pct": probe["util_pct"],
        "gpu_mem_total_mib": probe["total_mib"],
        "gpu_total_vram_mib": probe["total_mib"],
        "gpu_face": "nvidia-smi %d%% / %d MiB used of %d MiB"
                    % (int(probe["util_pct"]), probe["used_mib"],
                       probe["total_mib"]),
        "gpu_face_ts": stamp,
        "gpu_face_source": "nvidia-smi",
    }
    for k in FREE_KEYS:
        f[k] = round(free / 1024.0, 1) if key_unit(k) == "gb" else free
    for k in USED_KEYS:
        f[k] = probe["used_mib"]
    for k in PAIR_FREE_TOTAL:
        f[k] = "%d, %d" % (free, probe["total_mib"])
    return f


def gpu_mem_key(k):
    """Is this key a GPU-memory spelling, with or without the 'gpu' prefix?

    r1299: the prefix-based rule was the hole -- `free_vram_mb` was neither in the
    table nor reported, so it kept a 14-round-old number on a face that audited
    clean apart from its siblings."""
    k = k.lower()
    if k in ("total_ram_gb", "free_ram_gb", "idle_ram_gb", "ram_free_gb",
             "ram_load_pct", "ram_critical_face"):
        return False
    # r1169: the exclusion above was a frozen list of exact spellings, so the MB
    # spells of SYSTEM RAM (free_ram_mb / ram_free_mb) fell through and were
    # reported as unowned GPU keys. A RAM key is RAM in any unit: 'vram' keeps its
    # own rule, so match 'ram' only when it is not preceded by a letter.
    if re.search(r"(?<![a-z])ram", k):
        return False
    if not re.search(r"(vram|gpu|mib|mb|gb)", k):
        return False
    return bool(re.match(r"^(gpu)?[a-z_]*(free|used|idle)", k)) or \
        bool(re.search(r"(free|used|idle)_(vram|gpu)", k))


def _pair(value):
    """Parse a 'free, total' pair; None if it is anything else."""
    if not isinstance(value, str):
        return None
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2:
        return None
    try:
        return (float(parts[0]), float(parts[1]))
    except ValueError:
        return None


def audit(face):
    """Disagreements on an existing heartbeat face. Pure; returns a list of dicts."""
    out = []

    def spread(keys, unit):
        got = [(k, _mb(k, face[k])) for k in keys
               if isinstance(face.get(k), (int, float))]
        if len(got) < 2:
            return
        hi = max(got, key=lambda kv: kv[1])
        lo = min(got, key=lambda kv: kv[1])
        if hi[1] - lo[1] >= TOL_MIB:
            out.append({"family": unit, "spread_mib": round(hi[1] - lo[1], 1),
                        "high": hi[0], "low": lo[0],
                        "n_keys": len(got)})

    spread(FREE_KEYS, "free")
    spread(USED_KEYS, "used")
    spread(TOTAL_KEYS, "total")
    free = [(_mb(k, face[k]), k) for k in FREE_KEYS
            if isinstance(face.get(k), (int, float))]
    used = [(_mb(k, face[k]), k) for k in USED_KEYS
            if isinstance(face.get(k), (int, float))]
    total = [(_mb(k, face[k]), k) for k in TOTAL_KEYS
             if isinstance(face.get(k), (int, float))]
    if free and used and total:
        f = sorted(free)[len(free) // 2][0]
        u = sorted(used)[len(used) // 2][0]
        t = sorted(total)[len(total) // 2][0]
        if abs((f + u) - t) >= TOL_MIB:
            out.append({"family": "balance", "free_mib": round(f, 1),
                        "used_mib": round(u, 1), "total_mib": round(t, 1),
                        "gap_mib": round((f + u) - t, 1)})
    known = set(FREE_KEYS) | set(USED_KEYS) | set(TOTAL_KEYS) | set(PAIR_FREE_TOTAL) | {
        "gpu_util_pct", "gpu_face", "gpu_face_ts", "gpu_face_source"}
    # r1177: ownership is "apply() will refresh it", not "somebody tabulated it".
    # A numeric spelling with a derivable family is restated by the probe, so it
    # can no longer age; what still ages is a GPU-memory key whose value is a
    # formatted string (numeric pass cannot touch it) and is not the known pair.
    unowned = sorted(k for k in face
                     if k not in known and gpu_mem_key(k)
                     and (not isinstance(face.get(k), (int, float))
                          or isinstance(face.get(k), bool)
                          or gpu_mem_family(k)[0] is None))
    if unowned:
        out.append({"family": "unowned",
                    "keys": unowned,
                    "note": "GPU-memory key the probe cannot restate (formatted value "
                            "or underivable family): normalise it or consumers read a "
                            "random round"})
    # pair keys are invisible to the numeric pass, so they get their own leg
    for k in PAIR_FREE_TOTAL:
        if k not in face:
            continue
        parsed = _pair(face.get(k))
        if parsed is None:
            out.append({"family": "pair", "key": k, "value": face.get(k),
                        "note": "not a '<free>, <total>' pair"})
            continue
        free_med = [(_mb(x, face[x]), x) for x in FREE_KEYS
                    if isinstance(face.get(x), (int, float))]
        tot_med = [(_mb(x, face[x]), x) for x in TOTAL_KEYS
                   if isinstance(face.get(x), (int, float))]
        if free_med and abs(parsed[0] - sorted(free_med)[len(free_med) // 2][0]) >= TOL_MIB:
            out.append({"family": "pair", "key": k, "free_mib": parsed[0],
                        "note": "pair free value disagrees with the free family"})
        if tot_med and abs(parsed[1] - sorted(tot_med)[len(tot_med) // 2][0]) >= TOL_MIB:
            out.append({"family": "pair", "key": k, "total_mib": parsed[1],
                        "note": "pair total value disagrees with the total family"})
    if "gpu_util_pct" in face and face.get("gpu_face_ts") is None:
        out.append({"family": "provenance",
                    "note": "gpu_util_pct present with no gpu_face_ts: "
                            "written before this tool owned the face"})
    return out


def _paths(project):
    with io.open(os.path.join(project, "fleet", "machine.json"),
                 encoding="utf-8-sig") as fh:
        mid = json.load(fh)["machine_id"]
    return mid, os.path.join(project, "fleet", "machines", mid + ".json")


def _load(path):
    with io.open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def probe_live(smi=None):
    return parse_smi(_run_smi(smi))


def cmd_probe():
    p = probe_live()
    print(json.dumps(p, sort_keys=True))
    return 0


def cmd_audit(project=ROOT):
    mid, hb_path = _paths(project)
    if not os.path.exists(hb_path):
        print(json.dumps({"error": "heartbeat missing: %s" % hb_path}))
        return 2
    face = _load(hb_path)
    findings = audit(face)
    print(json.dumps({"machine_id": mid, "findings": findings,
                      "n_gpu_keys": len([k for k in face if k.startswith("gpu")])},
                     sort_keys=True))
    return 0


def cmd_apply(project=ROOT, smi=None):
    try:
        p = probe_live(smi)
    except Exception as ex:  # no write on a failed probe (law 4)
        print(json.dumps({"error": "probe failed: %s" % ex}, sort_keys=True))
        return 2
    stamp = _stamp()
    fields = fields_from(p, stamp)
    mid, hb_path = _paths(project)
    if os.path.exists(hb_path):
        try:
            fields.update(restate(_load(hb_path), fields))
        except Exception as ex:  # an unreadable face must not block the canonical write
            print(json.dumps({"restate_skipped": str(ex)[:120]}, sort_keys=True))
    sys.path.insert(0, ROOT)
    from Tools import heartbeat_write
    v, rc = heartbeat_write.write(project, fields)
    v["probe"] = p
    v["face"] = fields["gpu_face"]
    print(json.dumps(v, ensure_ascii=False, sort_keys=True))
    return rc


def _stamp():
    import datetime
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, want, got, extra=""):
        legs.append((name, want == got))
        print("%-72s %s %s" % (name, "PASS" if want == got else "FAIL", extra))

    # L1 parse: the exact shape nvidia-smi prints
    try:
        p = parse_smi("100 %, 11688 MiB, 16384 MiB\n")
        leg("L1 parse util/used/total", (100.0, 11688, 16384),
            (p["util_pct"], p["used_mib"], p["total_mib"]))
    except Exception as ex:
        leg("L1 parse util/used/total", True, False, str(ex))

    # L2 parse refuses garbage (a silent 0 is the defect this tool exists for)
    bad = 0
    for probe in ("", "garbage\n", "0 %, 900 MiB\n", "0 %, 20000 MiB, 16384 MiB"):
        try:
            parse_smi(probe)
        except ValueError:
            bad += 1
    leg("L2 parse refuses empty/short/incoherent input", 4, bad)

    # L3 one probe -> every alias agrees (activity leg: 21 keys must be present)
    f = fields_from({"util_pct": 100.0, "used_mib": 11688, "total_mib": 16384},
                    "2026-10-26T08:10:00+08:00")
    # MiB keys are exact; the GB mirrors carry a 1-dp convention, so their spread is
    # bounded by half a 0.1 GB step (~51 MiB) rather than zero. Both are pinned.
    mib = [_mb(k, f[k]) for k in FREE_KEYS if key_unit(k) == "mib"]
    gb = [_mb(k, f[k]) for k in FREE_KEYS if key_unit(k) == "gb"]
    leg("L3 exact aliases agree to the byte", 0.0, round(max(mib) - min(mib), 3),
        "n=%d MiB keys" % len(mib))
    leg("L3a 1-dp GB mirrors within half a step", True,
        round(max(gb + mib) - min(gb + mib), 1) <= 52.0,
        "spread=%.1f MiB" % (max(gb + mib) - min(gb + mib)))
    leg("L3b free+used == total", 16384.0,
        round(_mb("gpu_free_mib", f["gpu_free_mib"]) + f["gpu_used_mib"], 3))
    # L3c r1311: a key whose NAME promises GB must never be written with a MiB number.
    #     gpu_vram_free_gb sat on FREE_KEYS but not on GB_KEYS and carried 15099, so the
    #     face said "15099 GB free" to any reader that trusted the name.
    gb_named = [k for k in FREE_KEYS if key_unit(k) == "gb"]
    leg("L3c every GB-named key carries GB", [], [k for k in gb_named if f[k] >= 100],
        "%d GB keys" % len(gb_named))
    leg("L3d a MiB number under a GB name is caught, not agreed with", True,
        round(_mb("gpu_vram_free_gb", 15099) - _mb("gpu_free_mib", 15099), 1) > 64000,
        "reads %.0f MiB" % _mb("gpu_vram_free_gb", 15099))
    leg("L3c audit is silent on a self-consistent face", [], audit(f))

    # L4 audit catches the live defect: a literal 0 next to a 13.7 GB free claim
    stale = dict(f, gpu_free_vram_gb=1.31, gpu_vram_free_mb=781,
                 gpu_used_vram_mib=1717, gpu_idle_mib=14461)
    fams = {x["family"] for x in audit(stale)}
    leg("L4 audit flags free/used disagreement", True,
        "free" in fams and "used" in fams, sorted(fams))

    # L5 provenance leg: a util number with no face stamp is flagged, so a value
    # that predates this tool cannot pass as current
    prov = {"gpu_util_pct": 0, "gpu_free_mib": 14251, "gpu_used_mib": 2133,
            "gpu_mem_total_mib": 16384}
    leg("L5 audit flags unstamped gpu_util_pct", True,
        any(x["family"] == "provenance" for x in audit(prov)))

    # L5a the spelling table must cover every word order the live face actually uses:
    # a key that apply() writes but audit() ignores is a half-owned face
    for k, val in (("gpu_vram_free_mb", 781), ("gpu_vram_used_mb", 2008)):
        half = dict(f)
        half[k] = val
        leg("L5a %s is owned, not a stray round" % k, False,
            any(x["family"] == "unowned" for x in audit(half)))
    leg("L5a gpu_vram_used_mb is rewritten by the same probe", 11688,
        f["gpu_vram_used_mb"])

    # L5b r1177: an invented numeric spelling is RESTATED by the pattern rule, so
    # it cannot age just by being new (this replaces the "report it as unowned"
    # leg, which only held while ownership was an enumeration).
    stray = dict(f, gpu_memory_free_gb=1.0)
    filled = dict(stray, **restate(stray, f))
    leg("L5b an invented numeric spelling is restated", 4.6,
        filled["gpu_memory_free_gb"])
    leg("L5b an invented numeric spelling audits clean once restated", [], audit(filled))
    # L5c what still ages is a formatted value the numeric pass cannot touch
    leg("L5c a formatted GPU value outside the pair table is reported", True,
        any(x["family"] == "unowned"
            for x in audit(dict(f, gpu_memory_free="4.6 GB"))))
    # L5d the live defect of r1177: vram_used_gb (used family, GB unit) sat outside
    # every table while all of its MiB siblings were rewritten
    live = dict(f, vram_used_gb=2.0)
    fixed = dict(live, **restate(live, f))
    leg("L5d vram_used_gb is restated from the same probe", 11.4, fixed["vram_used_gb"])
    leg("L5d a heartbeat carrying vram_used_gb audits clean once restated", [],
        audit(fixed))

    # L7 r1299: an un-prefixed spelling is a GPU key too. `free_vram_mb` sat beside
    # 13 gpu_* keys with a 14-round-old value and nothing reported it.
    leg("L7 free_vram_mb is written by the probe", 4696, f["free_vram_mb"])
    leg("L7a an un-prefixed stray is restated, not left stale", 4696,
        dict(dict(f, vram_free_mb=1), **restate(dict(f, vram_free_mb=1), f))[
            "vram_free_mb"])
    leg("L7b RAM keys are not claimed as GPU keys", False, gpu_mem_key("free_ram_gb"))

    # L8 the pair key: written from one probe, parsed by the audit, and a stale pair
    # is caught (it is a string, so the numeric pass can never see it)
    leg("L8 pair key written as free, total", "4696, 16384", f["gpu_free"])
    leg("L8a pair parses", (4696.0, 16384.0), _pair(f["gpu_free"]))
    leg("L8b a stale pair is reported", True,
        any(x["family"] == "pair" for x in audit(dict(f, gpu_free="10111, 16384"))))
    leg("L8c an unparsable pair is reported, not ignored", True,
        any(x["family"] == "pair" for x in audit(dict(f, gpu_free="lots"))))

    # L6 failed probe writes nothing (rc 2, heartbeat bytes untouched)
    import tempfile
    tmp = tempfile.mkdtemp(prefix="gpuface_st_")
    os.makedirs(os.path.join(tmp, "fleet", "machines"))
    with io.open(os.path.join(tmp, "fleet", "machine.json"), "w",
                 encoding="utf-8") as fh:
        json.dump({"machine_id": "bm-z"}, fh)
    hp = os.path.join(tmp, "fleet", "machines", "bm-z.json")
    with io.open(hp, "w", encoding="utf-8") as fh:
        json.dump({"machine_id": "bm-z", "gpu_util_pct": 0,
                   "heartbeat_epoch_utc": 1792000000,
                   "clock_read": "2026-10-26T08:00:00+08:00",
                   "ts": "2026-10-26T08:00:00+08:00"}, fh)
    before = io.open(hp, "rb").read()
    shim = os.path.join(tmp, "smi_fail.cmd")
    with io.open(shim, "w", encoding="ascii", newline="\r\n") as fh:
        fh.write("@echo off\r\nexit /b 9\r\n")
    rc = cmd_apply(tmp, shim)
    after = io.open(hp, "rb").read()
    leg("L6 failed probe -> rc2 and heartbeat untouched", (2, True), (rc, before == after))

    # L9 r1169: a RAM spelling is never a GPU key (the frozen list let MB through)
    leg("L9a system RAM keys are not GPU-memory keys", (False, False, False),
        (gpu_mem_key("free_ram_mb"), gpu_mem_key("ram_free_mb"),
         gpu_mem_key("total_ram_gb")))
    leg("L9b vram keys still are GPU-memory keys", (True, True, True),
        (gpu_mem_key("vram_free_gb"), gpu_mem_key("free_vram_gb"),
         gpu_mem_key("gpu_free_vram_gb")))
    # L9c the GB spellings must be OWNED and unit-scaled, else they silently age
    _f9 = fields_from({"util_pct": 50.0, "used_mib": 4096, "total_mib": 16384},
                      "2026-10-27T07:00:00+08:00")
    leg("L9c free_vram_gb / vram_free_gb are written and scaled",
        (True, 12.0, 12.0),
        ("free_vram_gb" in FREE_KEYS and "vram_free_gb" in FREE_KEYS,
         _f9.get("free_vram_gb"), _f9.get("vram_free_gb")))
    leg("L9d a heartbeat carrying the GB spells audits clean",
        [], [x["family"] for x in audit(dict(_f9, free_ram_mb=8000,
                                             ram_free_mb=8000))])

    ok = sum(1 for _, p in legs if p)
    print("\nselftest %d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd in ("selftest", "--selftest"):
        return selftest()
    if cmd == "probe":
        try:
            return cmd_probe()
        except Exception as ex:
            print(json.dumps({"error": str(ex)}))
            return 2
    if cmd == "audit":
        return cmd_audit()
    if cmd == "apply":
        return cmd_apply()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))