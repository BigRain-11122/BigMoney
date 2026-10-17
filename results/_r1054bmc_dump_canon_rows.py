"""r1054: dump V5-relevant canon rows (female ID blocks + object shots) from mv_full_shots.py."""
import importlib.util, json

spec = importlib.util.spec_from_file_location(
    "mfs", r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\30s-reel-v1\mv_full_shots.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
want = ["R06_museum_verse", "E04_replay_faces", "C04_words_alive", "D05_words_warm",
        "B01_weary", "C01_carver_face", "D01_carver_words", "E03_gaze_meet",
        "INT1_hall_breath", "INT2_row_wake", "INT3_her_walk", "INT4_first_reflection", "INT5_approach"]
rows = {r[0]: r for r in m.NEW}
out = {}
for w in want:
    r = rows.get(w)
    if r is None:
        out[w] = None
        continue
    out[w] = {"len": len(r), "row": [str(x) for x in r]}
with open(r"results\_r1054bmc_canon_rows.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("dumped", {k: (v["len"] if v else None) for k, v in out.items()})
