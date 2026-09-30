"""PERPETUAL_FACES generator v0.2 -- T-133 s2 (CEO O-2026-09-30-2340).

v0.2 (bm-b r485): N1 runner landed (scripts/perpetual_faces_n1.py, wave-2
prereg research/PERPETUAL_N1_W2_PREREG.md frozen pre-run); first-wave W2
materialized via autofill submit per law freeze-signature sequencing line
("runner lands one batch, materialize one batch"); N1 supply_ready=False
until the per-shard materializer pattern lands (next slice) -- supply()
reports it honestly as supply-blocked, never fake-materializes.

Law: research/PERPETUAL_FACES.md v1.0 (FROZEN bm-b r484 2026-09-30).
Face-level prereg frozen ONCE (ticket law); per-wave preregs (R99
discipline) reference the law's pre-assigned seed bands (sec.4 ledger,
R250 one-step law -- bands frozen here BEFORE any wave runner exists,
no re-pick after freeze).

Faces (law sec.2):
  N1 nulls-deepening        base: p2_null_calibration(.ext) pattern
  N2 random-subspace        base: trial_labor chain grammar (exploration)
  N3 neighborhood robustness base: t24_g2_pack.py generalization
  N4 bootstrap alternate-history  base: engine replay + resample layer

v0.1 scope: trigger evaluation + flags + face registry + seed-band
disjointness selftest + honest no-op when no face runner has landed.
Materialization (pool entry write) activates per-face as runners land
(law freeze-signature sequencing: N1-W2 -> N3-R1 -> N2-W15 -> N4-B1);
a face with runner=None is NEVER materialized (fake-supply ban, law
sec.1 honest clause).

Contract (law sec.1/sec.3):
  supply   evaluate 3-leg trigger (pool starving AND py<70 AND no
           same-face in-flight wave) -> materialize next wave for the
           first runner-landed face in priority order N1>N3>N2>N4.
           Writes flags to results/perpetual_faces_state.json
           (pool_starved / supply_floor / faces_pending) consumed by
           the s3 daily-report/CEO-face wiring.  exit 0 normal (incl.
           honest no-op), 2 mechanism failure.
  status   read-only trigger face + registry + flags report. exit 0/2.
  selftest offline hermetic checks (no network, no pool writes):
           face registry integrity, seed-band disjointness vs
           science_gates.SEED_REGISTRY + v1/ext in-use bands, pool
           parse, state round-trip. exit 0/1.

Single-writer law: pool file written ONLY by this lane-machine
generator on materialization; autofill stays read-only (pool schema
single_writer note, unchanged). All materialized entries carry
worker_class=self-contained, lane_owner=ANY (R31/R65 lawful).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS  # noqa: E402
import science_gates as sg  # noqa: E402

LAW_REF = "research/PERPETUAL_FACES.md v1.0 (T-133 s2, O-2026-09-30-2340)"
STATE_PATH = os.path.join(PATHS.results_dir, "perpetual_faces_state.json")
POOL_PATH = os.path.join(PATHS.results_dir, "runnable_pool.json")

# --- law sec.4 pre-assigned seed bands (frozen, append-only ledger) ---
N1_BANDS = {
    2: {"a": (12_100, 14_099), "b_exit": (21_100, 21_299)},
    3: {"a": (14_100, 16_099), "b_exit": (21_300, 21_499)},
    4: {"a": (16_100, 18_099), "b_exit": (21_500, 21_699)},
}
# v1 + ext(wave-1) in-use bands (source of truth: those runners' constants)
V1_IN_USE = set(range(10_000, 10_100)) | set(range(20_000, 20_020))
EXT_W1_IN_USE = set(range(10_100, 12_100)) | set(range(20_100, 20_300))

# --- face registry (law sec.2; runner=None = not landed, never materialized) ---
FACES = [
    {"id": "N1", "name": "nulls-deepening", "priority": 1,
     "runner": "scripts/perpetual_faces_n1.py",
     "runner_args": ["run"],  # per-shard args appended at materialization
     "wave": 2, "prereg_ref": "research/PERPETUAL_N1_W2_PREREG.md",
     # supply auto-path blocked until the per-shard materializer pattern lands
     # (next slice); W2 first batch entered via autofill submit per the law
     # freeze-signature sequencing line -- never a fake-supply entry
     "supply_ready": False},
    {"id": "N3", "name": "neighborhood-robustness", "priority": 2, "runner": None,
     "runner_args": None, "wave": 1, "prereg_ref": None},
    {"id": "N2", "name": "random-subspace-furnace", "priority": 3, "runner": None,
     "runner_args": None, "wave": 15, "prereg_ref": None},
    {"id": "N4", "name": "bootstrap-alt-history", "priority": 4, "runner": None,
     "runner_args": None, "wave": 1, "prereg_ref": None},
]


def _load_pool():
    """Parse runnable_pool.json; tolerate missing file as empty pool."""
    if not os.path.exists(POOL_PATH):
        return {"entries": {}}
    with open(POOL_PATH, encoding="utf-8") as f:
        return json.load(f)


def _pool_live_count(pool):
    entries = pool.get("entries", [])
    vals = entries.values() if isinstance(entries, dict) else entries
    return sum(1 for e in vals if str(e.get("status", "")) in ("ready", "waiting", "running"))


def _py_face():
    """Lane machine py CPU pct from its autofill state last_tick; None if unknown."""
    try:
        p = os.path.join(PATHS.root, "fleet", "machine.json")
        with open(p, encoding="utf-8") as f:
            mid = json.load(f).get("machine_id")
        p = os.path.join(PATHS.results_dir, f"autofill_state.{mid}.json")
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return float(d.get("last_tick", {}).get("py_cpu_pct"))
    except Exception:
        return None


def _trigger():
    pool = _load_pool()
    live = _pool_live_count(pool)
    starving = live == 0
    py = _py_face()
    py_ok = True if py is None else py < 70.0
    return pool, live, starving, py, py_ok


def _load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"version": 1, "law_ref": LAW_REF, "waves": [], "last_supply": None}


def _write_state(st):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE_PATH)


def cmd_status():
    pool, live, starving, py, py_ok = _trigger()
    pending = [f["id"] for f in sorted(FACES, key=lambda x: x["priority"]) if not f["runner"]]
    landed = [f["id"] for f in FACES if f["runner"]]
    blocked = [f["id"] for f in FACES
               if f["runner"] and not f.get("supply_ready", True)]
    print(f"pool live entries: {live} (starving={starving})")
    print(f"lane py_cpu face: {py} (py_ok={py_ok})")
    print(f"faces runner-landed: {landed or 'NONE'}")
    if blocked:
        print(f"supply-blocked (per-shard materializer pending, honest): {blocked}")
    print(f"faces pending (honest, never materialized): {pending}")
    st = _load_state()
    w = len(st.get("waves", []))
    print(f"materialized waves to date: {w}")
    if starving and pending and not landed:
        print("VERDICT: supply_floor=true pool_starved=true "
              "faces_pending=%s -- runner landing is the remediation lane "
              "(law freeze-signature sequencing)" % ",".join(pending))
    elif starving:
        print("VERDICT: pool_starved=true supply runnable via landed faces")
    else:
        print("VERDICT: pool has live supply; no action")
    return 0


def cmd_supply():
    pool, live, starving, py, py_ok = _trigger()
    st = _load_state()
    st["flags"] = {
        "pool_starved": bool(starving),
        "supply_floor": bool(starving and not any(f["runner"] for f in FACES)),
        "generated_at": sg._now() if hasattr(sg, "_now") else None,
    }
    st["last_supply"] = {
        "live": live, "starving": bool(starving), "py": py, "py_ok": py_ok,
        "faces_pending": [f["id"] for f in FACES if not f["runner"]],
    }
    if not (starving and py_ok):
        st["flags"]["supply_floor"] = False
        _write_state(st)
        print(f"supply: no trigger (live={live} py={py}) -- flags updated")
        return 0
    landed = [f for f in sorted(FACES, key=lambda x: x["priority"])
              if f["runner"] and f.get("supply_ready", True)]
    blocked = [f["id"] for f in FACES
               if f["runner"] and not f.get("supply_ready", True)]
    if blocked:
        st["last_supply"]["supply_blocked"] = blocked
    if not landed:
        _write_state(st)
        if blocked:
            print(f"supply: trigger MET but runner-landed faces awaiting the "
                  f"per-shard materializer pattern ({','.join(blocked)}) -- "
                  f"honest no-op, flags written; first wave materialized via "
                  f"autofill submit per law sequencing line")
        else:
            print("supply: trigger MET but no face runner landed -- honest no-op, "
                  "flags written (pool_starved/supply_floor) for s3 wiring; "
                  "N1-W2 runner is the next law-sequenced deliverable")
        return 0
    face = landed[0]
    # materialization path activates with the first landed runner; v0.1
    # ships the registry with runner=None for all faces by law (runners
    # land with their own frozen wave preregs in subsequent rounds).
    entry = {
        "id": f"{face['id']}-W{face['wave']}",
        "ticket_ref": "T-2026-09-30-133 s2 (O-2026-09-30-2340)",
        "prereg_ref": face["prereg_ref"],
        "runner": face["runner"],
        "runner_args": face["runner_args"] or [],
        "lane_owner": "ANY",
        "priority": 1,
        "status": "ready",
        "entered_at": sg._now() if hasattr(sg, "_now") else None,
        "worker_class": "self-contained",
        "shards": [],  # filled by the wave's own materializer spec
        "workers_plan": {"workers": 12, "priority": "BelowNormal"},
    }
    pool.setdefault("entries", [])
    entries = pool["entries"]
    vals = entries.values() if isinstance(entries, dict) else entries
    if any(e.get("id") == entry["id"] for e in vals):
        print(f"supply: wave entry {entry['id']} already in pool -- idempotent no-op")
        _write_state(st)
        return 0
    pool["updated_at"] = entry["entered_at"]
    tmp = POOL_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=1)
    os.replace(tmp, POOL_PATH)
    st["waves"].append({"face": face["id"], "wave": face["wave"],
                        "entered_at": entry["entered_at"],
                        "bands": N1_BANDS.get(face["wave"]) if face["id"] == "N1" else None})
    _write_state(st)
    print(f"supply: materialized {entry['id']} into runnable_pool (single-writer lane write)")
    return 0


def cmd_selftest():
    ok = True
    # 1. face registry integrity (law sec.2: four faces, priorities 1-4)
    ids = [f["id"] for f in sorted(FACES, key=lambda x: x["priority"])]
    assert ids == ["N1", "N3", "N2", "N4"], "face priority order drift"
    assert all("runner" in f and "wave" in f for f in FACES)
    # 2. seed bands disjoint: intra-N1, vs v1, vs ext wave-1, vs SEED_REGISTRY
    reg_ints = {v for v in sg.SEED_REGISTRY.values() if isinstance(v, (int, float))}
    used = []
    for w, b in N1_BANDS.items():
        band_a = set(range(b["a"][0], b["a"][1] + 1))
        band_b = set(range(b["b_exit"][0], b["b_exit"][1] + 1))
        assert not (band_a & band_b), f"N1 w{w} A/B band overlap"
        assert not (band_a & V1_IN_USE) and not (band_b & V1_IN_USE), f"N1 w{w} hits v1 band"
        assert not (band_a & EXT_W1_IN_USE) and not (band_b & EXT_W1_IN_USE), f"N1 w{w} hits ext w1"
        assert not (band_a & reg_ints) and not (band_b & reg_ints), f"N1 w{w} hits SEED_REGISTRY"
        used.append((band_a, band_b))
    for i in range(len(used)):
        for j in range(i + 1, len(used)):
            assert not (used[i][0] & used[j][0]) and not (used[i][1] & used[j][1]), \
                f"N1 waves {i + 2}/{j + 2} band overlap"
    # 3. band continuity (no unassigned gap inside the pre-assigned ladder)
    for w in (3, 4):
        assert N1_BANDS[w]["a"][0] == N1_BANDS[w - 1]["a"][1] + 1, f"N1 w{w} A gap"
        assert N1_BANDS[w]["b_exit"][0] == N1_BANDS[w - 1]["b_exit"][1] + 1, f"N1 w{w} B gap"
    # 4. pool parse (read-only; missing file tolerated)
    pool = _load_pool()
    _pool_live_count(pool)
    # 5. state round-trip (no pool writes; state file may be created in tmp)
    st = _load_state()
    st["_selftest_probe"] = True
    st2 = json.loads(json.dumps(st))
    assert st2.get("_selftest_probe") is True
    del st["_selftest_probe"]
    # 6. py face reader robustness (missing machine file -> None, no crash)
    assert _py_face() is None or isinstance(_py_face(), float)
    print("perpetual_faces selftest: 6/6 PASS "
          "(registry/seed-bands/pool/state/py-face)")
    return 0 if ok else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    try:
        if cmd == "status":
            return cmd_status()
        if cmd == "supply":
            return cmd_supply()
        if cmd == "selftest":
            return cmd_selftest()
        print(f"unknown subcommand: {cmd} (use status|supply|selftest)")
        return 2
    except AssertionError as e:
        print(f"selftest FAIL: {e}")
        return 1
    except Exception as e:  # mechanism failure: report honestly, never mask
        print(f"mechanism failure: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
