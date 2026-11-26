# GPU alias writer census

_generated 2026-11-26T13:37:14+0800 · verdict **INCONSISTENT**_

bm-b free family spreads 3758.1 MiB (gpu.free_gb vs vram_free_gb); bm-b used family spreads 3549.0 MiB (gpu_used_mib vs gpu.mem_used_mib); 3 GiB-named key(s) carry MiB numbers, so a reader of the face is told a number that cannot be GiB; 8 alias(es) are also spelled outside gpu_face/heartbeat_write, so one of them can age alone

## Why this face exists

`fleet: GPU face self-consistent on heartbeat` has been carried red twice (r2131, r2132) with a 76 MiB spread among 19 FREE aliases. The leg can only say two numbers disagree; it cannot say who put them there. A red that nobody can act on is a red readers learn to skip (r1789), so this face names the writer and the spelling.

## Faces read

| machine | keys | free spread (MiB) | high | low | audit findings |
|---|---|---|---|---|---|
| bm-a | 27 | 14.0 | free_vram_mb | free_vram_gb | 0 |
| bm-b | 28 | 3765.1 | gpu.free_gb | gpu_mem_free_mib | 2 |
| bm-c | 33 | 5.0 | free_vram_mb | free_vram_gb | 0 |

**bm-b** carries two free-VRAM readings 3765.1 MiB apart: `gpu.free_gb` says 7342.1 MiB and `gpu_mem_free_mib` says 3577.0 MiB. A reader of that heartbeat has no way to know which half is the GPU and which half is an older probe left behind.

**bm-b** likewise carries used readings 3549.0 MiB apart (`gpu_mem_used_mib` 4404.0 MiB vs `gpu.mem_used_mib` 855 MiB).

## Names that promise GiB and carry MiB

The toolchain resolves the unit from the spelling, so a `*_gib` key is read as MiB and writer and checker agree with each other. A reader is handed the second column.

| machine | key | on the face | what it actually is |
|---|---|---|---|
| bm-a | `gpu_free_vram_gib` | 1038 GiB | 1038 MiB (1.0 GiB) |
| bm-c | `gpu_free_gib` | 13829 GiB | 13829 MiB (13.5 GiB) |
| bm-c | `gpu_free_vram_gib` | 13829 GiB | 13829 MiB (13.5 GiB) |

## Aliases spelled outside the owning tools

`Tools/gpu_face.py` and `Tools/heartbeat_write.py` restate every alias from one probe. A file below also spells the key: if it writes its own probe into the heartbeat, half the family moves and the other half keeps the old snapshot.

| key | other files |
|---|---|
| `free_vram_gb` | `Tools/machine_health_face.py` |
| `gpu.free_gb` | `Tools/machine_health_face.py` |
| `gpu_free_gb` | `Tools/machine_health_face.py` |
| `gpu_used_mb` | `scripts/model_slot_bench_bma.py`, `scripts/t70_midterm_dossier.py` |
| `gpu_vram_free_gb` | `Tools/machine_health_face.py` |
| `mem_used_mb` | `scripts/compute_audit.py` |
| `vram_free_gb` | `Tools/idle_trigger.py`, `scripts/model_slot_bench_bmc.py` |
| `vram_used_mb` | `scripts/line_arbiter.py` |

## Against the live probe

nvidia-smi on **bm-c** right now: 13838 MiB free of 16384 MiB. Only that face is judged against it -- a probe on this box says nothing about another box's card, which is why the other machines are absent from this section rather than marked stale.

- every free alias on every face is within 64 MiB of the live probe.


## Fix order (for a contention-free round)

1. Drop or rename the `*_gib` spellings: a key that cannot be read as its own name is a trap regardless of who writes it (`gpu_face.key_unit` is the single place to change, and `restate()` will follow).

2. Move any second writer onto `heartbeat_write.write()` instead of writing GPU keys itself, so one probe per round owns the whole family.

3. Only then re-run the leg: while a second writer exists the spread can reappear on any round, which is why it was carried twice rather than fixed once.
