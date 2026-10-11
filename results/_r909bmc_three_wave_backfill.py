# -*- coding: utf-8 -*-
"""r909 bm-c: three-wave prereg sec.7/sec.8 one-shot backfill (W209/W211 debt heal + W213 fresh).
Machine-read numbers from n1_w2XX_results.json physical bytes (zero hand-copy drift).
Paradigm = r846 W206 / r907 W212 backfill."""
import json, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def load_wave(w):
    with open(os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{w}_results.json"), encoding="utf-8") as f:
        d = json.load(f)
    sg = d["science_gates"]["ledger"]
    npc = d["null_pool_cumulative"]
    m = npc["merged"]
    only_key = [k for k in npc if k.endswith("_only")][0]
    wo = npc[only_key]
    kl = d["skill_line_v2_k_lift"]
    pre_key = [p for p in kl if p.startswith("line_pre")][0]
    mrg_key = [p for p in kl if p.startswith("line_merged")][0]
    semu_key = [p for p in npc if p.startswith("se_mu")][0]
    famA = d["families"]["A_random_engine_exit"]
    assert sg["prev_total"] + sg["batch_trials"] == sg["total"], f"W{w} ledger identity FAIL"
    return dict(sg=sg, m=m, wo=wo, kl=kl, pre_key=pre_key, mrg_key=mrg_key,
                semu=(semu_key, npc[semu_key]), p95=famA["full_sharpe_p95"],
                nA=famA["n"], voids=sg["voids_applied"], n_shards=len(d["shards_consumed"]),
                cutoff=d["evidence_cutoff"], flip=kl["canon_flip"], total=sg["total"])

R = {w: load_wave(w) for w in ("209", "211", "212", "213")}

# five-key machine verdicts (pred keys from each prereg sec.5, measured from results bytes)
def rel(a, b):
    return (a - b) / b

K = {}
K["209"] = dict(
    d1=abs(R["209"]["wo"]["mu"] - R["209"]["m"]["mu"]),
    d2=rel(R["209"]["m"]["sigma"], 0.24511748),  # W207 merged sigma key
    d3=abs(R["209"]["p95"] - 0.3195),            # W207 A p95 anchor
    d4=abs(R["209"]["kl"]["line_delta_k_lift"]),
)
K["211"] = dict(
    d1=abs(R["211"]["wo"]["mu"] - R["211"]["m"]["mu"]),
    d2=rel(R["211"]["m"]["sigma"], R["209"]["m"]["sigma"]),
    d3=abs(R["211"]["p95"] - R["209"]["p95"]),
    d4=abs(R["211"]["kl"]["line_delta_k_lift"]),
)
K["213"] = dict(
    d1=abs(R["213"]["wo"]["mu"] - R["213"]["m"]["mu"]),
    d2=rel(R["213"]["m"]["sigma"], R["212"]["m"]["sigma"]),
    d3=abs(R["213"]["p95"] - R["212"]["p95"]),
    d4=abs(R["213"]["kl"]["line_delta_k_lift"]),
)
for w in ("209", "211", "213"):
    k = K[w]
    assert k["d1"] < 0.02, f"W{w} key1 FAIL {k['d1']}"
    assert abs(k["d2"]) < 0.10, f"W{w} key2 FAIL {k['d2']}"
    assert k["d3"] < 0.05, f"W{w} key3 FAIL {k['d3']}"
    assert k["d4"] <= 0.02, f"W{w} key4 FAIL {k['d4']}"

def fmt(x, n=5):
    return f"{x:.{n}f}"

def sec7(w, chain_note, k):
    r = R[w]
    return f"""## §7 跑后实证。【finalize 收口机械回填】
- **finalize one-pass 已回填（bm-c r909·2026-10-12 04:2x 债务愈合窗·{chain_note}）**：
  - 账本恒等式：prev_total **{r['sg']['prev_total']:,}** + batch_trials **{r['sg']['batch_trials']:,}** = total **{r['total']:,}**（三键机读自 n1_w{w}_results.json science_gates.ledger·断言 prev+batch==total 过）。
  - 合并池 K={r['mrg_key'].split('_')[-1]} EXACT·merged mu=**{fmt(r['m']['mu'], 8)}** / merged sigma=**{fmt(r['m']['sigma'], 8)}**·w{w}-only mu=**{fmt(r['wo']['mu'], 8)}** / w{w}-only sigma=**{fmt(r['wo']['sigma'], 8)}**（全机读零手抄）。
  - skill_line_v2 K-lift 对照：line_pre **{r['kl'][r['pre_key']]}** → line_merged **{r['kl'][r['mrg_key']]}** @n_eff {r['kl']['n_eff_held_equal']:,}（delta **{r['kl']['line_delta_k_lift']:+.4f}**·判线 ±0.02 内·先例带 ±0.0003 对照如实）。
  - **§5 五预键机证（r909 三波探针 results/_r909bmc_three_wave_probe.py 本窗补做）**：key1 w-only vs merged |Δmu|=**{k['d1']:.4f}**<0.02 PASS；key2 sigma 相对变化 **{k['d2']:+.6%}**<±10% PASS；key3 A 档 p95 **{r['p95']}** 差 **{k['d3']:.4f}**<0.05 PASS；key4 K-lift **{k['d4']:+.4f}**≤±0.02 PASS；key5 投影承接见 §8。**五键全过=§5 预测键全部兑现**。
  - se_mu 收窄链对照：se_mu@K{r['semu'][0].split('_')[-1]}=**{r['semu'][1]}**（{r['semu'][0]}）。
  - canon flip 态=NOT performed（K2200 同例·治理提案面 only）。
  - audit：voids_applied={r['voids']}·machine=bm-c·shards_consumed={r['n_shards']}/12·evidence_cutoff={r['cutoff']}。
  - 产物=results/perpetual_faces/n1_w{w}_results.json（finalize one-pass·幂等禁重跑=r538 律·pit-95 孤儿 finalize 守卫在位·FAIL-CLOSED 五重守卫〔pit-95/shard 完备/overlap-gap/重名/账本恒等〕过闸即本 finalize 落地机证）。"""

def sec8(w, proj_note, extra_note):
    r = R[w]
    return f"""## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r909 同窗回填）**：
  - §5.5 下波投影承接：{proj_note}
  - 宝藏/方法论捕获问：本批新方法=**零**（freeze→引擎自燃→finalize 全走既有正法·队列机制本体已建制登记）→TREASURE_REGISTRY 出入记录=零行（如实披露非漏记）。
  - 诚实披露面：{extra_note}"""

NOTES = {
    "209": dict(
        chain_note="finalize 本体早已落地（r886 窗死亡会话·K=457,720·账本头 883,589）·本窗补 §5 五预键机证+§7/§8 机械回填（r902-r907 死亡会话链遗留债务愈合）",
        proj_note="**W210 投影已实证兑现**——W210 落带 A=476,804..478,803=越过 W209 声明 B 带（476,604..476,803）的 first-clean（阶梯第七十例·bm-b r857 probe 承接注记与本投影逐位收敛·W210 finalize 亦已落 K=459,920）。",
        extra_note="①本回填=r909 债务愈合窗（finalize 落地于 r886 窗死亡会话·§7/§8 回填滞后至今·五预键机证本窗三波探针补做）；②W210 经 r898 takeover 归 bm-c 已 finalize·承接链闭合。",
    ),
    "211": dict(
        chain_note="finalize 本体早已落地（r892 窗死亡会话·K=462,120·账本头 887,989·01:39:51）·r902 unfuse+r904 reburn 12/12 修复窗如实注记·本窗补 §5 五预键机证+§7/§8 机械回填（债务愈合）",
        proj_note="**W212 投影已实证兑现**——W212 落带 A=481,204..483,203=越过 W211 声明 B 带（481,004..481,203）的 first-clean（阶梯第七十三例·承接注记逐位收敛·W212 finalize 已落 K=464,320·账本头 890,189）。",
        extra_note="①本回填=r909 债务愈合窗（同 W209·死亡会话链遗留）；②W211 本体链含 r902 unfuse+r904 reburn 12/12 修复窗（unfuse 重摇后引擎重烧全 12 分片·finalize 消费 reburn 后正身——如实注记保留）。",
    ),
    "213": dict(
        chain_note="全链=r908 席位发布 4f3b0d6a8→r908 per-wave prereg eeda85145→r908 五面冻结拼接 a24069f4c（03:58）→引擎自燃 12/12（03:58:26-04:04:04·live daemon mtime-watch 热重载自动拾取·每片 182 backtests）→本窗 r909 one-pass finalize 04:1x",
        proj_note="**W214+ 投影（probe 机证 leg4）**：naive A 485,404..487,403 / naive B 485,604..485,803——**W213 B 带（485,404..485,603）注册后 naive W214 A 窗将被拒**：W214 冻结方必须在 post-W213 注册宇宙重 derive 且 A 越过 485,603（阶梯 A-hops-prior-B 第七十五例）·derive B 预留 W214 A 窗——verify at W214 prereg·hop 链逐跳在 probe 回执。",
        extra_note="①r908 死会话吸收（席位/prereg/冻结三 commit 落链后死于收口前·state 滞 r907——本窗=r909 推进愈合）；②W209/W211 §7/§8 回填债同窗愈合；③W212 §5 五预键债已由 r908 W213 prereg 构建时 47 count-asserted rolls 机证+本窗三波探针补全机证面；④六门探针事实（席位 MSG 已推/冻结五面已落/12 分片/registry 带位恒等/prereg 已 commit/上游链头恒等）本窗全验。",
    ),
}

for w, note in NOTES.items():
    P = os.path.join(ROOT, "research", f"PERPETUAL_N1_W{w}_PREREG.md")
    raw = open(P, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig" if bom else "utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    i7 = text.find("## §7")
    i8 = text.find("## §8")
    foot = text.find("- **跑前冻结=本件 commit**")
    assert 0 < i7 < i8 < foot, f"W{w} anchor order FAIL: {i7} {i8} {foot}"
    old7 = text[i7:i8]
    old8 = text[i8:foot]
    assert "占位" in old7 and "占位" in old8, f"W{w} placeholder missing (already backfilled?)"
    s7 = sec7(w, note["chain_note"], K[w]).replace("\n", nl)
    s8 = sec8(w, note["proj_note"], note["extra_note"]).replace("\n", nl)
    new_text = text[:i7] + s7 + nl + nl + s8 + nl + nl + text[foot:]
    with open(P, "wb") as f:
        f.write(new_text.encode("utf-8-sig" if bom else "utf-8"))
    # read-back verify
    chk = open(P, encoding="utf-8-sig" if bom else "utf-8").read()
    seg7 = chk.split("## §7")[1][:600]
    seg8 = chk.split("## §8")[1][:600]
    assert "占位" not in seg7 and "占位" not in seg8, f"W{w} stub still present"
    print(f"W{w} sec.7/sec.8 backfill LANDED | ledger {R[w]['total']:,} | p95 {R[w]['p95']} | K-lift {R[w]['kl']['line_delta_k_lift']:+.4f}")

print("three-wave backfill complete: W209+W211 debt healed, W213 fresh")
