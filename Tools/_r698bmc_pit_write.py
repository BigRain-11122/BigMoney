"""r698 bm-c pit direct-write: two spawn-domain pits -> research/pit-spawn.md
(append, LF blob face) + receipt results/_r698bmc_pit_directwrite.json.
Pattern credit: Tools/_r697bmc_pit_write.py."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIT = os.path.join(ROOT, "research", "pit-spawn.md")

E1 = (
    "- [2026-10-07 19:1x r698 bm-c] **击杀裁决前墙钟实取律（自链误判重复轮 near-miss 实弹·零击杀零伤害）**："
    "长轮中途按「进程龄」判 spawn 代际时，age=(now-create_time) 的 now 若用会话臆测流逝时间（工具调用次数×臆测每步分钟）"
    "而非实取墙钟——本窗实弹：手术轮体感 40+min vs 实钟仅 11min，wscript→powershell→codely 自链 11.3min 龄被臆测 now 推算成"
    "「19:29 spawn 的重复轮」，距按 2026-09-20 击杀判例误杀自链一步之遥；终判仅靠探针内 datetime.now() 实取=19:16:19 一锤定音"
    "（自链起点 19:05:01=本会话 tick 实证）。正法=①一切 kill/代际裁决探针首行实取墙钟（Get-Date/datetime.now），禁用会话记忆推算 now；"
    "②父链+prompt 铁证之后必加「龄与已知 spawn 时刻互核」第三腿；③击杀判例三腿=父链铁证+prompt 内容+实取墙钟龄，缺一不动手。"
    "How to apply：未来任何「探测到重复轮/双头会话」裁决，先实取墙钟再算龄；龄与已知 spawn 时刻对不上即回零自检。\n")
E2 = (
    "- [2026-10-07 19:1x r698 bm-c] **长轮>12min 锁窗过期的下轮 tick 重叠 spawn 坑+锁龄续期技法（iteration_loop round.lock 12min 窗实测）**："
    "round.lock 锁窗=12min（age<12min tick 跳过·≥12min 新轮照 spawn）——手术轮/诊断轮实跑 15-40min 时，下个 tick 必在轮中 spawn "
    "第二个无头轮（同仓双执行体：双 state 写/双 round_no 进位/commit 竞速/轮报互撞 r646 族全风险面）；本窗 19:25 tick 时锁龄将 20min "
    "一步之遥，正法=轮中收口前显式续锁龄 `(Get-Item round.lock).LastWriteTime = Get-Date`（诚实信号=本轮仍活，非伪造他人锁——"
    "只续自己持有的锁）把重叠 tick 推过收口窗。护窗算术=touch 后 12min 内的 tick 必跳（19:17 touch→19:25 跳·19:35 时龄 18min 仍会 "
    "spawn）→ 收口必须赶在 touch+12min 前完成或二次 touch。How to apply：一切预估 >12min 的重轮（代码手术/深度诊断/多批验证）"
    "开工即把「锁龄检查点」写进 S7 清单；撞见活轮勿抢杀，先 touch 锁龄再收口。\n")


def main():
    before = open(PIT, "rb").read()
    added = (E1 + E2).encode("utf-8")
    with open(PIT, "ab") as fh:
        fh.write(added)
    after = open(PIT, "rb").read()
    assert after == before + added, "append must be byte-exact"
    receipt = {
        "round": 698, "machine": "bm-c",
        "target": "research/pit-spawn.md",
        "entries": 2,
        "bytes_appended": len(added),
        "md5_appended": hashlib.md5(added).hexdigest(),
        "zero_loss_assert": after == before + added,
        "e1_head": E1[:80], "e2_head": E2[:80],
    }
    out = os.path.join(ROOT, "results", "_r698bmc_pit_directwrite.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps(receipt, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
