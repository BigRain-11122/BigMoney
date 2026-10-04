# r670 bm-a: heartbeat + T-167 done + round-report addendum (verdict landed in-round)
import json, time
from datetime import datetime, timezone, timedelta
import os

CST = timezone(timedelta(hours=8))

# --- heartbeat refresh
H = "fleet/machines/bm-a.json"
hb = json.load(open(H, encoding="utf-8"))
hb["last_seen"] = datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["current_task"] = ("T-167 s3 COMPLETE: THEME-JUDGE-P1 judged_negative family-level "
                      "honest closure (r670 crash-fix + reburn 87s + finalize 10:26; "
                      "verdict+attrition+grammar-ledger+prereg sec.7/8 all landed)")
hb["verdict"] = ("green: theme T1 line first judged verdict OUT (negative, honest); "
                 "next = fund trio finalize watch 10-05 + next trial wave per standing line")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = datetime.now(CST).isoformat(timespec="seconds")
tmp = H + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
os.replace(tmp, H)
c = json.load(open(H, encoding="utf-8"))
assert isinstance(c["heartbeat_epoch_utc"], int) and "T" in c["clock_read"]
print("heartbeat refreshed:", c["clock_read"])

# --- T-167 -> done with result_ref
T = "fleet/tasks/T-2026-10-04-167-P1.json"
d = json.load(open(T, encoding="utf-8"))
d["status"] = "done"
d["result_ref"] = ("results/theme_judge_p1/theme_judge_p1_results.json "
                   "(judged_negative family-level honest closure; burn_state.json + "
                   "prereg sec.7/8 backfill + attrition row + grammar-ledger "
                   "consumption row; r670)")
tmp = T + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2)
os.replace(tmp, T)
c2 = json.load(open(T, encoding="utf-8"))
assert c2["status"] == "done" and "theme_judge_p1_results" in c2["result_ref"]
print("T-167 -> done, result_ref landed")

# --- round report addendum
addendum = (
    "2026-10-04 10:2x | r670 addendum | 本轮内烧批完成+finalize 判决落地（原计划下轮首动提前兑现）: "
    "重燃 10:19:01 → burn_state 87s/26 workers 全绿（38 空块重算+2 健康 chunk_00 断点复用·4×2000 null 家族逐层铺瓦 0..1999 恰一次自证）"
    " → finalize 首跑撞 st['sensitivity'] 路径笔误（行在 burn_state['cells']['sensitivity'] 下·从未行使路径·append_ledger 纯函数零半态=修复零双记风险）→ 修复后 finalize exit 0。"
    "**判决=judged_negative 族级诚实关线**: 主面 TJ-SOLO-x1 pooled Sharpe 0.2735 < 同 mask 随机点火 null μ 0.3734（skill_line 1.3172 未达·距线 −1.04 非擦线负）；"
    "g1/g2/DSR ×4 面全 fail；PBO 0.4286 observe 带；M1 t=1.19<3；LOO 795/796 稳（无单 ETF 驱动）；"
    "12/20 点火年 cohort 负边→撤回判定成立（最差 2016 −38.9%·最大样本年 2024 n=759 −10.55pp）；famous 幸存者溢价塌缩（rest 边 −4.64pp）=E25 预测缩水面实证；"
    "深破线 bl=0.75 变体族读数高于冻结面（+130.4%/+145.4% vs +83.4%）但判线不因变体重设（E24-ii）=改道候选须另立预注册。"
    "消费面全落: results JSON 733KB（evidence_cutoff 2026-09-22+cutoff_meta）+ attrition 行（judgment·8,004·总账 633,981）+ 语法台账消费行 + prereg §7/§8 回填（预测对账 (a)(b) 命中/(c) σ 漏带低/(e) censored 31.3% 漏带高·根因=截断翻活尾）+ T-167 票 done（result_ref 在票）。"
    "regime_segments 分段腿 run 内 AttributeError 如实记录 error 字段（判决不消费该面·补腿可选）。"
    "| verify: finalize exit 0 + nulls 4×2000 铺瓦自证 + attrition 台账 CLEAN 复扫 + 台账行/回填 needle 断言全过 "
    "| ceo-visibility: [当前活] 题材战法判决已出：**判负**——「破线出场+复活再入场」这套机器规则在 1,822 个算法点火的题材事件上，"
    "跑不赢「随便挑时点进场」的随机基准（0.27 vs 0.37），且 20 个点火年里 12 年是亏边的——诚实关线，不粉饰；方向不弃，改道候选（0.75 深破线）已留档须另立项 "
    "[最近实物] results/theme_judge_p1/theme_judge_p1_results.json + research/THEME_JUDGE_P1.md §7/§8（10:2x）"
    " [下个里程碑] fund 三族 V-NULLS 烧完 ETA 10-05 → judged finalize（预演 ALL-GREEN x3 就绪）；题材线改道批候选起草（≤10-06）；10-08 开市窗双跳\n"
)
with open("round_reports-bm-a.md", "ab") as fh:
    fh.write(addendum.encode("utf-8"))
raw = open("round_reports-bm-a.md", "rb").read()
raw.decode("utf-8")
assert b"r670 addendum" in raw[-3000:]
print("round report addendum landed")
