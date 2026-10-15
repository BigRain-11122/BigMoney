# -*- coding: utf-8 -*-
# _r1032bmc_jayredo_precheck.py -- runner 点火前干跑校验（组装+lint+映射·零烧制）
import importlib.util, json, re, sys
BASE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
MEDIA = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001"
spec_ = importlib.util.spec_from_file_location("jay_redo_pack", BASE + r"\JAY-REDO-PACK-v1.py")
pack = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(pack)
BAD = re.compile(r"\b(no|not|never|without|don't|doesn't|nope)\b", re.I)
r1025 = json.load(open(MEDIA + r"\jayredo\jayredo_kf_r1025_progress.json", encoding="utf-8-sig"))

RESHAKE = [
 ("E01c_first_line.mp4", "A close-up at eye level of %s with his fountain pen resting lightly at the top corner of a blank pale page, chin tucked, his heavy-lidded eyes on the clean page in a drowsy focus, his fingers clearly formed around the pen barrel, the smooth blank paper glowing softly under the lamp. %s %s" % (pack.HIM_MODERN, pack.LAMP, pack.STYLE)),
 ("SIL2_ots_crowd_v4_s9018.mp4", "A medium shot over his shoulder of %s standing alone before the lit case in the empty closed hall, the long aisle clear and quiet around him in deep shadow, his calm face lit warm in three-quarter, his heavy-lidded eyes resting on the carved stone. %s %s" % (pack.HIM_MODERN, pack.CASE_NIGHT, pack.STYLE)),
 ("SING1_torch_song_v2_s9013.mp4", "A medium close-up at eye level of %s standing loose and spent before the tall stele in the Babylonian hall, shoulders slack after the long night, chin sunk, eyelids heavy and half-lowered, mouth open mid-line on a flat level line with the corners at rest, one hand hanging limp at his side, a reed-bundle torch burning warm amber in its cast bronze sconce behind his shoulder, his fringe over his brows, his face lit by the flame in three-quarter. %s %s" % (pack.HIM_SCRIBE, pack.TORCH if hasattr(pack, "TORCH") else "A thick reed-bundle torch in a cast bronze sconce bowl throws raking warm light at 2000K across him and the carved stone, the hall beyond warm film-base brown fading to black.", pack.STYLE)),
]
for shot in pack.SHOTS:
    if shot[2].startswith("校验"):
        RESHAKE.append((shot[0], shot[2].split("不达标重摇：", 1)[1]))
assert len(RESHAKE) == 6, "reshake %d" % len(RESHAKE)
REJECTS = {n for n, _ in RESHAKE}
I2V_JOBS = []
for name, win, kf, iv in pack.SHOTS:
    if name in REJECTS or kf.startswith("校验"):
        continue
    if name == "INT3_photo_stare.mp4":
        iv = iv.replace("his drowsy gaze holding the photo through one slow blink",
                       "his heavy upper lids settled lower over his drowsy gaze, the photo held through one slow blink")
        assert "heavy upper lids settled lower" in iv, "INT3 adjust miss"
    if name == "D03b_direct_gaze.mp4":
        iv = iv.replace("deep crushed shadows",
                       "deep shadows holding their amber warmth, his eyes softly readable in the case glow")
        assert "deep crushed shadows" not in iv, "D03b adjust miss"
    I2V_JOBS.append((name, iv))
assert len(I2V_JOBS) == 11, "i2v %d" % len(I2V_JOBS)
fails = []
for n, pr in RESHAKE:
    h = BAD.findall(pr)
    if h: fails.append((n, h))
for n, iv in I2V_JOBS:
    h = BAD.findall(iv)
    if h: fails.append((n, h))
# 帧映射核验
missing = [n for n, _ in I2V_JOBS if not r1025.get("done", {}).get(n, {}).get("file")]
print("RESHAKE6:", [n for n, _ in RESHAKE])
print("I2V11:", [n for n, _ in I2V_JOBS])
print("LINT:", "PASS zero-negatives" if not fails else ("FAIL %s" % fails))
print("FRAME-MAP:", "ALL PRESENT" if not missing else ("MISSING %s" % missing))
print("VERDICT:", "GO" if (not fails and not missing) else "NO-GO")
