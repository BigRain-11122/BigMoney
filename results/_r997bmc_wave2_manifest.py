# -*- coding: utf-8 -*-
# _r997bmc_wave2_manifest.py -- wave-2 fact-freeze (32-slot INT8 768P re-production manifest)
# Law: facts machine-derived, zero transcription (r583). Sources:
#   - mv_full_shots.NEW (44 rows, i2v prompts) via module import (data-only module)
#   - ARCH_FRAMES = K:\Fluxgroup\archive\mv0001-kf-frames-bmc-r840\frames_full (44-frame archive)
#   - assembly rows = build_full_mv_v2.build_rows() shape WITHOUT bm-a path side-effects
#     (re-derived from NEW/REUSE lists read as data; DROP_NEW + v2 bridges replicated)
# Honest split: this freezes WHAT to burn + WHERE source frames are; H3 reignite = next window.
import io, json, os, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SHOTS = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\30s-reel-v1\mv_full_shots.py"
ARCH = r"K:\Fluxgroup\archive\mv0001-kf-frames-bmc-r840\frames_full"
BMC_B = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc"

# mv_full_shots imports prompt_lexicon (LX) from patched-scripts -- that dir exists in group tree
spec = importlib.util.spec_from_file_location("mfs", SHOTS)
mfs = importlib.util.module_from_spec(spec)
sys.modules["mfs"] = mfs
spec.loader.exec_module(mfs)
NEW = mfs.NEW
REUSE = mfs.REUSE
DROP_NEW = {"INT1_hall_breath", "INT2_row_wake", "INT3_her_walk", "INT4_first_reflection",
            "INT5_approach", "C01_carver_face", "D03_two_worlds"}
V2_BRIDGE = ["INT1_desk_breath", "INT2_paper_fight", "INT3_photo_stare", "INT4_rubbing_glow",
             "INT5_head_bow", "C01_carver_face", "D03_two_worlds", "D03b_direct_gaze", "E01c_first_line"]
E01B_NEW_END = 191.60

# assembly rows (shape-faithful re-derive of build_rows(), zero side effects)
rows = []
for sid, t0, t1, v, kf_p, iv_p in NEW:
    if sid in DROP_NEW:
        continue
    rows.append([sid, t0, t1, v, sid + ".mp4", True, iv_p])
for sid in V2_BRIDGE[:-1] + [V2_BRIDGE[5]]:
    pass  # handled explicitly below with time windows
rows.append(["INT1_desk_breath", 0.00, 3.50, 0.85, "INT1_desk_breath.mp4", True, None])
rows.append(["INT2_paper_fight", 3.50, 7.50, 0.92, "INT2_paper_fight.mp4", True, None])
rows.append(["INT3_photo_stare", 7.50, 11.50, 0.90, "INT3_photo_stare.mp4", True, None])
rows.append(["INT4_rubbing_glow", 11.50, 14.60, 0.95, "INT4_rubbing_glow.mp4", True, None])
rows.append(["INT5_head_bow", 14.60, 17.50, 0.88, "INT5_head_bow.mp4", True, None])
rows.append(["C01_carver_face", 77.34, 80.18, 0.90, "C01_carver_face.mp4", True, None])
rows.append(["D03_two_worlds", 147.84, 150.54, 0.85, "D03_two_worlds.mp4", True, None])
rows.append(["D03b_direct_gaze", 150.54, 152.14, 0.90, "D03b_direct_gaze.mp4", True, None])
for r in REUSE:
    sid, t0, t1, v, k = r[0], r[1], r[2], r[3], r[4]
    if sid == "E01b_sand":
        rows.append([sid, t0, E01B_NEW_END, v, k + ".mp4", False, None])
        rows.append(["E01c_first_line", E01B_NEW_END, t1, 0.90, "E01c_first_line.mp4", True, None])
    else:
        rows.append([sid, t0, t1, v, k + ".mp4", False, None])
rows.sort(key=lambda r: r[1])

# frame availability census
def frame_candidates(sid):
    out = []
    for root in (ARCH, BMC_B):
        for ext in (".png", ".jpg"):
            p = os.path.join(root, sid + ext)
            if os.path.isfile(p):
                out.append(p)
    # archive naming variants: sid without suffix / sid + seed variants
    if not out and os.path.isdir(ARCH):
        for f in os.listdir(ARCH):
            if f.startswith(sid) and f.lower().endswith((".png", ".jpg")):
                out.append(os.path.join(ARCH, f))
    return out

manifest = {"frozen_ts": "r997 2026-10-14 15:0x", "order_ref": "O-20261014-1035 wave-2 (13:2x revision: 29 direct + 3 new shots INT1_desk_breath/D01_carver_words/B02_far_home)",
            "engine": "H3 INT8 768P 1344x768 length-124", "burns": [], "gaps": []}
arch_list = sorted(os.listdir(ARCH)) if os.path.isdir(ARCH) else []
print("ARCH frame count:", len(arch_list))
for sid, t0, t1, v, fname, is_new, iv in rows:
    if not is_new:
        continue  # REUSE = FLUX local history, not wave-2 face
    cands = frame_candidates(sid)
    ent = {"sid": sid, "t0": t0, "t1": t1, "speed": v, "src_mp4": fname,
           "frame": cands[0] if cands else None, "i2v_prompt_in_NEW": bool(iv)}
    manifest["burns"].append(ent)
    if not cands:
        manifest["gaps"].append(sid)
print("NEW-face burn slots:", len(manifest["burns"]))
print("GAPS (no source frame found):", manifest["gaps"] if manifest["gaps"] else "NONE")
# three 13:2x new shots census
for probe in ("INT1_desk_breath", "D01_carver_words", "B02_far_home"):
    c = frame_candidates(probe)
    print("new-shot %-18s frame: %s" % (probe, c[0] if c else "ABSENT (director seat must supply KF before burn)"))
out_path = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\wave2_manifest_r997.json"
io.open(out_path, "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=1))
print("MANIFEST FROZEN ->", out_path)
