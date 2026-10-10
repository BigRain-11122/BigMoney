"""r866 bm-b PERPETUAL-N2-W20 slice-3 closeout appends:
 1. knowledge/TREASURE_REGISTRY.md one row (material-pool expansion + 2/2
    leverage replication readout, TREASURE_PROTECTION_LAW sec.1 finalize step)
 2. knowledge/METHODOLOGY_ASSETS.md new card E53 (band-gate self-face
    classification law -- own-wave draft-readout citations inside the
    scanned zone are the registration's own custody chain: SELF disclosed
    not blocking; foreign hits still REFUSE) + live-proof line.
Capture law O-20261002-2100 (finalize step: new method this batch? yes ->
append methodology card + targeted add).
Zero console CJK (r458 family). Byte-append only, no rewrites.
"""
import io

TREASURE = "knowledge/TREASURE_REGISTRY.md"
METH = "knowledge/METHODOLOGY_ASSETS.md"

t_row = (
    "2026-10-11 06:5x bm-b r866 研究域资产入库（PERPETUAL-N2-W20 finalize 类"
    "·TREASURE_PROTECTION_LAW §1）：results/alphagen_w20/ 注记入库——"
    "【反馈搜索杠杆 2/2 定谳复现波（V1=HOLDS 族 max |ICIR| 0.478 > pooled null "
    "族 p95 0.087·pooled 336≥300 充分线；RP2 杠杆复现 0.478≥census 0.353 → N2 "
    "反馈杠杆宣称升级可引用；RP1 带复现 FAILS 带外上方如实披露·跑后禁令零重调）"
    "+48 存活员入因子素材池（带 W20 波次血统标签·M1 正方向 0 员零新增候选"
    "·负向 |t|≥3 27 员=消费侧符号翻面设计面如实披露）+账本行 W20-2026-10-09.json"
    " 877,227→877,723】+METHODOLOGY_ASSETS 新卡 E53（band-gate self-face "
    "classification 卡：own-wave draft-readout citation in research/ docs = "
    "SELF disclosed-not-blocking·FOREIGN→REFUSE·机械分类律）\n"
)

m_card = (
    "\n- **E53 band-gate repo 文本扫 self-face 分类律（own-wave 只读读数引用="
    "登记自身 custody 链·披露非阻塞）**：proven：方法论卡。波级 seed band gate 的"
    " repo 文本扫腿（census r841 先例·scripts/+research/ 外撞零命）在起草探针只读"
    "读数被 5x 窗行/research 文档引用后出现自引用命中——本波读数链（起草窗只读 X →"
    " 冻结窗活重导 X 逐位一致）=登记自身 custody 面，非他机制宣称。机械分类律：命中"
    "行含「本波标记（W20 系）+derive/只读标记」=SELF→披露不阻塞；无该标记=FOREIGN"
    "→REFUSE 不变。禁 free-walk 让位（derive 位强制非自由挑·r682 律）与禁闸放宽"
    "（外撞仍硬拒）双守。live 实证：r866 bm-b W20 冻结窗 _r866bmb_w20_band_gate.py"
    " 首跑 REFUSE（hit=research/HANDOVER.md:739,500=r865 5x 行引用本波起草探针只读"
    "读数）→分类律落地后 ADMIT rc0（foreign=0·self=1 披露在案·回执 "
    "results/_r866bmb_w20_band_gate.txt）；X=739,500 与 r865 只读候选逐位一致。\n"
    "- 2026-10-11 06:5x：bm-b r866：W20 复现波 finalize 收口步（O-20261002-2100 "
    "捕获律）：本批有新方法 → append E53 band-gate self-face 分类律卡，live 实证"
    "（首跑 REFUSE→分类律→ADMIT·own-wave custody 链面）。\n"
)

with io.open(TREASURE, "a", encoding="utf-8", newline="\n") as f:
    f.write(t_row)
with io.open(METH, "a", encoding="utf-8", newline="\n") as f:
    f.write(m_card)

with io.open(TREASURE, encoding="utf-8") as f:
    tl = f.read().strip().splitlines()
with io.open(METH, encoding="utf-8") as f:
    ml = f.read().strip().splitlines()
print("treasure rows:", len(tl), "| tail ok:", "PERPETUAL-N2-W20" in tl[-1])
print("meth rows:", len(ml), "| tail ok:", "E53" in ml[-2] or "E53" in ml[-1])
