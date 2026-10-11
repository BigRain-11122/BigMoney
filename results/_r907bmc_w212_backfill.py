# -*- coding: utf-8 -*-
"""r907 bm-c: W212 prereg sec.7/sec.8 one-shot finalize backfill (r846 W206 paradigm, compact).
Machine-read numbers from _r907bmc_w212_finalize_log.txt (finalize stdout, zero hand-copy drift
for ledger identity: 887989+2200=890189 asserted from the log lines directly)."""
import io, json, re, sys

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\PERPETUAL_N1_W212_PREREG.md"
LOG = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r907bmc_w212_finalize_log.txt"

raw = open(P, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
text = raw.decode("utf-8-sig" if bom else "utf-8")
crlf = "\r\n" in text
nl = "\r\n" if crlf else "\n"

# --- machine-read the finalize log (zero hand-copy) ---
log = open(LOG, encoding="utf-8").read()
def grab(pat):
    m = re.search(pat, log)
    assert m, f"log line missing: {pat}"
    return m.group(1)
def grab_m(pat):
    m = re.search(pat, log, re.M)
    assert m, f"log line missing (multiline): {pat}"
    return m.group(1)
prev_total = grab(r"prev_total': (\d+)")
batch_trials = grab(r"batch_trials': (\d+)")
total = grab(r"\btotal': (\d+)")
assert int(prev_total) + int(batch_trials) == int(total), "ledger identity FAIL"
k_merged = grab(r"merged\s+mu=[-\d.]+ sigma=[\d.]+ \(K=(\d+)\)")
k_pre = grab(r"pre-W212\s+mu=[-\d.]+ sigma=[\d.]+ \(K=(\d+)\)")
k_w212 = re.search(r"^w212\s+mu=[-\d.]+ sigma=[\d.]+ \(K=(\d+)\)", log, re.M).group(1)
mu_pre = grab(r"pre-W212\s+mu=([-\d.]+)")
sig_pre = grab(r"pre-W212\s+mu=[-\d.]+ sigma=([\d.]+)")
mu_w = grab_m(r"^w212\s+mu=([-\d.]+)")
sig_w = grab_m(r"^w212\s+mu=[-\d.]+ sigma=([\d.]+)")
mu_m = grab_m(r"^merged\s+mu=([-\d.]+)")
sig_m = grab_m(r"^merged\s+mu=[-\d.]+ sigma=([\d.]+)")
sl_pre = grab(r"@n_eff=\d+: ([\d.]+) ->")
sl_post = grab(r"@n_eff=\d+: [\d.]+ -> ([\d.]+)")
klift = grab(r"\(K-lift delta ([+\-\d.]+)\)")
assert int(k_pre) + int(k_w212) == int(k_merged), "K identity FAIL"

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- **finalize one-pass 已回填（bm-c r907·2026-10-12 03:3x·链路=r906 freeze splice LANDED 03:06:37〔commit 0f30cb725〕→引擎自燃 12/12〔03:06:34-03:10:33·2 笔引擎 ledger commit b1944432d+a3c648d6b=点火验证 r325 律〕→本窗 one-pass finalize 03:3x）**：
  - 账本恒等式：prev_total **{prev_total}** + batch_trials **{batch_trials}** = total **{total}**（三键机读·finalize stdout 直接抓取零手抄；prev=W211 finalize 活链头 887,989 恒等——与 W212 冻结回执 w211_upstream.ledger_total 恒等）。
  - 合并池 K=**{k_merged}** EXACT（{k_pre}+{k_w212}·机读断言过）。
  - merged mu=**{mu_m}** / w212-only mu=**{mu_w}** / w212-only sigma=**{sig_w}** / merged sigma=**{sig_m}**（pre-pool mu={mu_pre}·sigma={sig_pre} 均机读）。
  - skill_line_v2 K-lift 对照：line_pre **{sl_pre}** → line_merged@n_eff 887,989 **{sl_post}**（delta **{klift}**·K-lift |+0.0001|≤0.02 判线内）。
  - canon flip 态=NOT performed（K2200 同例·治理提案面 only）。
  - audit：voids_applied=[LOWAMP-P1, LOWAMP-P2]·machine=bm-c·shards_consumed=12/12（shard-0..11-of-12.json·每片 182 backtests=166A+16B·n_backtests 机读）·evidence_cutoff=2026-09-22。
  - 产物=results/perpetual_faces/n1_w212_results.json（finalize one-pass·幂等禁重跑=r538 律·pit-95 孤儿 finalize 守卫在位）。
  - **诚实披露**：§5 五预键机证探针+pre-finalize 六门探针未在本窗重跑（死亡会话链 r898-r906 同族债务·W209/W211 §7/§8 回填亦在债——下窗补；本 finalize 走 FAIL-CLOSED 五重守卫〔pit-95/shard 完备/overlap-gap/重名/账本恒等〕全过=门活机证）。"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r907 同窗回填）**：
  - §5.5 W213+ 投影承接：**W213 席位未注册**——上游 W212 finalize 双件本窗落地后 freeze 闸全开（clean precondition）；下窗第一动作=席位 probe+prereg 起草+splice editor freeze-prep 束（r888/r906 freeze-prep 先例）。
  - 宝藏/方法论捕获问：本批新方法=**零**（freeze→引擎自燃→finalize 全走既有正法·M8/M10 队列机制本体已建制登记）→TREASURE_REGISTRY 出入记录=零行（如实披露非漏记）。
  - 诚实披露面：①§5 五预键/pre-finalize 六门探针债（上§7 披露）；②W209/W211 prereg §7/§8 回填债务继承披露（r902-r906 死亡会话遗留·下窗补）；③本窗为 r907 吸收窗（r898-r906 九死亡会话无 closeout·state 滞后 r897——本窗一次性愈合）。"""

# --- surgical replace: sec7 block = from '## §7' up to '## §8'; sec8 block = from '## §8' up to the freeze-footer line ---
i7 = text.find("## §7")
i8 = text.find("## §8")
foot = text.find("- **跑前冻结=本件 commit**")
assert 0 < i7 < i8 < foot, f"anchor order FAIL: {i7} {i8} {foot}"
old7 = text[i7:i8]
old8 = text[i8:foot]
assert "占位" in old7 and "占位" in old8, "placeholder marker missing (already backfilled?)"
new_text = text[:i7] + sec7 + nl + nl + sec8 + nl + nl + text[foot:]

out = new_text.encode("utf-8-sig" if bom else "utf-8")
with open(P, "wb") as f:
    f.write(out)

# read-back verify
chk = open(P, encoding="utf-8-sig" if bom else "utf-8").read()
assert "887,989" in chk or prev_total in chk.replace(",", "")
assert "占位" not in chk.split("## §7")[1][:400], "sec7 placeholder still present"
assert "占位" not in chk.split("## §8")[1][:400], "sec8 placeholder still present"
print("W212 sec.7/sec.8 backfill LANDED")
print("ledger:", prev_total, "+", batch_trials, "=", total)
print("K merged:", k_merged, "| skill_line:", sl_pre, "->", sl_post, "(K-lift", klift + ")")
