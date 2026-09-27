# r348 bm-b rebase-stop resolver: results/autofill_state.json (mixed-dict+ledger,
# classifier GREEN 1/1, law r203/R208/r215/r220). Blobs frozen pre-add (r96 law).
# Facts: HEAD(:2:)=bm-c tick 23:50:02 launches47 (upstream, fresher last_tick);
# MINE(:3:)=bm-b tick 23:20:01 launches47 (replayed pick 9438dd99);
# BASE(:1:)=bm-c tick 23:20:02 launches47. Union verdict below; format mirror
# upstream HEAD bytes (LF/indent1, r337 mirror law) -- take-HEAD whole-bytes if
# keyset identity holds (r339 take-ours-whole precedent).
import json
import subprocess
import io


def blob(stage):
    r = subprocess.run(["git", "show", f":{stage}:results/autofill_state.json"],
                       capture_output=True)
    assert r.returncode == 0 and r.stdout, f"blob :{stage}: empty/err"
    return r.stdout


base_b, head_b, mine_b = blob(1), blob(2), blob(3)
bd, hd, md = (json.loads(x) for x in (base_b, head_b, mine_b))


def lkey(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)


hl, ml = hd.get("launches", []), md.get("launches", [])
union = {lkey(e): e for e in hl}
for e in ml:
    union.setdefault(lkey(e), e)
print("launches: head", len(hl), "mine", len(ml), "union", len(union),
      "identical_sets", set(map(lkey, hl)) == set(map(lkey, ml)))

hts, mts = hd["last_tick"]["ts"], md["last_tick"]["ts"]
print("last_tick ts: HEAD", hts, "| MINE", mts, "-> take",
      "HEAD" if hts >= mts else "MINE")
assert isinstance(hd["last_tick"], dict) and isinstance(md["last_tick"], dict)

# Resolution: union==HEAD set AND HEAD last_tick strictly newer -> result bytes
# == HEAD bytes verbatim (zero churn, zero loss: |A u B| == 47 == both sides).
assert set(map(lkey, hl)) == set(map(lkey, ml)), "launches diverge: manual adjudication needed"
assert hts > mts, "last_tick not fresher: manual adjudication needed"
with io.open("results/autofill_state.json", "wb") as f:
    f.write(head_b)
back = json.load(io.open("results/autofill_state.json", encoding="utf-8"))
assert isinstance(back["last_tick"], dict)
assert back["last_tick"]["ts"] == hts and len(back["launches"]) == len(union)
print("RESOLVED take-HEAD whole-bytes: last_tick", hts,
      "launches", len(back["launches"]), "| parse-verify PASS (r185)")
