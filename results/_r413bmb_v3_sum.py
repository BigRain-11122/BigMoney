import json
v = json.load(open("results/decision_chain_v3_tournament.json", encoding="utf-8"))
verd = v.get("verdict", {})
def s(x): return json.dumps(x, ensure_ascii=False)
print("j_target:", s(verd.get("j_target"))[:200])
print("winners:", s(verd.get("winners"))[:200])
print("verdict_core:", s(verd.get("verdict"))[:300] if "verdict" in verd else "n/a")
faces = verd.get("j_c_faces", {})
for face, arms in faces.items():
    wins = {a: arms[a].get("chain_win") for a in arms}
    print(f"face={face} chain_win={wins}")
print("audit:", s(v.get("audit", {}).get("verdict", v.get("audit")))[:200])
print("n_arms_faces keys:", list(verd.keys()))
print("executed_by:", s(v.get("executed_by"))[:100])
print("finalize_runtime_sec:", v.get("finalize_runtime_sec"))
print("prereg_sha256:", str(v.get("prereg_sha256"))[:20])
