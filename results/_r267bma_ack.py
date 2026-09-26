"""R267 bm-a addendum: O-20260926-2000-bm-c receipt (orders_ack append + round-report
addendum + CODELY.md execution-record line + state pointer refresh). Face-mirror law
R254/R255/R257 (probe BOM/EOL/indent/ensure_ascii/tailNL from current bytes).
"""
import json, subprocess, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
NOW = "2026-09-26 20:46"

# ---- heartbeat: orders_ack append (R251 law: full filename incl .md) ----------
hb_path = ROOT + r"\fleet\machines\bm-a.json"
hb = json.load(open(hb_path, encoding="utf-8"))
ack = hb["orders_ack"]
assert "O-20260926-2000-bm-c.md" not in ack, "already acked"
hb["orders_ack"] = ack + " O-20260926-2000-bm-c.md"
hb["task"] = ("R267 addendum: O-2000 base-unification acked (inventory snapshot delivered, migration executor "
              "armed+launched at round end); next = S0 verify migration state from new root C:\\Fluxgroup, assemble "
              "five receipts, 09-28 Mon new-bar chain, MF_IC_P1 on panel completion, 10-01 monthly trio")
hb["heartbeat_epoch_utc"] = int(__import__("time").time())
hb["clock_read"] = datetime.datetime.now().astimezone().isoformat()
b = json.dumps(hb, indent=1).encode()
assert not b.endswith(b"\n") and b"\r" not in b
open(hb_path, "wb").write(b)
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]
assert chk["orders_ack"].count("O-20260926-2000-bm-c.md") == 1
print("heartbeat acked, epoch:", chk["heartbeat_epoch_utc"])

# ---- state pointer refresh ---------------------------------------------------
st_path = ROOT + r"\state-bm-a.json"
st = json.load(open(st_path, encoding="utf-8"))
st["did"] = ("R267 maintenance round + O-2000 base-unification receipt: 15-UU rebase resolved (take-new x13 union x2, "
             "zero loss), ack inventory fleet/ack/O-20260926-2000-bm-a-inventory.md, migration executor armed+launched "
             "(detached, gate = this instance exit)")
st["current_task"] = "R267 closed (maintenance + O-2000 ack + migration executor launched)"
st["next"] = ("(1) S0 FIRST: verify migration state from new root C:\\Fluxgroup (journal tail + receipt marker + "
             "aborted.flag check) -> assemble five receipts per order (tree snapshot/task-list before-after/ignition/"
             "git-HEAD/root_path registration) + push; (2) 09-28 Monday new-bar chain (cutoff 09-24); (3) MF_IC_P1 when "
             "moneyflow panel completes; (4) 10-01 monthly trio + REGIME_GUARD v3 date gate; (5) R270 5x HANDOVER recon")
for k in ("ts", "last_round_ts", "updated_at", "last_run", "last_round_at", "updated"):
    st[k] = NOW
b = json.dumps(st, indent=1).encode()
assert not b.endswith(b"\n") and b"\r" not in b
open(st_path, "wb").write(b)
print("state refreshed")

# ---- round report addendum line ------------------------------------------------
rp_path = ROOT + r"\logs\iteration-loop\round_reports-bm-a.md"
raw = open(rp_path, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
line = (
    NOW + " | R267 addendum | (dept:工程/舰队) O-20260926-2000-bm-c 机队基地统一令（CEO 直令·bm-c 20:00 承令推送）"
    "rebase 后窗收令→同轮执行：push 撞 bm-b r271+bm-c 令 commit→15-UU 按技能分类器+配方解（分类 11+UNKNOWN 4 手工定性："
    "快照/scorecard 族 :3 本机 20:02-20:03 恒新=take-new 整面（deepdiff 实证 scorecard_v1 差=仅 /generated、"
    "strategy_scorecard 差=generated+elapsed_sec、REPORT 对 generated_at 定胜负 r242 律）；ledger 族 union："
    "compute_audit history 201|201→202 零丢失、regime_state 等值整面、autofill launches union 49+last_tick 本机 "
    "20:00:02 恒新（r245 cap-asc 律+isinstance 断言）；resolver results/_r267bma_resolve.py 全件解析过=15/15）"
    "→rebase 落 b8e9d070→收令即动：ack=现状盘点快照 fleet/ack/O-20260926-2000-bm-a-inventory.md（单卷 C: 无 K:→"
    "目标根 C:\\Fluxgroup；8 git 仓清单+63 任务清单+36 承载面 Action/WD 定义+九件对照+死任务 MoneyAutoGuardian "
    "目标缺席=disable-only+Unity Bee 三处必清）；迁移执行器 results/_r267bma_fluxgroup_migration.ps1（外置执行副本 "
    "C:\\Users\\sjs20\\fluxgroup-migration-bma.ps1·PSParser 0 错·fail-closed 门序：36 件重定义 XML 移动前预校验→"
    "全 disable→等在飞实例自然收 40min 门→8 仓零丢失自证（bigmoney 合法脏=autofill_state.json 按 R245 stash）→"
    "同卷改名瞬时→MiniGame 真身移产线区+gaming junction 回指单份律→九件骨架→Bee 清→重定义 3 重试→全 re-enable+"
    "点火留痕）于本轮末动作分离启动（O-1730 物理依赖票内留痕：迁移须停本执行体所在循环=执行器以本实例退出为门·"
    "detached 轮外执行·窗限 09-29 12:00 内）；回执五件组装=下轮 S0（自新路径起跑：journal+receipt 标记+root_path "
    "登记）｜证据=本 commit 全件+orders_ack 84/84 diff empty+journal 起始行｜下轮指针：S0 首查迁移态（C:\\Fluxgroup "
    "就位?aborted.flag?）→五件回执组装+推送→09-28 周一新 bar 链→MF_IC_P1→10-01 月首轮三件套"
)
with open(rp_path, "ab") as f:
    f.write(line.encode("utf-8") + eol)
print("round report addendum appended")

# ---- CODELY.md execution-record line ---------------------------------------------
cm_path = ROOT + r"\CODELY.md"
raw = open(cm_path, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
cline = (
    "- [" + NOW + "] O-20260926-2000-bm-c 机队基地统一令 bm-a 收令执行（CEO 直令·bm-c 承令·ack 15min 判据=盘点快照）："
    "目标根 C:\\Fluxgroup（单卷无 K: 用主数据盘）·36 任务 XML 字面量重定义面·MiniGame 真身移产线区+junction 单份律·"
    "Unity Bee 三处必清·物理依赖票内留痕（停本循环→detached executor 以实例退出为门·本轮末启动·窗限 09-29 12:00）·"
    "回执五件=下轮 S0 组装。指针=fleet/ack/O-20260926-2000-bm-a-inventory.md+results/_r267bma_fluxgroup_migration.ps1"
)
if not raw.endswith(b"\n"):
    open(cm_path, "ab").write(eol)
open(cm_path, "ab").write(cline.encode("utf-8") + eol)
print("CODELY.md line appended")
