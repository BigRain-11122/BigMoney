# -*- coding: utf-8 -*-
"""r1088 bm-c surgical post-splice heal: live n1 W267 block stale _set_wave(265) -> _set_wave(267).

Defect (r1076-family setwave-stale face, 4th recurrence, CEO defect-birthplace law
2026-10-16): the W267 splice carried the 2-stale canon hdr face _set_wave(265)
into the live n1 W267 block; post-splice selftest red: "W267 A hits W265".

Root cure at birth station (this window): derive editor p3_setwave_rootcure
rep + phase5 presence gates (_set_wave(267):1 / _set_wave(265):0); healed canon
regenerated (62156B, exactly 1-line delta L561, phase4 70-face zero-residual
PASS, phase5 PASS, py_compile OK).

This script heals the ALREADY-SPLICED live n1 only. The splice itself cannot be
re-run (pf anchor w265_own_line+close consumed; freeze-edits re-execution would
fail-closed at must()). Byte-level, occurrence-map-asserted, fail-closed.

Measured live this window (r1077 measured-counts law):
  _set_wave(265): lines 73397 (W265 block opener, LEGIT, preserve) + 74709 (W267 block, STALE)
  _set_wave(266): line 74051 (W266 block, LEGIT, preserve)
  _set_wave(267): 0 occurrences pre-heal
"""
import codecs, datetime, hashlib, json, os, py_compile, tempfile

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
N1 = ROOT + r"\scripts\perpetual_faces_n1.py"
PF = ROOT + r"\scripts\perpetual_faces.py"
RECEIPT = ROOT + r"\results\_w267bmc_freeze_receipt.json"

PRE_SHA16 = "e1426cbabbe12140"          # post-splice pre-heal n1 (defect present)
W265_OPEN_LINE, W266_SETWAVE_LINE, STALE_LINE = 73397, 74051, 74709   # 1-based, live-measured

def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]

assert sha16(N1) == PRE_SHA16, "pre-heal n1 sha16 mismatch: %s" % sha16(N1)

raw = open(N1, "rb").read()
lines = raw.split(b"\n")
occ = [i + 1 for i, l in enumerate(lines) if b"_set_wave(265)" in l]
assert occ == [W265_OPEN_LINE, STALE_LINE], "occurrence map drift: %s" % occ
assert STALE_LINE > W266_SETWAVE_LINE > W265_OPEN_LINE      # region sanity: W267 block below W266
occ266 = [i + 1 for i, l in enumerate(lines) if b"_set_wave(266)" in l]
assert occ266 == [W266_SETWAVE_LINE], "W266 setwave map drift: %s" % occ266
assert not [l for l in lines if b"_set_wave(267)" in l], "pre-heal _set_wave(267) already present"

i = STALE_LINE - 1
assert lines[i].strip() == b"_set_wave(265)", "stale line body drift: %r" % lines[i]
lines[i] = lines[i].replace(b"_set_wave(265)", b"_set_wave(267)", 1)
new_raw = b"\n".join(lines)

assert new_raw.count(b"_set_wave(265)") == 1     # only W265 block opener remains
assert new_raw.count(b"_set_wave(266)") == 1     # W266 block face untouched
assert new_raw.count(b"_set_wave(267)") == 1     # the healed W267 block face
assert len(new_raw) == len(raw)                  # same-length replacement

open(N1, "wb").write(new_raw)
py_compile.compile(N1, cfile=os.path.join(tempfile.gettempdir(), "n1_heal_check.pyc"), doraise=True)
post = sha16(N1)
assert post != PRE_SHA16
print("N1 HEALED: line %d _set_wave(265)->_set_wave(267); sha16 %s -> %s" % (STALE_LINE, PRE_SHA16, post))

# ---- receipt update: n1_sha16_post + post_splice_heals disclosure ----
rec_raw = open(RECEIPT, "rb").read()
bom = rec_raw.startswith(codecs.BOM_UTF8)
rec = json.loads(rec_raw.decode("utf-8-sig"))
assert rec["n1_sha16_post"] == PRE_SHA16, "receipt n1_sha16_post not at pre-heal value"
assert rec["pf_sha16_post"] == sha16(PF), "live pf drifted from receipt pf_sha16_post"
rec["n1_sha16_post"] = post
rec["post_splice_heals"] = {
    "setwave_rootcure": {
        "defect": "spliced n1 W267 block carried the 2-stale canon hdr face _set_wave(265) (post-splice selftest red: 'W267 A hits W265'); r1076-family 4th recurrence",
        "law": "CEO defect-birthplace law 2026-10-16: fix at earliest station + gate the birth station, disclose the heal",
        "birth_station_gate": "derive editor p3_setwave_rootcure rep('_set_wave(265)'->'_set_wave(267)', 1) + phase5 presence gates (_set_wave(267):1 / _set_wave(265):0); healed canon regenerated this window (62156B, exactly 1-line delta L561, phase4 70-face zero-residual PASS, py_compile OK)",
        "surgical_heal": "live n1 line 74709 only (W267 block region; W265 block opener line 73397 and W266 block face line 74051 preserved; occurrence map [73397, 74709] asserted pre-heal; splice NOT re-run -- pf anchor w265_own_line+close consumed, re-execution fail-closed)",
        "same_window_heals_context": "2 prereg-side heals already disclosed this window (receipt wave field 265->266 stale-since-W265-TOL-canon; authored stamp 09:0x->10:5x per prereg derive mtime 10:58:26)",
        "evidence": "results/_r1088bmc_n1_setwave_heal.py + derive editor log results/_r1088bmc_derive_editor_log.txt + selftest re-run PASS (this window)",
        "healed_at": datetime.datetime.now().isoformat(timespec="minutes"),
        "n1_sha16_preheal": PRE_SHA16,
        "n1_sha16_healed": post
    }
}
out = json.dumps(rec, indent=1, ensure_ascii=True)
if rec_raw.endswith(b"\n"):
    out += "\n"
data = out.encode("utf-8")
if bom:
    data = codecs.BOM_UTF8 + data
open(RECEIPT, "wb").write(data)
print("RECEIPT UPDATED: n1_sha16_post=%s + post_splice_heals" % post)
print("HEAL OK")
