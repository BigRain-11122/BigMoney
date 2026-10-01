"""r529 bm-a band-overlap machine evidence: N3-R1 seed values vs N1 W13 A band.

Discovery window: 2026-10-01 18:2x (r529 S3 never-dry supply scan, W18 gate
prep). Question: does any frozen N1 wave band overlap the N3-R1 bootstrap-CI
seed values (SEED_BASE + member index, frozen r509 bm-a, SEED_REGISTRY
entry perpetual_n3_r1=70_000 registered as a single base point)?

Legs:
  leg1  derive N3-R1 actual seed set from the runner source (no hand-copy).
  leg2  derive every N1 WAVE_CONFIGS band from the N1 runner (A/B per wave).
  leg3  intersect; any nonempty = collision face (print per-wave).
  leg4  cross-check SEED_REGISTRY representation (base point vs band).
Zero network, deterministic, read-only. Exit 0 always (evidence face);
verdict printed for the round report.
"""
import re
import sys

sys.path.insert(0, "scripts")

N3_SRC = "scripts/perpetual_faces_n3.py"


def main() -> int:
    # member ids + SEED_BASE single-sourced from the runner module
    import perpetual_faces_n3 as n3
    n3_base = n3.SEED_BASE
    names = sorted(n3.FAMILIES)
    assert names, "FAMILIES empty"
    n3_seeds = set(range(n3_base, n3_base + len(names)))
    print(f"leg1 N3-R1 seeds: base={n3_base} members={len(names)} "
          f"values={min(n3_seeds)}..{max(n3_seeds)}")

    import perpetual_faces_n1 as n1
    collisions = []
    for wave, cfg in sorted(n1.WAVE_CONFIGS.items()):
        a = set(range(cfg["a_seed_base"], cfg["a_seed_base"] + 2000))
        b = set(range(cfg["b_exit_seed_base"], cfg["b_exit_seed_base"] + 200))
        for tag, band in (("A", a), ("B", b)):
            inter = sorted(n3_seeds & band)
            if inter:
                collisions.append((wave, tag, inter))

    import science_gates as sg
    reg = sg.SEED_REGISTRY
    n3_reg = {k: v for k, v in reg.items() if "n3" in k.lower()}
    print(f"leg4 SEED_REGISTRY n3 entries: {n3_reg} "
          f"(band fully registered: "
          f"{n3_seeds <= set(reg.values())})")

    if collisions:
        for wave, tag, inter in collisions:
            print(f"leg3 COLLISION: N1 W{wave} {tag} band x N3-R1 seeds "
                  f"-> {inter} (count={len(inter)})")
    else:
        print("leg3 clean: no N1 band overlaps N3-R1 seeds")
    print(f"verdict: {'OVERLAP-FOUND' if collisions else 'CLEAN'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
