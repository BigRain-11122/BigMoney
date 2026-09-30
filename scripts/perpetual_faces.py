"""PERPETUAL_FACES generator v0.3 -- T-133 s2 (CEO O-2026-09-30-2340).

v0.2 (bm-b r485): N1 runner landed (scripts/perpetual_faces_n1.py, wave-2
prereg research/PERPETUAL_N1_W2_PREREG.md frozen pre-run); first-wave W2
materialized via autofill submit per law freeze-signature sequencing line
("runner lands one batch, materialize one batch").

v0.3 (bm-b r490): per-shard materializer pattern landed (the "next slice"
the v0.2 registry promised). Runner is wave-parameterized (v0.3 --wave,
law sec.4 pre-assigned rows W2/W3; spawn-side wave carrier via executor
initargs). supply() now expands the next law wave into 12 per-shard pool
entries (W2 registration face verbatim) when the 3-leg trigger fires;
per-wave prereg presence is the materialization gate (never fake-supply);
pool rewrites mirror the file's probed indent/EOL (r289 format law).

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
           first runner-landed face in priority order N1>N3>N2>N4 as
           12 per-shard entries (per-wave prereg required, never
           fake-supply; next wave derived from pool entry truth).
           Writes flags to results/perpetual_faces_state.json
           (pool_starved / supply_floor / faces_pending) consumed by
           the s3 daily-report/CEO-face wiring.  exit 0 normal (incl.
           honest no-op), 2 mechanism failure.
  status   read-only trigger face + registry + flags report. exit 0/2.
  selftest offline hermetic checks (no network, no pool writes):
           face registry integrity, seed-band disjointness vs
           science_gates.SEED_REGISTRY + v1/ext in-use bands, pool
           parse, state round-trip, materializer expansion face,
           pool format-mirror probe. exit 0/1.

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
     # per-shard materializer pattern landed r490 (runner v0.3 --wave):
     # supply() expands the next law sec.4 wave into 12 per-shard entries
     # when the 3-leg trigger fires; per-wave prereg presence is the gate
     "supply_ready": True},
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
    """Live = claimable/pending supply. park_note'd entries are deliberate
    governance holds (r304 park_note marker law / r504 authority law),
    not supply: their unfreeze is gated on canon self-proof or a GM
    ruling and the picker never claims a 'waiting' entry -- counting
    them as live deadlocks the never-dry law behind a parked entry
    forever (live case r497: W14 re-park N=0 held live=1 while every
    burnable face was done and the pool was truly starved)."""
    entries = pool.get("entries", [])
    vals = entries.values() if isinstance(entries, dict) else entries
    n = 0
    for e in vals:
        if str(e.get("status", "")) not in ("ready", "waiting", "running"):
            continue
        if e.get("park_note"):
            continue
        n += 1
    return n


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


def _expand_wave_entries(face, wave, ts):
    """Per-shard materializer (law sec.1): expand one wave into 12 pool
    entries -- the W2 registration face verbatim (one entry per shard,
    runner carries the wave, checkpoint=presence=done contract, unclaimed
    shard faces). Pure function: no pool/state writes (selftest exercises
    it hermetically)."""
    bands = N1_BANDS[wave]
    entries = []
    for i in range(12):
        entries.append({
            "id": f"PERPETUAL-N1-W{wave}-SHARD-{i}",
            "ticket_ref": "T-2026-09-30-133 s2 (O-2026-09-30-2340)",
            "prereg_ref": (f"research/PERPETUAL_N1_W{wave}_PREREG.md "
                           f"(frozen pre-run; law sec.4 W{wave} bands "
                           f"A {bands['a'][0]}+ / B-exit {bands['b_exit'][0]}+)"),
            "consumer_plan": ("science_gates null-pool deepening: merged "
                              "pool (law sec.5 cumulative) -> skill_line_v2 "
                              "K-lift + p95/p99 face (G1 prime skill line "
                              "consumer)"),
            "runner": "scripts/perpetual_faces_n1.py",
            "runner_args": ["run", "--shard", str(i), "--of", "12",
                            "--wave", str(wave)],
            "lane_owner": "ANY",
            "priority": 1,
            "status": "ready",
            "entered_at": ts,
            "worker_class": "self-contained",
            "data_gates": ("in-runner FAIL-CLOSED: universe==48 bare codes "
                           "+ panel end==2026-09-22 same-window + law sec.4 "
                           "seed bands (selftest-enforced) + determinism "
                           "byte-equal rerun"),
            "shards": [{
                "key": f"n1w{wave}-{i}of12",
                "status": "ready",
                "checkpoint": (f"results/p2cal_ext/n1_w{wave}/"
                              f"shard-{i}-of-12.json (presence=done; "
                              f"deterministic rerun byte-equal)"),
                "note": (f"N1-W{wave} wave shard {i} of 12 "
                         f"(A2000+B200 contiguous slice); ~2min serial burn"),
            }],
            "workers_plan": {
                "workers": 8, "priority": "BelowNormal",
                "workers_law": ("ProcessPoolExecutor code-backed, "
                                "O-20260930-2355 multicore law (serial-vs-"
                                "pool byte-equal parity proven on W2); "
                                "BLAS 1/worker cap; --workers override"),
            },
        })
    return entries


def _pool_format_probe():
    """r289 format law: probe the pool file's indent + EOL + trailing-NL
    face before any rewrite (bare json.dump defaults = whole-file diff).
    Missing file -> the canonical producer face (indent 2, CRLF)."""
    indent, crlf, trailing_nl = 2, True, False
    if os.path.exists(POOL_PATH):
        b = open(POOL_PATH, "rb").read()
        nl = b.count(b"\n")
        crlf = b.count(b"\r\n") >= max(1, nl) // 2
        trailing_nl = b.endswith(b"\n")
        for line in b.decode("utf-8", errors="replace").split("\n"):
            s = line.strip()
            if s.startswith('"'):
                indent = len(line) - len(line.lstrip(" "))
                break
    return indent, crlf, trailing_nl


def _pool_write_mirror(pool):
    """Atomic pool write mirroring the probed producer format (single-writer
    lane law; the tmp+replace face is the established producer pattern)."""
    indent, crlf, trailing_nl = _pool_format_probe()
    s = json.dumps(pool, ensure_ascii=False, indent=indent)
    if crlf:
        s = s.replace("\n", "\r\n")
    if trailing_nl and not s.endswith("\n"):
        s += "\r\n" if crlf else "\n"
    tmp = POOL_PATH + ".tmp"
    with open(tmp, "wb") as f:
        f.write(s.encode("utf-8"))
    os.replace(tmp, POOL_PATH)


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
    ts = sg._now() if hasattr(sg, "_now") else None
    if face["id"] != "N1":
        # future faces (N3/N2/N4): their per-shard materializer patterns
        # land together with their runners (law freeze-signature sequencing)
        _write_state(st)
        print(f"supply: face {face['id']} runner landed but its per-shard "
              f"materializer pattern has not landed -- honest no-op")
        return 0
    vals = list(pool.get("entries", []))
    if isinstance(pool.get("entries"), dict):
        vals = list(pool["entries"].values())
    # law sec.1 leg-3: no same-face in-flight wave (live = ready/waiting/running;
    # park_note'd entries are deliberate holds, not in-flight supply -- same
    # r304/r504 marker law as _pool_live_count)
    n1_live = [e for e in vals
               if str(e.get("id", "")).startswith("PERPETUAL-N1-")
               and str(e.get("status", "")) in ("ready", "waiting", "running")
               and not e.get("park_note")]
    if n1_live:
        _write_state(st)
        print(f"supply: same-face wave in flight ({len(n1_live)} live "
              f"PERPETUAL-N1-* entries) -- honest no-op (law sec.1 leg-3)")
        return 0
    # next wave from pool entry truth (materialization ledger of record;
    # generator-local state waves[] is not the cross-machine truth face)
    waves_seen = []
    for e in vals:
        eid = str(e.get("id", ""))
        if eid.startswith("PERPETUAL-N1-W") and "-SHARD-" in eid:
            try:
                waves_seen.append(
                    int(eid.split("PERPETUAL-N1-W")[1].split("-SHARD-")[0]))
            except (IndexError, ValueError):
                pass
    wave = (max(waves_seen) + 1) if waves_seen else face["wave"]
    if wave not in N1_BANDS:
        st["last_supply"]["awaiting"] = f"law sec.4 bands for W{wave}"
        _write_state(st)
        print(f"supply: next wave W{wave} has no law sec.4 pre-assigned "
              f"bands yet (tail rows extend per-wave at prereg time) -- "
              f"honest no-op")
        return 0
    prereg_rel = f"research/PERPETUAL_N1_W{wave}_PREREG.md"
    if not os.path.exists(os.path.join(PATHS.root, prereg_rel)):
        st["last_supply"]["awaiting"] = f"frozen prereg for W{wave}"
        _write_state(st)
        print(f"supply: per-wave prereg {prereg_rel} not frozen -- never "
              f"fake-supply (honest no-op; prereg is the wave gate)")
        return 0
    new_entries = _expand_wave_entries(face, wave, ts)
    existing_ids = {str(e.get("id", "")) for e in vals}
    new_entries = [e for e in new_entries if e["id"] not in existing_ids]
    if not new_entries:
        _write_state(st)
        print(f"supply: W{wave} per-shard entries already in pool -- "
              f"idempotent no-op")
        return 0
    pool.setdefault("entries", [])
    if isinstance(pool["entries"], dict):
        for e in new_entries:
            pool["entries"][e["id"]] = e
    else:
        pool["entries"].extend(new_entries)
    pool["updated_at"] = ts
    _pool_write_mirror(pool)
    st["waves"].append({"face": face["id"], "wave": wave, "entered_at": ts,
                        "n_entries": len(new_entries),
                        "bands": N1_BANDS.get(wave)})
    _write_state(st)
    print(f"supply: materialized {len(new_entries)} per-shard entries "
          f"PERPETUAL-N1-W{wave}-SHARD-0..11 into runnable_pool "
          f"(single-writer lane write, format-mirrored)")
    return 0


def cmd_selftest():
    global POOL_PATH               # 8b swaps it to a temp file (restored)
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
    # 4b. park_note'd entries are deliberate holds, never live supply
    # (r304/r504 marker law; live case r497 W14 re-park deadlocked the
    # starvation leg -- the face this generator exists to feed)
    probe_pool = {"entries": [
        {"id": "A", "status": "done"},
        {"id": "B", "status": "waiting"},
        {"id": "C", "status": "waiting", "park_note": "governance hold"},
        {"id": "D", "status": "ready", "park_note": "governance hold"},
        {"id": "E", "status": "ready"},
    ]}
    assert _pool_live_count(probe_pool) == 2, \
        "park_note'd entries must not count as live supply"
    # 5. state round-trip (no pool writes; state file may be created in tmp)
    st = _load_state()
    st["_selftest_probe"] = True
    st2 = json.loads(json.dumps(st))
    assert st2.get("_selftest_probe") is True
    del st["_selftest_probe"]
    # 6. py face reader robustness (missing machine file -> None, no crash)
    assert _py_face() is None or isinstance(_py_face(), float)
    # 7. per-shard materializer expansion face (pure function; no writes)
    ts = "2026-10-01T00:00:00"
    exp = _expand_wave_entries(FACES[0], 3, ts)
    assert len(exp) == 12, "expansion must be 12 per-shard entries"
    assert [e["id"] for e in exp] == \
        [f"PERPETUAL-N1-W3-SHARD-{i}" for i in range(12)]
    for i, e in enumerate(exp):
        assert e["runner_args"] == ["run", "--shard", str(i), "--of", "12",
                                    "--wave", "3"], f"shard {i} args drift"
        assert e["status"] == "ready" and e["lane_owner"] == "ANY"
        assert e["worker_class"] == "self-contained"
        assert e["entered_at"] == ts and e["priority"] == 1
        assert "PERPETUAL_N1_W3_PREREG" in e["prereg_ref"]
        assert str(N1_BANDS[3]["a"][0]) in e["prereg_ref"], "law A band uncited"
        assert str(N1_BANDS[3]["b_exit"][0]) in e["prereg_ref"], "law B band uncited"
        assert len(e["shards"]) == 1 and e["shards"][0]["key"] == f"n1w3-{i}of12"
        assert e["shards"][0]["status"] == "ready"
        assert e["shards"][0]["checkpoint"].startswith(
            f"results/p2cal_ext/n1_w3/shard-{i}-of-12.json")
        assert "owner" not in e["shards"][0], "unclaimed at materialization"
        assert e["workers_plan"]["workers"] >= 1, "O-2355 workers face"
        for forbidden_owner in ("owner", "owner_since", "done_at", "done_by"):
            assert forbidden_owner not in e["shards"][0]
    # expansion band cites stay law-frozen (R250): tamper probe refuses
    bands_copy = dict(N1_BANDS[3])
    try:
        N1_BANDS[3] = {"a": (99_999, 99_999), "b_exit": (99_998, 99_998)}
        bad = _expand_wave_entries(FACES[0], 3, ts)
        assert "99999" in bad[0]["prereg_ref"], "expansion ignores band table"
    finally:
        N1_BANDS[3] = bands_copy
    # 8. pool format-mirror probe (read-only; r289 law: indent2+CRLF probed)
    if os.path.exists(POOL_PATH):
        indent, crlf, trailing_nl = _pool_format_probe()
        assert indent == 2 and crlf, f"pool format face drifted: {indent}/{crlf}"
        assert trailing_nl is False, "pool trailing face drifted"
    # 8b. writer round-trip on a temp file (hermetic; real pool untouched):
    # probe defaults + CRLF mirror + no trailing NL + byte-identical face
    real_pool = POOL_PATH
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        try:
            POOL_PATH = os.path.join(td, "pool_probe.json")
            sample = {"version": 1, "entries": [{"id": "X-1", "n": [1, 2]}]}
            _pool_write_mirror(sample)
            b = open(POOL_PATH, "rb").read()
            assert b.count(b"\r\n") == b.count(b"\n") and b.count(b"\n") > 0, \
                "CRLF mirror broken"
            assert not b.endswith(b"\n"), "trailing NL leaked"
            assert b'{\r\n  "version": 1' in b, "indent2 mirror broken"
            rt = json.loads(b.decode("utf-8"))
            assert rt == sample, "round-trip content drift"
            # probe on the temp face agrees (indent2/CRLF/no-trailing)
            assert _pool_format_probe() == (2, True, False)
        finally:
            POOL_PATH = real_pool
    print("perpetual_faces selftest: 8/8 PASS "
          "(registry/seed-bands/pool/state/py-face/"
          "materializer-expansion/pool-format-probe+writer-roundtrip)")
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
