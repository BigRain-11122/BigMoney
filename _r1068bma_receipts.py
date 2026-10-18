# -*- coding: utf-8 -*-
"""r1068 bm-a: append receipt lines into O-20261018-2144-bm-c.md and
O-20261018-2236-bm-c.md receipt sections (fresh-read-modify-write per r1006 law;
bm-b used the same append pattern on O-2144). Asserts both markers replaced."""
import io

R2144 = "fleet/orders/O-20261018-2144-bm-c.md"
R2236 = "fleet/orders/O-20261018-2236-bm-c.md"

M2144 = "- [ ] bm-a 回执："
NEW2144 = ("- [x] bm-a 回执：r1068 收令即办（23:0x）：①§1.1 三裁件=导演席 BigStream 域按双公司分工律"
           "（r1064 同件判例）零 BigMoney quant-loop 义务——导演席他窗在飞（V5.9 修复批 22:48 已落集团），"
           "§2.3 委员会 10:00 后径裁兜底已在 O-2236 令内；②§1.2 GPU 自领活=BigStream MV 烧批车道"
           "（i2v PACK-A 在飞面 20:28·quant 公司无 bm-a GPU 烧批车道）+本机 10min SLA 执法机制本窗已落"
           "（BmaIdleGuard 过渡守卫在役·首跳实弹验证 rc0·两跳判定+pause 让路+SatEngine 自动复活）；"
           "③§1.3 备货池补货=work-bank 机制候 kit 上链（kit 不在集团 origin·两探 23:0x tip e740d12 零命中·"
           "MSG-20261018-2310-bma-idleguard-kit-push 已发 @bm-c）·producer 侧收官预挂律执法面=守卫银行缺位"
           "自动曝光 PRODUCER 行。[via bm-a r1068]")

M2236 = "- [ ] bm-a："
NEW2236 = ("- [x] bm-a：r1068 收令即办（23:0x）：①§3.1 **过渡守卫已部署+任务在役**——Tools/bma_idleguard.pyw"
           "（按令 §2.1 规格：两跳判定 ≥600s 零误发/machine-state.flag=pause 让路窗零动作/GPU 忙判=util≥20%+"
           "非白名单烧批进程 ≥800MiB/SatEngine 死即自动复活〔register_satengine_task+tick 正典配方〕/银行缺位="
           "诚实曝光 PRODUCER 行·schema 零猜测）+BmaIdleGuard 计划任务注册（10min 节律·首火 23:15·Ready 实测·"
           "S4U XML flip 拒绝访问=carried C-20261016-04 提权窗待〔与 watchdog 同病〕——pythonw=GUI 子系统结构性"
           "零窗·默认 principal 下零弹窗保证仍成立）+首跳实弹验证 rc0（日志=GPU util 3% 闲面+satengine 0 活+"
           "hop1-idle-marked·日志=~/.codely-cli/sentinel/bma-idleguard.log）；②**canon kit 拉取 BLOCKED on "
           "upstream**：kit 不在集团 origin（idle-guard-kit/work-bank 零命中）→MSG-20261018-2310 已发 @bm-c 请推"
           "上链；kit 落地后 ≤1 轮 canon adopt（本地化三处已预研：PYW 路径=Tools/bma_idleguard.pyw/银行文件名="
           "bm-a-gpu-bank.json/SYS_PY=Python314 pythonw）；③§3.2 O-2144 §1 三件并窗裁定见该令回执节。"
           "[via bm-a r1068]")

with io.open(R2144, "r", encoding="utf-8") as f:
    t2144 = f.read()
assert M2144 in t2144, "O-2144 bm-a receipt marker missing"
t2144 = t2144.replace(M2144, NEW2144, 1)
with io.open(R2144, "w", encoding="utf-8") as f:
    f.write(t2144)

with io.open(R2236, "r", encoding="utf-8") as f:
    t2236 = f.read()
assert M2236 in t2236, "O-2236 bm-a receipt marker missing"
t2236 = t2236.replace(M2236, NEW2236, 1)
with io.open(R2236, "w", encoding="utf-8") as f:
    f.write(t2236)

# read-back verification
with io.open(R2144, "r", encoding="utf-8") as f:
    assert "[x] bm-a 回执：r1068" in f.read(), "O-2144 read-back failed"
with io.open(R2236, "r", encoding="utf-8") as f:
    assert "[x] bm-a：r1068" in f.read(), "O-2236 read-back failed"
print("RECEIPTS_OK 2144+2236")
