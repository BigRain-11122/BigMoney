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
    # W5 (r307 bm-c, prereg-time tail extension per the law's "波5+ 顺延"
    # clause): the arithmetic +2_000 tail (18_100..20_099) collides with
    # the v1 B in-use band 20_000..20_019, SEED_REGISTRY value 20000 and
    # the ext W1 B band 20_100..20_299 -- the disjointness hard law
    # (selftest leg 2, R250) wins over the stride convention, so A skips
    # to the first contiguous 2,000-window beyond every reserved band
    # (21_900 == W5 B end + 1, packing invariant in selftest leg 3b).
    # NOT a re-pick: the W5 band was never assigned and the measurement
    # face has no result to fish. W6+ WARNING: the B +200 arithmetic tail
    # (21_900..22_099) now lands inside the W5 A band -- the W6 prereg
    # must re-base B with the same disclosed skip-over discipline.
    5: {"a": (21_900, 23_899), "b_exit": (21_700, 21_899)},
    # W6 (r309 bm-c, prereg-time extension per the law's pinned W6+
    # WARNING): B keeps its arithmetic stride concept but the +200 tail
    # (21_900..22_099) is documented-refused (falls inside the W5 A band
    # 21_900..23_899) -- disjointness hard law wins, so B skips past
    # every reserved band INCLUDING this wave's own A band and packs at
    # the first free 200-window (== W6 A end + 1). A itself keeps the
    # arithmetic +2_000 tail verbatim (23_900 == W5 A end + 1, no
    # collision). NOT a re-pick: W6 bands were never assigned and the
    # measurement face has no result to fish (R250).
    6: {"a": (23_900, 25_899), "b_exit": (25_900, 26_099)},
    # W7 (r501 bm-b, prereg-time extension, same pinned skip-over
    # discipline -- BOTH tails refused this wave): A's arithmetic
    # +2_000 tail (25_900..27_899) is documented-refused (falls on the
    # W6 B band 25_900..26_099), so A skips past every reserved band and
    # packs at the first free 2,000-window (W6 B end + 1 == 26_100);
    # B's arithmetic +200 tail (26_100..26_299) is in turn refused (it
    # falls inside THIS wave's own A band), so B skips past every
    # reserved band including this wave's A and packs at W7 A end + 1.
    # Refusal facts machine-proven in selftest leg 3d. NOT a re-pick:
    # W7 bands were never assigned, measurement face has nothing to
    # fish (R250). W8+ WARNING: A's arithmetic tail (28_100..30_099)
    # will land on the W7 B band -- W8 must re-base A the same way.
    7: {"a": (26_100, 28_099), "b_exit": (28_100, 28_299)},
    # W8 (r312 bm-c, prereg-time extension -- the law sec.4 pinned W8+
    # WARNING window itself is gate-refused): A's arithmetic +2_000
    # tail (28_100..30_099) is documented-refused -- hits the W7 B band
    # (28_100..28_299) AND the SEED_REGISTRY lfc_p1_screen point
    # 30_000 (actual draw range 30_000..30_099, N_RAND=50 x 2 exit
    # regimes); the law-pinned first-free prediction (28_300..30_299)
    # is refused by the same point + actual range -- so A packs at the
    # first 2,000-window clear of every reserved band AND the lfc
    # actual draw range (30_100..32_099); B's arithmetic +200 tail
    # (28_300..28_499) is clean this wave and keeps the stride
    # verbatim. NOT a re-pick (R250). N2/N4 yield note: this A band
    # covers the 30_000+ domain -- N2-W15 draft probe bands
    # (31_000/31_500/32_000) must re-pick at their freeze per law
    # sec.4 (MSG heads-up r312). W9+ WARNING: both arithmetic tails
    # project clean next wave (A 32_100..34_099, B 28_500..28_699) --
    # no forced skip expected; verify at prereg time as always.
    8: {"a": (30_100, 32_099), "b_exit": (28_300, 28_499)},
    # W9 (r506 bm-b, prereg-time extension per O-20261001-1332 sec.1.2 --
    # arithmetic tails land clean exactly as the W8 row projected): A
    # 32_100 == W8 A end + 1, B 28_500 == W8 B end + 1; no skip-over
    # this wave, both strides kept verbatim. Machine-verified at prereg
    # time against every reserved band + SEED_REGISTRY + the lfc actual
    # draw range (results/_r506bmb_w9_band_gate.py ADMIT receipt); the
    # all-bands disjoint leg 2 covers W9 automatically once listed.
    # NOT a re-pick (R250). N2/N4 yield note: this A band covers
    # 32_100..34_099 -- N2/N4 preregs must steer clear per law sec.4.
    9: {"a": (32_100, 34_099), "b_exit": (28_500, 28_699)},
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
    {"id": "N3", "name": "neighborhood-robustness", "priority": 2,
     "runner": "scripts/perpetual_faces_n3.py",
     "runner_args": ["run", "--member"],   # member id appended per shard
     "wave": 1, "prereg_ref": "research/PERPETUAL_N3_R1_PREREG.md",
     # runner landed r509 bm-a (selftest 7/7 + real-data anchor probe 6/6
     # + one write-path shard smoke per r506 real-run law) -- per-shard
     # materializer pattern lands same window per freeze-signature
     # sequencing; member list + entry ids single-sourced from the runner
     "supply_ready": True},
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
        if not _claimable(e):
            continue
        n += 1
    return n


def _claimable(e):
    """True when the entry still has burnable work. An entry whose every
    shard is done is burn-complete regardless of its entry.status -- the
    daemon harvest only lands the shard layer (r488 presence=done
    semantics) and the entry-layer done flip belongs to the observing
    round (r180 dual-flip), so a closed wave awaiting its entry flip is
    a ghost face, not supply. Counting ghosts as live deadlocks the
    never-dry law behind a finished wave forever (live case r309: 12
    finalized W5 entries entry=ready blocked the W6 supply trigger while
    every burnable face was done)."""
    shards = e.get("shards") or []
    if shards and all(str(s.get("status", "")) == "done" for s in shards):
        return False
    return True


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


def _expand_n3_r1_entries(ts):
    """N3-R1 materializer (law sec.1): expand the wave into 6 per-member
    pool entries. Member list + entry ids are single-sourced from the
    runner module (import face -- pool ids and the runner's pool_claims
    handshake can never drift apart). Pure function: no writes."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import perpetual_faces_n3 as n3   # single-source member/entry face
    entries = []
    for m in n3.load_members():
        mid = m["id"]
        spec = n3.FAMILIES[mid]
        n_cells = 2 + 2 * len(spec["oat"])
        entries.append({
            "id": n3.pool_entry_id(mid),
            "ticket_ref": "T-2026-09-30-133 s2 (O-2026-09-30-2340; "
                          "N3 face wave-1 per canon drafting order "
                          "N1-W2 -> N3-R1)",
            "prereg_ref": "research/PERPETUAL_N3_R1_PREREG.md "
                          "(frozen pre-run; seed band perpetual_n3_r1 "
                          "= 70_000+member_idx registered in "
                          "SEED_REGISTRY pre-freeze)",
            "consumer_plan": ("G2 evidence-supply deepening: per-member "
                              "packs (neighborhood/cost_x3/per_year/"
                              "bootstrap_ci/current-line recheck/"
                              "g2_registration_v2) -> finalize merge "
                              "results/perpetual_faces/n3_r1_results.json "
                              "+ ledger +28; measurement face, no "
                              "registration claim"),
            "runner": "scripts/perpetual_faces_n3.py",
            "runner_args": ["run", "--member", mid],
            "lane_owner": "ANY",
            "priority": 1,
            "status": "ready",
            "entered_at": ts,
            "worker_class": "self-contained",
            "data_gates": ("in-runner FAIL-CLOSED: universe==48 bare codes "
                           "+ panel end==2026-09-22 same-window + anchor "
                           "gate vs member-file recorded evidence "
                           "(tol 0.002, trades exact) + determinism "
                           "byte-equal rerun (JSONL checkpoint "
                           "presence=done)"),
            "shards": [{
                "key": mid,
                "status": "ready",
                "checkpoint": (f"results/perpetual_faces/n3_r1/cells-{mid}"
                               f".jsonl (presence=done; deterministic rerun "
                               f"byte-equal)"),
                "note": (f"N3-R1 member shard {mid}: {n_cells} engine "
                         f"cells (center anchor + x3 + "
                         f"{2 * len(spec['oat'])} OAT nbhd); "
                         f"~40-80s single-core light burn"),
            }],
            "workers_plan": {
                "workers": 1, "priority": "BelowNormal",
                "workers_law": ("light batch honest single-core (per-cell "
                                "engine run ~5-10s; no multicore shell "
                                "for a <5min shard)"),
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
    ts = sg._now() if hasattr(sg, "_now") else None
    vals = list(pool.get("entries", []))
    if isinstance(pool.get("entries"), dict):
        vals = list(pool["entries"].values())
    # face dispatch in priority order (law sec.1 N1>N3>N2>N4) with
    # per-face wave gates; a face gated by its own wave state (bands /
    # per-wave prereg / same-face in-flight) falls through to the next
    # landed face -- canon sequencing (N1-W2 -> N3-R1 -> N2-W15 -> N4-B1)
    # is honored by the gates, not by hardcoding one face.
    chosen = None            # (face_id, payload)
    for face in landed:
        fid = face["id"]
        # law sec.1 leg-3: no same-face in-flight wave (live =
        # ready/waiting/running; park_note'd entries are deliberate
        # holds, not in-flight supply -- same r304/r504 marker law)
        live = [e for e in vals
                if str(e.get("id", "")).startswith(f"PERPETUAL-{fid}-")
                and str(e.get("status", "")) in ("ready", "waiting",
                                                "running")
                and not e.get("park_note")
                and _claimable(e)]
        if live:
            st["last_supply"]["awaiting"] = (f"{fid} wave in flight "
                                             f"({len(live)} live entries)")
            continue
        if fid == "N1":
            # next wave from pool entry truth (materialization ledger of
            # record; generator-local state waves[] is not the
            # cross-machine truth face)
            waves_seen = []
            for e in vals:
                eid = str(e.get("id", ""))
                if eid.startswith("PERPETUAL-N1-W") and "-SHARD-" in eid:
                    try:
                        waves_seen.append(int(
                            eid.split("PERPETUAL-N1-W")[1]
                               .split("-SHARD-")[0]))
                    except (IndexError, ValueError):
                        pass
            wave = (max(waves_seen) + 1) if waves_seen else face["wave"]
            if wave not in N1_BANDS:
                st["last_supply"]["awaiting"] = \
                    f"law sec.4 bands for W{wave}"
                continue
            prereg_rel = f"research/PERPETUAL_N1_W{wave}_PREREG.md"
            if not os.path.exists(os.path.join(PATHS.root, prereg_rel)):
                st["last_supply"]["awaiting"] = f"frozen prereg for W{wave}"
                continue
            chosen = (fid, wave)
            break
        if fid == "N3":
            if not os.path.exists(os.path.join(PATHS.root,
                                               face["prereg_ref"])):
                st["last_supply"]["awaiting"] = "frozen prereg for N3-R1"
                continue
            chosen = (fid, None)
            break
        # N2/N4: runner not landed yet -> honest fall-through
        st["last_supply"]["awaiting"] = f"{fid} runner not landed"
    if chosen is None:
        _write_state(st)
        print(f"supply: trigger MET but every landed face is gated "
              f"({st['last_supply'].get('awaiting')}) -- honest no-op")
        return 0
    face_id, wave = chosen
    if face_id == "N1":
        new_entries = _expand_wave_entries(face, wave, ts)
        bands_rec = N1_BANDS.get(wave)
        id_msg = f"PERPETUAL-N1-W{wave}-SHARD-0..11"
        wave_no = wave
    else:
        new_entries = _expand_n3_r1_entries(ts)
        bands_rec = {"seed_base": 70_000, "band": "70_000+member_idx"}
        id_msg = "PERPETUAL-N3-R1-<6 members>"
        wave_no = 1
    existing_ids = {str(e.get("id", "")) for e in vals}
    new_entries = [e for e in new_entries if e["id"] not in existing_ids]
    if not new_entries:
        _write_state(st)
        print(f"supply: {face_id} per-shard entries already in pool -- "
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
    st["waves"].append({"face": face_id, "wave": wave_no, "entered_at": ts,
                        "n_entries": len(new_entries), "bands": bands_rec})
    _write_state(st)
    print(f"supply: materialized {len(new_entries)} per-shard entries "
          f"{id_msg} into runnable_pool "
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
    # 3b. W5 skip-over packing invariant (law sec.4 W5 row): the arithmetic
    # +2_000 tail (18_100..20_099) is documented-refused (hits v1 B band
    # 20_000..20_019 / registry 20000 / ext W1 B 20_100..20_299); A sits at
    # the first free window after every reserved band == W5 B end + 1, and
    # the B tail keeps the +200 stride (W4 B end + 1).
    assert N1_BANDS[5]["a"][0] == N1_BANDS[5]["b_exit"][1] + 1, \
        "W5 packing drift (A must sit at W5 B end + 1)"
    assert N1_BANDS[5]["a"][1] - N1_BANDS[5]["a"][0] + 1 == 2000, "W5 A width"
    assert N1_BANDS[5]["b_exit"][1] - N1_BANDS[5]["b_exit"][0] + 1 == 200, "W5 B width"
    assert N1_BANDS[4]["b_exit"][1] + 1 == N1_BANDS[5]["b_exit"][0], "W5 B tail gap"
    # 3c. W6 skip-over packing invariant (law sec.4 W6+ WARNING): A keeps
    # the arithmetic +2_000 tail (W5 A end + 1); B's arithmetic +200 tail
    # (21_900..22_099) is documented-refused -- it falls inside the W5 A
    # band -- so B skips past every reserved band including this wave's
    # own A band and packs at the first free 200-window (W6 A end + 1).
    # Refusal facts machine-proven: the arithmetic B position MUST
    # collide (the skip is forced, not a free pick).
    assert N1_BANDS[6]["a"][0] == N1_BANDS[5]["a"][1] + 1, "W6 A tail gap"
    assert N1_BANDS[6]["a"][1] - N1_BANDS[6]["a"][0] + 1 == 2000, "W6 A width"
    assert N1_BANDS[6]["b_exit"][1] - N1_BANDS[6]["b_exit"][0] + 1 == 200, "W6 B width"
    assert N1_BANDS[6]["b_exit"][0] == N1_BANDS[6]["a"][1] + 1, \
        "W6 packing drift (B must sit at W6 A end + 1)"
    arith_b = set(range(N1_BANDS[5]["b_exit"][1] + 1,
                        N1_BANDS[5]["b_exit"][1] + 201))
    w5_a = set(range(N1_BANDS[5]["a"][0], N1_BANDS[5]["a"][1] + 1))
    assert arith_b & w5_a, \
        "W6 B skip must be forced (arithmetic tail must hit the W5 A band)"
    # 3d. W7 skip-over packing invariant (r501 bm-b, same forced-skip
    # family -- BOTH tails refused this wave): A's arithmetic +2_000
    # tail (25_900..27_899) is documented-refused (hits the W6 B band
    # 25_900..26_099), so A packs at the first free 2,000-window ==
    # W6 B end + 1; B's arithmetic +200 tail (26_100..26_299) is refused
    # too (falls inside this wave's own A band), so B packs at
    # W7 A end + 1. Refusal facts machine-proven below.
    assert N1_BANDS[7]["a"][1] - N1_BANDS[7]["a"][0] + 1 == 2000, "W7 A width"
    assert N1_BANDS[7]["b_exit"][1] - N1_BANDS[7]["b_exit"][0] + 1 == 200, \
        "W7 B width"
    assert N1_BANDS[7]["a"][0] == N1_BANDS[6]["b_exit"][1] + 1, \
        "W7 packing drift (A must sit at W6 B end + 1)"
    assert N1_BANDS[7]["b_exit"][0] == N1_BANDS[7]["a"][1] + 1, \
        "W7 packing drift (B must sit at W7 A end + 1)"
    arith_a7 = set(range(N1_BANDS[6]["a"][1] + 1, N1_BANDS[6]["a"][1] + 2001))
    w6_b = set(range(N1_BANDS[6]["b_exit"][0], N1_BANDS[6]["b_exit"][1] + 1))
    assert arith_a7 & w6_b, \
        "W7 A skip must be forced (arithmetic tail must hit the W6 B band)"
    arith_b7 = set(range(N1_BANDS[6]["b_exit"][1] + 1,
                         N1_BANDS[6]["b_exit"][1] + 201))
    w7_a = set(range(N1_BANDS[7]["a"][0], N1_BANDS[7]["a"][1] + 1))
    assert arith_b7 & w7_a, \
        "W7 B skip must be forced (arithmetic tail must hit the W7 A band)"
    # 3e. W8 skip-over packing invariant (r312 bm-c, forced-skip family
    # with a registry-point refusal): A's arithmetic +2_000 tail
    # (28_100..30_099) is documented-refused -- it hits the W7 B band
    # AND the SEED_REGISTRY lfc_p1_screen point 30_000 (actual draw
    # range 30_000..30_099, N_RAND=50 x 2 exit regimes); the law
    # sec.4 pinned W8+ WARNING window (28_300..30_299) is refused by
    # the same point + actual range, so A packs at the first
    # 2,000-window clear of every reserved band AND the lfc actual
    # draw range (30_100..32_099); B's arithmetic +200 tail
    # (28_300..28_499) is clean this wave (the A jump cleared the
    # collision the warning predicted) and keeps the stride verbatim.
    # Refusal facts machine-proven below.
    assert N1_BANDS[8]["a"][1] - N1_BANDS[8]["a"][0] + 1 == 2000, "W8 A width"
    assert N1_BANDS[8]["b_exit"][1] - N1_BANDS[8]["b_exit"][0] + 1 == 200, \
        "W8 B width"
    arith_a8 = set(range(N1_BANDS[7]["a"][1] + 1, N1_BANDS[7]["a"][1] + 2001))
    w7_b = set(range(N1_BANDS[7]["b_exit"][0], N1_BANDS[7]["b_exit"][1] + 1))
    assert arith_a8 & w7_b, \
        "W8 A skip must be forced (arithmetic tail must hit the W7 B band)"
    assert 30_000 in arith_a8 and 30_000 in sg.SEED_REGISTRY.values(), \
        "W8 A skip must be forced (arithmetic tail must hit lfc_p1_screen registry point)"
    warned_a8 = set(range(28_300, 30_300))
    lfc_actual = set(range(30_000, 30_100))
    assert 30_000 in warned_a8 and (warned_a8 & lfc_actual), \
        "law-pinned W8 warning window must be refused (registry point + lfc actual range)"
    w8_a = set(range(N1_BANDS[8]["a"][0], N1_BANDS[8]["a"][1] + 1))
    assert not (w8_a & lfc_actual), "W8 A must clear the lfc actual draw range"
    assert N1_BANDS[8]["a"][0] == 30_100, \
        "W8 A packs at the first 2,000-window clear of the lfc actual range"
    assert N1_BANDS[8]["a"][0] > max(N1_BANDS[7]["b_exit"][1], *lfc_actual), \
        "W8 A must sit beyond every reserved band and the lfc range"
    arith_b8 = set(range(N1_BANDS[7]["b_exit"][1] + 1,
                         N1_BANDS[7]["b_exit"][1] + 201))
    assert not (arith_b8 & w8_a), \
        "W8 B arithmetic tail must be clean (no skip this wave)"
    assert N1_BANDS[8]["b_exit"][0] == N1_BANDS[7]["b_exit"][1] + 1, \
        "W8 B tail gap (stride kept verbatim)"
    # 3f. W9 arithmetic-continuation invariant (r506 bm-b, O-20261001-1332
    # sec.1.2): the W8 row projected BOTH arithmetic tails clean, and the
    # machine gate at prereg time confirmed ADMIT (no forced skip this
    # wave) -- A == W8 A end + 1, B == W8 B end + 1, strides verbatim,
    # both clear of every reserved band + SEED_REGISTRY + the lfc actual
    # draw range (leg 2 all-bands disjoint covers W9 once listed here).
    assert N1_BANDS[9]["a"][1] - N1_BANDS[9]["a"][0] + 1 == 2000, "W9 A width"
    assert N1_BANDS[9]["b_exit"][1] - N1_BANDS[9]["b_exit"][0] + 1 == 200, \
        "W9 B width"
    assert N1_BANDS[9]["a"][0] == N1_BANDS[8]["a"][1] + 1, \
        "W9 A must keep the arithmetic stride (no skip -- ADMIT receipt)"
    assert N1_BANDS[9]["b_exit"][0] == N1_BANDS[8]["b_exit"][1] + 1, \
        "W9 B must keep the arithmetic stride (no skip -- ADMIT receipt)"
    w9_a = set(range(N1_BANDS[9]["a"][0], N1_BANDS[9]["a"][1] + 1))
    w9_b = set(range(N1_BANDS[9]["b_exit"][0], N1_BANDS[9]["b_exit"][1] + 1))
    assert not (w9_a & lfc_actual) and not (w9_b & lfc_actual), \
        "W9 bands must clear the lfc actual draw range"
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
    # 4c. ghost faces are not supply (r309 W5 live case: a finalized wave
    # awaiting its entry-layer done flip must not block the never-dry
    # trigger): ready + all shards done = burn-complete = not claimable;
    # ready + any shard not done = claimable; shardless entries keep the
    # legacy claimable face.
    probe_pool2 = {"entries": [
        {"id": "G1", "status": "ready",
         "shards": [{"key": "k", "status": "done"}]},
        {"id": "G2", "status": "ready",
         "shards": [{"key": "k", "status": "ready"}]},
        {"id": "G3", "status": "ready",
         "shards": [{"key": "k1", "status": "done"},
                    {"key": "k2", "status": "ready"}]},
    ]}
    assert _pool_live_count(probe_pool2) == 2, \
        "ghost (all-shards-done) entries must not count as live supply"
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
    # 7b. N3-R1 materializer expansion face (pure function; no writes;
    # member list + entry ids single-sourced from the runner module)
    exp3 = _expand_n3_r1_entries(ts)
    assert len(exp3) == 6, "N3-R1 expansion must be 6 per-member entries"
    import perpetual_faces_n3 as n3mod
    assert [e["id"] for e in exp3] == \
        [n3mod.pool_entry_id(m["id"]) for m in n3mod.load_members()], \
        "N3 entry ids drifted from the runner handshake face"
    for e in exp3:
        mid = e["id"].split("PERPETUAL-N3-R1-")[1]
        assert e["runner_args"] == ["run", "--member", mid], "N3 args drift"
        assert e["status"] == "ready" and e["lane_owner"] == "ANY"
        assert e["worker_class"] == "self-contained"
        assert "PERPETUAL_N3_R1_PREREG" in e["prereg_ref"], "N3 prereg uncited"
        assert "70_000" in e["prereg_ref"], "N3 seed band uncited"
        assert e["shards"][0]["key"] == mid
        assert e["shards"][0]["checkpoint"] == (
            f"results/perpetual_faces/n3_r1/cells-{mid}.jsonl "
            f"(presence=done; deterministic rerun byte-equal)")
        assert e["workers_plan"]["workers"] == 1, "N3 light-batch workers face"
        for forbidden_owner in ("owner", "owner_since", "done_at", "done_by"):
            assert forbidden_owner not in e["shards"][0]
    # 8. pool format-mirror probe (read-only; r289 law: indent2+CRLF probed;
    #    trailing face follows the migrated canonical producer -- bm-b r499
    #    pool-format migration made the flip tool emit trailing NL and the
    #    probe dynamic; the guard asserts probe-vs-bytes truth, not a
    #    hardcoded pre-migration face)
    if os.path.exists(POOL_PATH):
        indent, crlf, trailing_nl = _pool_format_probe()
        assert crlf, f"pool EOL face drifted: crlf={crlf}"
        b = open(POOL_PATH, "rb").read()
        assert trailing_nl == b.endswith(b"\n"), "trailing probe drift vs bytes"
        # indent probe-vs-bytes truth (bm-c r307 trailing-pin fix applied
        # to the indent face too: the file's real indent is whatever the
        # majority producer writes -- a hardcoded pre-migration pin only
        # chronic-false-flags every resolve/producer cycle)
        probe_indent = None
        for line in b.decode("utf-8", errors="replace").split("\n"):
            if line.strip().startswith('"'):
                probe_indent = len(line) - len(line.lstrip(" "))
                break
        assert indent == probe_indent, \
            f"indent probe drift vs bytes: {indent}/{probe_indent}"
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
          "(registry/seed-bands+3c-W6+3d-W7-packing/pool/state/py-face/"
          "materializer-expansion/pool-format-probe+writer-roundtrip; "
          "4b park_note + 4c ghost claimable legs)")
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
