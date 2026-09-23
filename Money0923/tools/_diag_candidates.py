import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = json.load(open("state/state.json", encoding="utf-8"))
a = s.get("arena", {})
q = a.get("qualified") or []
fam: dict[str, list] = {}
for x in q:
    fam.setdefault(x.get("strategy"), []).append(x)
print(f"认证选手按族分布（共{len(q)}人）:")
for k, v in sorted(fam.items(), key=lambda kv: -len(kv[1])):
    best = v[-1]
    print(f"  {k}: {len(v)}人  最近认证={best.get('id')} 连胜{best.get('streak')}局")
ps = a.get("pstats") or {}
rows = []
for k, v in ps.items():
    if (v.get("n") or 0) >= 20:
        rows.append((k, v.get("n"), round(v.get("avg_ps") or 0, 3),
                     round(v.get("avg_ret") or 0, 4), round(v.get("avg_dd") or 0, 4),
                     round(v.get("halt_ok") or 0, 3)))
rows.sort(key=lambda r: -r[2])
print("实战样本>=20局的选手盈稳分Top12:")
for r in rows[:12]:
    print(f"  {r[0]} n={r[1]} 盈稳分={r[2]} 均收益={r[3]*100:+.2f}%/局 均回撤={r[4]*100:.1f}% halt_ok={r[5]}")
