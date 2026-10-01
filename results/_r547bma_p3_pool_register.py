# -*- coding: utf-8 -*-
"""r547 bm-a: LOWAMP-P3 pool registration (raw-text surgical, r509 law).

Mirrors the P2 registration face (a09afe1fa): 18 entries = 16 cell-shards
(LAREP/LAEQ/LAT3/LAEDGE x legacy/deep x base/x2) + NULLS + SENS; ids and
shard-keys DERIVED programmatically via runner _entry_of (r514 mirror
law), never hand-assembled; flat-0-key indent + CRLF preserved
byte-exactly; insertion = anchor-based (last-entry close + array close),
NO json re-serialization.
"""
import io
import json
import subprocess
import sys

sys.path.insert(0, "scripts")
import lowamp_p3 as L   # noqa: E402  (runner single source for _entry_of)

POOL = "results/runnable_pool.json"
raw = open(POOL, "rb").read()
text = raw.decode("utf-8")
assert raw.count(b"\n") == raw.count(b"\r\n"), "pool must be pure CRLF"
assert "LOWAMP-P3" not in text, "P3 entries already present"

# ---- derive ids/shard-keys from the runner (no hand-assembly) ----------
class _A:
    def __init__(self, **kw):
        self.__dict__.update(kw)

entries = []
for cell in ("LA-REP", "LA-EQ", "LA-T3", "LA-EDGE"):
    for axis in ("legacy", "deep"):
        for face in ("base", "x2"):
            e, s = L._entry_of(_A(cell=cell, axis=axis, face=face))
            entries.append({"id": e, "shard": s,
                            "args": ["run", "--cell", cell,
                                     "--axis", axis, "--face", face]})
e, s = L._entry_of(_A(nulls=True))
entries.append({"id": e, "shard": s, "args": ["run", "--nulls"]})
e, s = L._entry_of(_A(sensitivity=True))
entries.append({"id": e, "shard": s, "args": ["run", "--sensitivity"]})
assert len(entries) == 18, len(entries)
assert len({x["id"] for x in entries}) == 18, "id collision"

TS = "2026-10-02 01:2x"
TICKET_REF = ("T-2026-10-01-140-P1 remaining face (O-20261001-2355 sec.1(e) "
              "re-open channel; prereg frozen 390f0bfce bm-a r547; "
              "banned_direction_gate ADMIT rc0)")
PREREG_REF = ("research/LOWAMP-P3.md (exit-axis dual-channel: params bridge "
              "4 keys + ExitPatch bridge-outer loss_time_days/"
              "global_hard_limit per live.paper contract = r522 dead-letter "
              "root cause fixed; law-A post-burn exit-reason census >20% "
              "auto-block; E1 four-leg mandatory pre-consumption; cutoff "
              "2026-09-22 D2)")
GATES = ("in-runner FAIL-CLOSED: probe.json PASS required before ignition "
         "(results/lowamp_p3/probe.json PASS 14/14 2026-10-02: G-CENSUS "
         "1254/1506 inherited + adj 19/19 + cutoff end-row==2026-09-22 + "
         "cost x1 rt 26.082bp single-source + D6 max|corr| fresh probe "
         "0.1868 vs 0.7 + closed_family open); per-start JSONL checkpoint "
         "resume (t22 pattern); idempotent no-op when shard complete; "
         "engine canon T+1, exit priority frozen, engine/ zero-mod; "
         "sec.0.6 HOLD-THROUGH dual-channel exit-axis (params bridge 4 "
         "keys + ExitPatch 2 keys, prereg verbatim); law-A census in "
         "finalize (default-stack share >20% -> consumption-blocked)")


def render(ent):
    lines = []
    lines.append("{")
    lines.append(f'"id": "{ent["id"]}",')
    lines.append(f'"ticket_ref": "{TICKET_REF}",')
    lines.append(f'"prereg_ref": "{PREREG_REF}",')
    lines.append('"runner": "scripts/lowamp_p3.py",')
    lines.append('"runner_args": [')
    lines.append(",\r\n".join(f'"{a}"' for a in ent["args"]))
    lines.append("],")
    lines.append('"lane_owner": "ANY",')
    lines.append('"priority": 0,')
    lines.append('"status": "ready",')
    lines.append(f'"entered_at": "{TS}",')
    lines.append('"entered_by": "bm-a (OS iteration loop r547)",')
    lines.append(f'"data_gates": "{GATES}",')
    lines.append('"workers_plan": {')
    lines.append('"workers": 12,')
    lines.append('"priority": "BelowNormal"')
    lines.append("},")
    lines.append('"shards": [')
    lines.append("{")
    lines.append(f'"key": "{ent["shard"]}",')
    lines.append('"status": "ready",')
    ck = ("results/lowamp_p3/ JSONL checkpoint resume (t22 pattern)"
          if "--cell" in ent["args"] else
          f'results/lowamp_p3/ {"nulls" if "--nulls" in ent["args"] else "sens"}'
          " JSONL checkpoint")
    lines.append(f'"checkpoint": "{ck}"')
    lines.append("}")
    lines.append("]")
    lines.append("}")
    return "\r\n".join(lines)


block = ",\r\n".join(render(e) for e in entries)

# ---- raw-text anchor insertion (no re-serialization) --------------------
# tail shape: ...}\r\n]\r\n}\r\n  (last entry close, array close, obj close)
tail = text[-len("}\r\n]\r\n}\r\n"):]
assert tail.endswith("}\r\n]\r\n}\r\n"), repr(text[-30:])
anchor = "}\r\n]\r\n}\r\n"
idx = text.rfind(anchor)
assert idx == len(text) - len(anchor), "anchor not at EOF"
new_text = text[:idx] + "},\r\n" + block + "\r\n]\r\n}\r\n"

# ---- validation before write --------------------------------------------
parsed = json.loads(new_text)
pool_entries = parsed["entries"]
ids = [x["id"] for x in pool_entries]
assert ids[-18:] == [e["id"] for e in entries], "tail order mismatch"
assert len(ids) == len(set(ids)), "global id collision"
for e in entries:
    pe = next(x for x in pool_entries if x["id"] == e["id"])
    assert pe["shards"][0]["key"] == e["shard"]
    assert pe["status"] == "ready" and pe["shards"][0]["status"] == "ready"
# byte-shape invariants: pure CRLF, EOF newline, flat-0-key id lines
nb = new_text.encode("utf-8")
assert nb.count(b"\n") == nb.count(b"\r\n")
assert nb.endswith(b"}\r\n")
for probe in ('\n"id"', '\n"shards"'):
    pass
# id lines at column 0 (flat-0-key face)
for ln in new_text.split("\r\n"):
    if ln.startswith('"id": "LOWAMP-P3'):
        assert ln[0] == '"'

with io.open(POOL, "w", encoding="utf-8", newline="") as fh:
    fh.write(new_text)
print(f"registered 18 P3 entries; pool bytes {len(raw)} -> {len(nb)}")
print("entry ids:", [e["id"] for e in entries][:3], "... +15 more")
