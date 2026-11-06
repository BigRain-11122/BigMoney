"""r1388 witness: does a writer that never mentions the GPU heal a disagreeing face?

The claim being tested is not "the new code has legs" (it does, L15/L16) but that the
defect was REAL in the code that was committed: HEAD's chokepoint keyed on a leading
`gpu` prefix, so a face holding `vram_free_gb` beside `gpu_free_mib` kept two different
free-memory numbers under one stamp, and a caller without a GPU key could never repair it
(merge-only). Both versions are run here against the same fixture face, loaded from disk
by path, so the comparison is HEAD-blob vs working-tree, not a re-reading of the diff.
"""
import importlib.util
import io
import json
import os
import sys
import tempfile

ROOT = os.getcwd()
sys.path.insert(0, ROOT)
HEAD_BLOB = os.path.join(tempfile.gettempdir(), "hb_head.py")

import Tools.gpu_face as gf

real_probe = gf.probe_live


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, tag, caller):
    root = os.path.join(tempfile.mkdtemp(prefix="w1388_"), tag)
    hp = mod._fixture(root, ["O-x.md"])
    face = json.load(io.open(hp, encoding="utf-8"))
    face.update({"vram_free_gb": 13.74, "gpu_free_mib": 15259,
                 "gpu_used_mib": 1125, "gpu_mem_total_mib": 16384})
    json.dump(face, io.open(hp, "w", encoding="utf-8"), ensure_ascii=False)
    mod._gpu_face_mod = lambda: gf
    gf.probe_live = lambda smi=None: {"util_pct": 0.0, "used_mib": 1125,
                                      "total_mib": 16384}
    try:
        v, rc = mod.write(root, dict(caller))
    finally:
        gf.probe_live = real_probe
    after = json.load(io.open(hp, encoding="utf-8"))
    return {"rc": rc, "audit": gf.audit(after),
            "vram_free_gb": after.get("vram_free_gb"),
            "gpu_free_mib": after.get("gpu_free_mib"),
            "applied": sorted(k for k in (v.get("applied") or []) if "gpu" in k or "vram" in k)}


head = load(HEAD_BLOB, "hb_head")
now = load(os.path.join(ROOT, "Tools", "heartbeat_write.py"), "hb_now")

out = {
    "tool": "_r1388bmc_gpu_alias_witness",
    "machine": "bm-c",
    "question": "a writer with no GPU key on a face holding vram_free_gb=13.74 beside gpu_free_mib=15259",
    "head_blob": run(head, "head", {"did": "witness"}),
    "working_tree": run(now, "now", {"did": "witness"}),
}
out["verdict"] = ("HEAD leaves the disagreement (audit non-empty, 13.74 kept); "
                  "the working tree restates both spellings from one probe")
print(json.dumps(out, ensure_ascii=False, indent=1))
with io.open(os.path.join(ROOT, "results", "_r1388bmc_gpu_alias_witness.json"),
             "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)