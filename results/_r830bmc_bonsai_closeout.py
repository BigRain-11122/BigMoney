"""r830 bm-c: D-20261010-04 bigmoney face -- formal closeout annotation on
Bonsai trial tickets T-99/T-100 (both already status=done; this adds the
D-20261010-04 ruling close: observe maintained, not adopted, re-eval
conditions). Idempotent: skips if key already present."""
import json, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TICKETS = ["fleet/tasks/T-2026-09-28-99-P1.json",
           "fleet/tasks/T-2026-09-28-100-P1.json"]
KEY = "closeout_D-20261010_04"
VAL = ("2026-10-10 D-20261010-04 (r830 bm-c receipt): Bonsai trial line "
       "FORMALLY CLOSED = observe maintained, NOT adopted (merged verdict "
       "T-99 bm-b + T-100 bm-c: 16GB-tier tg128 40.52+-1.10 / 40.75+-0.30 "
       "tok/s meets official '30+' claim; CPU tier 0.848-1.33 tok/s = "
       "unusable per BigStream/BigLife reject/observe corroboration). "
       "Re-evaluation conditions = GPU idle-window tg128 live test + new "
       "hard requirement trigger. Do not reopen without both conditions.")

for rel in TICKETS:
    p = os.path.join(ROOT, *rel.split("/"))
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    if KEY in d:
        print("skip (already closed):", rel)
        continue
    assert d.get("status") == "done", rel + " not done: " + str(d.get("status"))
    d[KEY] = VAL
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("closed:", rel, "id=" + str(d.get("id")))
print("bonsai closeout done")
