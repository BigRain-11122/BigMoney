# DIGEST 2026-11-03 r1392 (bm-b): the 176.8 MiB was a definition, not an age

Smoke was red on the only leg it is allowed to be red on for bm-b:

    fleet: GPU face self-consistent on heartbeat
    findings=[{'family': 'free', 'spread_mib': 176.8,
               'high': 'gpu_free_mib', 'low': 'vram_free_gb', 'n_keys': 18}]

## What the face said

    gpu_free_mib = 2061   (canonical: total - used, 8192 - 6131)
    vram_free_gb = 1.84   (1884 MiB, from nvidia-smi's own memory.free)

## What one instant says

    nvidia-smi --query-gpu=memory.total,memory.used,memory.free
    8192, 6293, 1726      ->  total - used = 1899,  reservation = 173

The gap is the driver reservation: `memory.free` excludes it, `total - used` includes it. It is a
constant, so it does not heal with a probe -- which is exactly what r1177, r1284, r1363 and r1314
each tried (rewrite the canonical spellings; the alternate spelling returns next round).

## What changed

`Tools/gpu_face.py`:

- `parse_smi` reads the fourth field (`memory.free`) when present and stays compatible with the
  three-field fixtures;
- `fields_from` publishes `gpu_reserved_mib` (free_derived - free_smi) and `gpu_memory_semantics`
  naming the canonical definition (`free = total - used`);
- `audit` is unchanged in strictness -- one name carrying two quantities is still a finding -- but a
  free-family spread that equals the published reservation now carries `definition_note`, so the
  next reader is not asked to re-derive whether it is staleness;
- selftest 41/41 (ten new legs: the 4th field, the 3-field fallback, the reservation, the two new
  keys not being memory spellings, a memory.free spelling being reported, and the note being
  attached).

Live face after `python Tools/gpu_face.py apply`:

    findings = []        gpu_reserved_mib = 173       gpu_free_mib = 1899
    n_gpu_keys = 35      gpu_purged = ['vram_used_gb'] (a stray two-decimal used spelling)

## Why it matters beyond bm-b

A face that publishes "free" twice under two spellings is not reproducible by construction; any
consumer reading one of them reads a different quantity than the consumer beside it. The face now
says which definition it uses and publishes the constant that separates the other one.

## Card

`knowledge/METHODOLOGY_ASSETS.md` E374.