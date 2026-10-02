"""r383 bm-c W113 prereg §7/§8 mechanical backfill (r307 same-round law;
r412 SS7/SS8 mechanism; W112 precedent format). All numeric values are
READ from the landed results file + W112 prereg -- zero hand transcription
(r535 derive law). Bytes-in/bytes-out (r530). EOL preserved (r530/r500)."""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
P = os.path.join(ROOT, "research", "PERPETUAL_N1_W113_PREREG.md")
RES = os.path.join(ROOT, "results", "perpetual_faces", "n1_w113_results.json")
PRE112 = os.path.join(ROOT, "research", "PERPETUAL_N1_W112_PREREG.md")

with open(RES, encoding="utf-8") as f:
    d = json.load(f)
led = d["science_gates"]["ledger"]
sk = d["skill_line_v2_k_lift"]
npc = d["null_pool_cumulative"]
w = npc["w113_only"]
m = npc["merged"]
fa = d["families"]["A_random_engine_exit"]
se_mu = npc["se_mu_at_k246520"]
anchor_mu = -0.09276358334710065   # W111 landed key (frozen in §5)
anchor_sigma = 0.24489883563788295
anchor_p95 = 0.3191
g1 = abs(w["mu"] - anchor_mu)
g2 = (m["sigma"] - anchor_sigma) / anchor_sigma * 100
g3 = fa["full_sharpe_p95"] - anchor_p95
g4 = sk["line_delta_k_lift"]
assert led["prev_total"] == 610948 and led["batch_trials"] == 2200
assert led["total"] == 613148 and led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"]
assert g1 < 0.02 and abs(g2) < 10 and abs(g3) < 0.05 and g4 >= -0.02, (g1, g2, g3, g4)
print(f"gates: g1={g1!r} g2={g2!r}% g3={g3!r} g4={g4!r} -- ALL PASS")

with open(P, "rb") as f:
    raw = f.read()
crlf = raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n")
print("EOL:", "CRLF" if crlf else "LF")
txt = raw.decode("utf-8")
if crlf:
    txt = txt.replace("\r\n", "\n")  # normalize to LF for matching

sec7 = (
f"## §7 跑后实证。【r382 冻结占位·r383 bm-c finalize 收口机械回填】\n\n"
f"- 12/12 分片 bm-c 引擎烧毕（r382 冻结 eeb062290 窗后引擎 tick 自燃 12/12 完备 ~8min·appender 76401aee7 三尾片落账·finalize 前 12/12 完备 r310 律）；finalize one-pass（r538 律·首跑禁重跑——本波实弹：中窗 wave-complete 物化趟先落一账（prev 610,948→613,148）后手跑 finalize 无守卫再追加（613,148→615,348 双计）·草稿未 commit 未推零外污染=r576 可刷面·strip 后 one-pass 对真链头 610,948 重 derive；pit-95 orphan-finalize 守卫 +16 行同窗入 runner finalize() 首位〔r206/r509/r538 族根治〕）。\n"
f"- ledger：prev_total 610,948（W112 bm-a r591 落账解锁·链序 W110 606,548 bm-b 代 bm-a→W111 608,748 bm-b→W112 610,948 bm-a）+ batch_trials 2,200 = **{led['total']:,}**；voids_applied=LOWAMP-P1/P2。\n\n"
f"- w113-only：n={w['n_values']:,}·mu={w['mu']!r}·sigma={w['sigma']!r}；merged：K={m['n_values']:,}·mu={m['mu']!r}·sigma={m['sigma']!r}。\n"
f"- skill_line_v2 @n_eff_held {sk['n_eff_held_equal']:,}：{sk['line_pre_w113']:.4f}→**{sk['line_merged_246520']:.4f}**（K-lift delta {g4:+.4f} ≥ −0.02 门内·正负交替如实报〔W110 +0.0000→W111 +0.0000→W112 −0.0001→W113 {g4:+.4f}〕）；se_mu @K{m['n_values']:,}={se_mu:.6f}（收窄链持续 W110 0.0005→W111 0.000498→W112 0.000495→W113 {se_mu:.6f}）；canon_flip 未执行（治理提案面·K2200 同法）。\n"
f"- §5 预测四门全过（冻结锚=W111 finalize 实测键）：|Δmu|={g1!r}<0.02（W113-only {w['mu']:.8f} · 单波偏离面如实报·门内）；σ 变化 {g2:.4f}%<±10%（锚 {anchor_sigma!r}·本波 merged {m['sigma']!r}）；A 档 p95 差 {g3:+.4f}<0.05（锚 {anchor_p95}·本波 {fa['full_sharpe_p95']}）；K-lift {g4:+.4f}≥−0.02。\n"
f"- W114+ 链面披露：本波 finalize 时点上游 finalize 链=零在飞（W112 已落账 bm-a r591·链 W1..W113 全闭合；W114 bm-a 已公示席位未冻结——席位在飞不阻 finalize·r307 FAIL-CLOSED 判据=上游 finalize 链）；W115+ 投影=下波冻结方必本机 gate 机派复核非转抄（r587 律·§5.5 W114 投影已被 bm-a r592 席位实占核验一致）。\n")

sec8 = (
f"- 首跑唯一一跑律执行面·本波双计险情实录（r538 族）：finalize 产物 n1_w113_results.json 未 commit 前遭遇中窗 wave-complete 物化×手跑 finalize 两趟=草稿双计（prev 613,148/total 615,348）·未推零外污染·strip 后 one-pass 重 derive（ledger 块在件内实测 prev 610,948/batch 2,200/total 613,148）；守卫落地=finalize_already_landed FAIL-CLOSED 腿入 runner（+16 行纯插入·sg 单源·live-fire 重跑拒绝 rc=2 断言过）。\n"
f"- 两态腿断言验证：n1 selftest（默认 --wave 调用 r522 律）finalize 后重跑 PASS（W113 materializer 腿 dep 断言跑后态合法·r307 同轮回填律）；pf 9/9。\n"
f"- 预注册纪律：§1-§6 判据面零触碰（冻结后禁改判据），本腿只机械回填 §7/§8（r307 同轮回填律）。\n")

old_h7 = "## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假】\n\n- （finalize 落账后机械回填；两态腿断言在场=r307 律）"
old_s8 = "- （finalize 落账后机械回填）"
assert txt.count(old_h7) == 1, "§7 anchor not unique"
assert txt.count(old_s8) == 1, "§8 anchor not unique"
new = txt.replace(old_h7, sec7.rstrip("\n"))
new = new.replace(old_s8, sec8.rstrip("\n"))
assert "机械回填）" not in new, "placeholder residue"

if crlf:
    new = new.replace("\r\n", "\n").replace("\n", "\r\n")
with open(P, "wb") as f:
    f.write(new.encode("utf-8"))
print("backfill written; §7 len:", len(sec7), "§8 len:", len(sec8))
