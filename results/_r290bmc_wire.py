import json, hashlib, re, os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TMP = os.environ["TEMP"]

# 1) sha of fresh decisions face (consumed this round via git show origin/main)
raw = open(os.path.join(TMP, "decisions_fresh.md"), "rb").read()
sha = hashlib.sha256(raw).hexdigest()

# 2) state surgical rewrite: detect indent + newline, add watermark key
p = os.path.join(REPO, "state-bm-c.json")
sp = open(p, "rb").read().decode("utf-8")
crlf = sp.count("\r\n")
lf = sp.count("\n") - crlf
ind = re.search(r"\n(\s+)\"machine_id\"", sp).group(1)
d = json.loads(sp)
d["last_decisions_sha"] = sha
d["last_decisions_read_at"] = "2026-09-30T22:35:00+08:00"
out = json.dumps(d, ensure_ascii=False, indent=len(ind))
if crlf > 0:
    out = out.replace("\n", "\r\n")
open(p, "w", encoding="utf-8", newline="").write(out)
print("sha=", sha[:16], "indent=", len(ind), "crlf=", crlf, "lf=", lf)

# 3) CODELY.md memory append (S4, four-question gate passed)
mem = os.path.join(REPO, "CODELY.md")
entry = (
    "- [2026-09-30 r290 bm-c] 集团决策面盲读坑+D-19 新鲜读律接线（149-commit 滞后实弹）：本机集团树 "
    "K:\\Fluxgroup\\FluxGroup 的 git checkout 常态落后 origin 百+ commit 且无任何同步机制（循环只 pull BigMoney 仓）"
    "——直读工作树 decisions.md=陈旧面，r290 实测漏读 D-20260930-05..41 共 37 条（含 RW-5 冻结令/投递层统一单 D-19/"
    "散户轨道重构令 D-41；此前全靠 BigMoney 仓内 MSG/正典旁路传播才未误事，非可靠机制）。根治=iteration_prompt.txt "
    "决策审核步已改（D-20260930-19 接线）：git -C 集团树 fetch + git show origin/main:docs/decisions.md 新鲜面消费"
    "+state 自持水位键 last_decisions_sha（SHA-256 内容寻址·D-18 禁行数比对）+派工通告板块+orders.md CEO 待办物理件区。"
    "How to apply：一切读集团台账/令件的场合一律 origin/main 面（git show 零树触碰），禁信本机集团树工作树副本；"
    "水位比对用内容 hash 禁行数。\n"
)
with open(mem, "a", encoding="utf-8", newline="") as f:
    f.write(entry)
print("memory appended, CODELY bytes:", os.path.getsize(mem))

# 4) HQ-FEEDBACK line (D-19 receipt + mechanism gap report)
fb = os.path.join(REPO, "HQ-FEEDBACK.md")
fentry = (
    "- F-20260930-02 [bm-c r290 2026-09-30 22:3x·D-20260930-19 回执+机制缺口呈报] ①回执：D-11+D-16+D-18 合并单"
    "司内接线已落地（Tools/iteration_prompt.txt 决策审核步改新鲜读律：git show origin/main 面+派工通告板消费+"
    "orders.md CEO 待办物理件区+state-bm-c.json 水位键 last_decisions_sha SHA-256 内容寻址；回执 commit 本窗）；"
    "D-13① SLA 自本窗起按通告板消费。②机制缺口呈报（非本司可自愈面）：bm-c 机集团树 checkout 无任何同步机制"
    "（r290 实测落后 origin 149 commit+本地 settings.json 平台搅动恒脏=pull--rebase 不可行）——建议集团层定谳"
    "「各司对集团台账只读消费一律走 git show origin/main」为正典（bm-c 已按此接线可作参照实现），或生态 sync 工具"
    "纳入集团树 fetch+show 供给面；不建议各司自行 pull/rebase 集团树（脏树+跨机并发=rebase 连环坑 r473/r486 族）。\n"
)
with open(fb, "a", encoding="utf-8", newline="") as f:
    f.write(fentry)
print("feedback appended, HQ-FEEDBACK bytes:", os.path.getsize(fb))
